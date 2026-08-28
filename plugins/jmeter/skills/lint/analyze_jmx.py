#!/usr/bin/env python3
"""JMX 정적 린트 — on_sample_error=stopthread × 엄격 어설션 조기사망 위험 탐지.

2026-08-28 실증 기반 규칙 (spec §4.1):
  B1. stopthread 그룹 내 응답코드 어설션이 단일값(예: 200)이고 ignore_status 미사용
      → 실데이터 404/5xx에서 해당 스레드 즉시 사망 (2-3 인트로 이미지 404 사례)
      BLOCKER는 리소스 부재 404가 정상응답인 선택적 리소스 엔드포인트(image/asset 등)에만
      적용 — 로그인/스키마 고정 API의 단일값 200은 실증상 무해하므로 RISK로 관찰 권고
  B2. stopthread 그룹 내 JSONPathAssertion이 경로 존재 강제(EXPECT_NULL=false + 기대값 공란)
      → 빈 응답에서 실패, 저빈도(0.2%)로 스레드 누적 소진 (3-2 검색 빈 결과 사례)
      배열 인덱스 경로($[0].x)는 BLOCKER — 빈 배열이 정상응답. 객체 필드($.x)는 RISK
  R1. 무한루프(loops=-1) — DURATION 제어 의존 확인 안내
  R2. __P() 파라미터 기본값 누락
  R3. 상대경로 에셋 참조 — worker CWD 의존 경고
"""
import json
import re
import sys
import xml.etree.ElementTree as ET

# 리소스 부재 시 404가 정상응답일 수 있는 엔드포인트 경로 힌트 (B1 BLOCKER 판정용)
OPTIONAL_RESOURCE_HINTS = ("image", "asset", "thumbnail", "avatar", "file", "download")


def _sampler_path(el, parents):
    """어설션 소속 HTTPSampler의 경로 — hashTree 상위로 올라가며 선행 형제 샘플러 탐색.

    JMX 구조상 어설션은 샘플러 바로 뒤의 중첩 hashTree 자식이므로
    어설션의 직속 부모에는 샘플러가 없다. 소유권 규칙: 가장 가까운 선행 샘플러.
    """
    node = el
    while node is not None:
        p = parents.get(node)
        if p is None:
            return ""
        siblings = list(p)
        for sib in reversed(siblings[:siblings.index(node)]):
            if sib.tag == "HTTPSamplerProxy":
                sp = sib.find(".//stringProp[@name='HTTPSampler.path']")
                return (sp.text or "") if sp is not None else ""
        node = p
    return ""


