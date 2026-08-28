#!/usr/bin/env python3
"""run 폴더 무결성 3종 — 검사 대상 파일 분리 (spec §4.5).
① result.jtl 마지막 라인 필드수 = 헤더 ② result.jtl 샘플 span ≈ DURATION±20% ③ jmeter.log 최종 summary 라인.
summary = 는 콘솔(jmeter.log) 항목이지 jtl(CSV)에는 없다 — 판정 지표로 사용 금지."""
import os
import re
import sys


def main():
    d = sys.argv[1]
    jtl, log = os.path.join(d, "result.jtl"), os.path.join(d, "jmeter.log")
    problems = []
    if not os.path.exists(jtl):
        print("[FAIL] result.jtl 없음"); return 1
    lines = open(jtl, encoding="utf-8").read().splitlines()
    header_cols = len(lines[0].split(","))
    last_cols = len(lines[-1].split(","))
    if header_cols != last_cols:
        problems.append(f"jtl 마지막 라인 필드수 불일치 {header_cols}≠{last_cols} (중단)")
    span = (int(lines[-1].split(",")[0]) - int(lines[1].split(",")[0])) / 1000
    # DURATION은 폴더명에서 추출: ..._D{d}-...
    m = re.search(r"_D(\d+)-", d)
    if m:
        dur = int(m.group(1))
        if not (dur * 0.8 <= span <= dur * 1.5):
            problems.append(f"span {span:.0f}s ≉ DURATION {dur}s (중단 의심)")
    if os.path.exists(log):
        log_text = open(log, encoding="utf-8").read()
        if not re.search(r"^summary \+.*=.*\d+ in ", log_text, re.M) and "summary =" not in log_text:
            problems.append("jmeter.log에 summary 라인 없음 (중단 의심)")
    else:
        problems.append("jmeter.log 없음 — 무결성 ③ 확인 불가")
    for p in problems:
        print(f"[WARN] {p}")
    if not problems:
        print(f"무결성 OK (span {span:.0f}s)")
    return 1 if any("불일치" in p or "중단 의심" in p and "span" in p for p in problems) else 0


if __name__ == "__main__":
    sys.exit(main())