def analyze(path):
    findings = []
    root = ET.parse(path).getroot()

    has_stopthread = any(
        (p.find(".//stringProp[@name='ThreadGroup.on_sample_error']") is not None
         and p.find(".//stringProp[@name='ThreadGroup.on_sample_error']").text == "stopthread")
        for p in root.iter("ThreadGroup")
    )
    parents = {c: p for p in root.iter() for c in p}

    for ra in root.iter("ResponseAssertion"):
        if ra.get("enabled") == "false":
            continue
        field = ra.find(".//stringProp[@name='Assertion.test_field']")
        if field is None or field.text != "Assertion.response_code":
            continue
        values = [(s.text or "") for s in ra.findall(
            ".//collectionProp[@name='Asserion.test_strings']/stringProp")]
        assume = ra.find(".//boolProp[@name='Assertion.assume_success']")
        ignore_status = assume is not None and assume.text == "true"
        strict = len(values) == 1 and "|" not in values[0] and not ignore_status
        if strict and has_stopthread:
            optional_resource = any(
                h in _sampler_path(ra, parents).lower() for h in OPTIONAL_RESOURCE_HINTS)
            if optional_resource:
                findings.append({
                    "severity": "BLOCKER", "element": ra.get("testname", "?"),
                    "message": f"응답코드 어설션이 단일값 '{values[0]}' — stopthread 조합 시 404/5xx 응답에서 조기사망",
                    "template": "test_string을 '200|404'로, test_type을 matches(2)로, assume_success(Ignore Status)를 true로",
                })
            else:
                findings.append({
                    "severity": "RISK", "element": ra.get("testname", "?"),
                    "message": "단일값 응답코드 어설션 — 엔드포인트가 데이터 의존 404/5xx를 반환할 수 있는지 확인",
                    "template": "",
                })

    for ja in root.iter("JSONPathAssertion"):
        if ja.get("enabled") == "false":
            continue
        exp_null = ja.find(".//boolProp[@name='EXPECT_NULL']")
        expected = ja.find(".//stringProp[@name='EXPECTED_VALUE']")
        forces_existence = (exp_null is not None and exp_null.text == "false"
                            and expected is not None and not (expected.text or "").strip())
        if forces_existence and has_stopthread:
            jp = ja.find(".//stringProp[@name='JSON_PATH']")
            json_path = (jp.text or "") if jp is not None else ""
            array_indexed = re.search(r"\$\[\d+\]", json_path) is not None
            if array_indexed:
                findings.append({
                    "severity": "BLOCKER", "element": ja.get("testname", "?"),
                    "message": "배열 인덱스 JSONPath 경로 존재 강제 — 빈 응답(빈 배열)에서 실패, 저빈도로 스레드 누적 소진",
                    "template": "어설션 비활성(enabled=false) 또는 EXPECT_NULL=true — 추출기 기본값이 있으면 다운스트림 무영향",
                })
            else:
                findings.append({
                    "severity": "RISK", "element": ja.get("testname", "?"),
                    "message": "JSONPath 경로 존재 강제 — 응답 스키마에서 항상 존재하는 필드인지 확인",
                    "template": "",
                })

    for lc in root.iter():
        is_loop = (lc.tag == "LoopController"
                   or (lc.tag == "elementProp" and lc.get("elementType") == "LoopController"))
        if not is_loop:
            continue
        # GUI Infinite 저장은 intProp -1, 수동 편집본은 stringProp "-1" — 둘 다 감지
        loops = lc.find(".//stringProp[@name='LoopController.loops']")
        if loops is None:
            loops = lc.find(".//intProp[@name='LoopController.loops']")
        if loops is not None and loops.text == "-1":
            findings.append({
                "severity": "RISK", "element": lc.get("testname") or "LoopController",
                "message": "무한루프 — DURATION으로만 종료됨. run/knee의 duration 인자가 항상 전달되는지 확인",
                "template": "",
            })

    text = open(path, encoding="utf-8").read()
    for m in re.finditer(r"\$\{__P\(([^),}]+)\)\}", text):
        findings.append({
            "severity": "RISK", "element": m.group(1),
            "message": "__P 파라미터에 기본값 없음 — 인자 미전달 시 JMeter 실행 오류",
            "template": f"__P({m.group(1)},<기본값>)",
        })

    for sp in root.iter("stringProp"):
        if sp.get("name") == "HTTPSampler.path" and sp.text and "assets/" in sp.text and not sp.text.startswith("http"):
            findings.append({
                "severity": "RISK", "element": sp.text,
                "message": "상대경로 에셋 참조 — worker CWD에 의존. jmeter-server는 반드시 저장소 루트에서 기동해야 함",
                "template": "",
            })
    return findings


def main():
    if len(sys.argv) < 2:
        print("usage: analyze_jmx.py <file.jmx> [--json]", file=sys.stderr)
        return 2
    as_json = "--json" in sys.argv
    path = sys.argv[1]
    try:
        findings = analyze(path)
    except ET.ParseError as e:
        print(f"[ERROR] XML 파싱 실패: {e}", file=sys.stderr)
        return 2
    if as_json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        for f in findings:
            line = f"[{f['severity']}] {f['element']} — {f['message']}"
            if f["template"]:
                line += f" | 수정: {f['template']}"
            print(line)
    return 1 if any(f["severity"] == "BLOCKER" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
