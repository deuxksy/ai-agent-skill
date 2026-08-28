# jmeter 플러그인 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** zzizily 마켓플레이스 11번째 도메인 `jmeter` 플러그인(스킬 6종: lint·deploy·run·knee·collect·report)을 구현하고 v1.16.0 통합 버전으로 등록한다.

**Architecture:** 각 스킬은 `plugins/jmeter/skills/<name>/SKILL.md`(절차형 지시)이며, lint만 부가로 정적 분석 스크립트 `analyze_jmx.py`를 동봉해 실행 가능한 검증을 제공한다. 모든 스킬은 공통 설정 `jmeter.json` 스키마와 결과 폴더 명명규칙을 공유한다.

**Tech Stack:** Claude Code plugin(마켓플레이스 매니페스트 JSON), Python 3 표준라이브러리(ElementTree, 검증 스크립트), Bash(원격 ssh/rsync 절차)

**Spec:** `docs/superpowers/specs/2026-08-28-jmeter-plugin-design.md` (본 계획은 spec §4의 상세와 함께 읽는다 — 스킬별 세부 절차·판정룰·스키마는 spec에 확정본이 있다)

## Global Constraints

- 저장소: `~/git/ai-agent-skill` (main 브랜치, 커밋 규약: Conventional Commits, 말머리 영어·본문 한국어)
- 버전: 공개 플러그인 전부 **1.15.0 → 1.16.0** 동기화. `meridian`은 독립 버전(0.1.0) 유지 — 건드리지 않는다
- SKILL.md frontmatter: `name`, `description`(한국어, 트리거 중심 — 기존 스킬 양식 준수)
- 모든 원격 cd는 **절대경로** (`~` 금지 — zsh/PowerShell 확격 깨짐). pgrep은 **bracket 패턴**
- 스킬 마크다운 내 bash 블록은 `bash -n`으로 문법 검증한다
- 결과 폴더 명명: `results/{시나리오}_{하이픈→언더스코어}-T{t}x{n}_R{r}_D{d}-{yymmdd}-{hhmmss}/` (부하원 타임존 기준)
- jmeter.json에 평문 credential 금지 — `*_ref`(환경변수/ssh-config) 참조만

---

### Task 1: 플러그인 스캐폴드 + v1.16.0 전체 동기화 + 마켓플레이스 등록

**Files:**
- Create: `plugins/jmeter/.claude-plugin/plugin.json`
- Create: `plugins/jmeter/skills/` (빈 디렉토리 — 이후 태스크가 채움)
- Modify: `.claude-plugin/marketplace.json` (jmeter 엔트리 추가 + 전체 1.16.0)
- Modify: `plugins/{security,infra,trackers,sessions,l10n,git,rules,docs,review,dev}/.claude-plugin/plugin.json` (version만)
- Modify: `README.md`, `CLAUDE.md`

**Interfaces:**
- Produces: `plugins/jmeter/` 경로와 `plugin.json`(name "jmeter", version "1.16.0", skills "./skills/") — 이후 모든 태스크가 이 디렉토리에 파일을 추가한다

- [ ] **Step 1: plugin.json 생성**

`plugins/jmeter/.claude-plugin/plugin.json`:

```json
{
  "name": "jmeter",
  "description": "JMeter 스트레스 테스트 파이프라인: JMX 정적 린트, 원격 서버 설치·배포·기동, 부하 실행·집계, knee/MAX TPS 탐색, 결과 수집·무결성 검증, 보고서·차트 생성",
  "version": "1.16.0",
  "author": {
    "name": "Crong"
  },
  "skills": "./skills/"
}
```

- [ ] **Step 2: 공개 플러그인 10종 버전 동기화**

```bash
cd ~/git/ai-agent-skill
for f in plugins/*/.claude-plugin/plugin.json; do
  case "$f" in *meridian*) continue;; esac
  python3 - "$f" <<'EOF'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d["version"] = "1.16.0"
json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
open(p, "a").write("\n")
EOF
done
```

- [ ] **Step 3: marketplace.json에 jmeter 등록 + 전체 버전 갱신**

`.claude-plugin/marketplace.json`의 `plugins` 배열 끝에 추가 (다른 엔트리와 동일 형식):

```json
{
  "name": "jmeter",
  "source": "./plugins/jmeter",
  "description": "JMeter 스트레스 테스트 파이프라인: JMX 린트, 원격 설치·배포·기동, 실행·집계, knee 탐색, 수집·검증, 리포트",
  "version": "1.16.0"
}
```

기존 엔트리의 `"version": "1.15.0"`은 전부 `"1.16.0"`으로 치환 (sed 또는 python 일괄 처리).

- [ ] **Step 4: README.md 갱신**

`grep -n '10개' README.md`로 나온 위치(개요 문장, 카탈로그 표, 설치 가이드) 전부 10→11 갱신 + `claude plugin install jmeter@zzizily` 행 추가 + Diátaxis How-To 표에 jmeter 행 추가:

```markdown
| | [jmeter](./plugins/jmeter/README.md) | JMeter 스트레스 테스트: JMX 린트, 원격 배포·기동, 실행·knee 탐색, 수집·리포트 |
```

- [ ] **Step 5: CLAUDE.md 갱신**

- 분류 원칙에 8번 추가: `8. **부하 테스트/JMeter 실행** → `jmeter``
- 카탈로그 표에 행 추가: `` | `jmeter` | 1.16.0 | `lint`, `deploy`, `run`, `knee`, `collect`, `report` | `jmeter@zzizily` | ``

- [ ] **Step 6: 검증**

```bash
# (a) meridian 제외 전 플러그인이 1.16.0 — 출력 없어야 통과
grep -L '"version": "1.16.0"' plugins/*/.claude-plugin/plugin.json | grep -v meridian
# (b) meridian은 0.1.0 유지
grep '"version"' plugins/meridian/.claude-plugin/plugin.json
# (c) marketplace JSON 유효 + jmeter 등록 + 엔트리 11개
python3 -c "import json; m=json.load(open('.claude-plugin/marketplace.json')); ps=[p['name'] for p in m['plugins']]; assert 'jmeter' in ps and len(ps)==11, ps; print('OK', len(ps))"
# (d) plugin.json 2종 유효
python3 -c "import json; json.load(open('plugins/jmeter/.claude-plugin/plugin.json')); print('OK')"
```

Expected: (a) 출력 없음, (b) 0.1.0, (c) `OK 11`, (d) `OK`

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "feat(jmeter): 플러그인 스캐폴드 및 v1.16.0 전체 동기화, 마켓플레이스 등록"
```

---

### Task 2: `jmeter:lint` — JMX 정적 분석 스킬 (스크립트 TDD 포함)

**Files:**
- Create: `plugins/jmeter/skills/lint/SKILL.md`
- Create: `plugins/jmeter/skills/lint/analyze_jmx.py`
- Create: `plugins/jmeter/skills/lint/fixtures/2-3-pre.jmx` (ecoai-gwageo HEAD에서 추출)
- Create: `plugins/jmeter/skills/lint/fixtures/3-2-pre.jmx`

**Interfaces:**
- Consumes: 없음 (독립)
- Produces: `analyze_jmx.py` — CLI: `python3 analyze_jmx.py <file.jmx> [--json]`, 종료코드 0(위험 0)/1(blocker 있음)/2(파싱 오류). 출력 라인 형식 `[BLOCKER|RISK|INFO] <testname> — <내용>` , `--json`은 `[{severity, element, message, template}]`

- [ ] **Step 1: 픽스처 추출 (수정 전 원본 — 실증 사례)**

```bash
cd ~/git/ai-agent-skill && mkdir -p plugins/jmeter/skills/lint/fixtures
git -C ~/git/kyolim/ecoai-gwageo show HEAD:src/jmeter/2-3.jmx > plugins/jmeter/skills/lint/fixtures/2-3-pre.jmx
git -C ~/git/kyolim/ecoai-gwageo show HEAD:src/jmeter/3-2.jmx > plugins/jmeter/skills/lint/fixtures/3-2-pre.jmx
python3 -c "import xml.etree.ElementTree as ET; ET.parse('plugins/jmeter/skills/lint/fixtures/2-3-pre.jmx'); ET.parse('plugins/jmeter/skills/lint/fixtures/3-2-pre.jmx'); print('fixtures OK')"
```

주의: ecoai-gwageo 작업복사본의 2-3/3-2는 이미 수정돼 있으므로 반드시 `git show HEAD:`로 **커밋 시점 원본**을 꺼낸다.

- [ ] **Step 2: analyze_jmx.py 작성**

```python
#!/usr/bin/env python3
"""JMX 정적 린트 — on_sample_error=stopthread × 엄격 어설션 조기사망 위험 탐지.

2026-08-28 실증 기반 규칙 (spec §4.1):
  B1. stopthread 그룹 내 응답코드 어설션이 단일값(예: 200)이고 ignore_status 미사용
      → 실데이터 404/5xx에서 해당 스레드 즉시 사망 (2-3 인트로 이미지 404 사례)
  B2. stopthread 그룹 내 JSONPathAssertion이 경로 존재 강제(EXPECT_NULL=false + 기대값 공란)
      → 빈 응답에서 실패, 저빈도(0.2%)로 스레드 누적 소진 (3-2 검색 빈 결과 사례)
  R1. 무한루프(loops=-1) — DURATION 제어 의존 확인 안내
  R2. __P() 파라미터 기본값 누락
  R3. 상대경로 에셋 참조 — worker CWD 의존 경고
"""
import json
import re
import sys
import xml.etree.ElementTree as ET


def analyze(path):
    findings = []
    root = ET.parse(path).getroot()

    has_stopthread = any(
        (p.find(".//stringProp[@name='ThreadGroup.on_sample_error']") is not None
         and p.find(".//stringProp[@name='ThreadGroup.on_sample_error']").text == "stopthread")
        for p in root.iter("ThreadGroup")
    )

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
            findings.append({
                "severity": "BLOCKER", "element": ra.get("testname", "?"),
                "message": f"응답코드 어설션이 단일값 '{values[0]}' — stopthread 조합 시 404/5xx 응답에서 조기사망",
                "template": "test_string을 '200|404'로, test_type을 matches(2)로, assume_success(Ignore Status)를 true로",
            })

    for ja in root.iter("JSONPathAssertion"):
        if ja.get("enabled") == "false":
            continue
        exp_null = ja.find(".//boolProp[@name='EXPECT_NULL']")
        expected = ja.find(".//stringProp[@name='EXPECTED_VALUE']")
        forces_existence = (exp_null is not None and exp_null.text == "false"
                            and expected is not None and not (expected.text or "").strip())
        if forces_existence and has_stopthread:
            findings.append({
                "severity": "BLOCKER", "element": ja.get("testname", "?"),
                "message": "JSONPath 경로 존재 강제 — 빈 응답(빈 배열)에서 실패, 저빈도로 스레드 누적 소진",
                "template": "어설션 비활성(enabled=false) 또는 EXPECT_NULL=true — 추출기 기본값이 있으면 다운스트림 무영향",
            })

    for lc in root.iter("LoopController"):
        loops = lc.find(".//stringProp[@name='LoopController.loops']")
        if loops is not None and loops.text == "-1":
            findings.append({
                "severity": "RISK", "element": lc.get("testname", "LoopController"),
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
```

- [ ] **Step 3: 픽스처에 대한 실패 테스트 실행 (도그푸드 — spec §6 통과 기준)**

```bash
cd ~/git/ai-agent-skill/plugins/jmeter/skills/lint
python3 analyze_jmx.py fixtures/2-3-pre.jmx; echo "exit=$?"
python3 analyze_jmx.py fixtures/3-2-pre.jmx; echo "exit=$?"
```

Expected: 2-3에서 `인트로 이미지 HTTP 200` BLOCKER 1건(exit=1), 3-2에서 `JSON Path Assertion - $[0].addressName` BLOCKER 1건(exit=1). 어느 쪽도 BLOCKER가 나오지 않으면 규칙 구현이 틀린 것 — 수정 후 재실행.

- [ ] **Step 4: 통과 확인 — 오늘 수정본(양성 케이스)은 위험 없어야**

```bash
cd ~/git/kyolim/ecoai-gwageo
python3 ~/git/ai-agent-skill/plugins/jmeter/skills/lint/analyze_jmx.py src/jmeter/2-3.jmx; echo "exit=$?"
python3 ~/git/ai-agent-skill/plugins/jmeter/skills/lint/analyze_jmx.py src/jmeter/3-2.jmx; echo "exit=$?"
```

Expected: 두 파일 모두 응답코드/JSONPath BLOCKER 없음(exit=0, 무한루프 RISK는 허용)

- [ ] **Step 5: SKILL.md 작성**

`plugins/jmeter/skills/lint/SKILL.md`:

```markdown
---
name: lint
description: "JMX 정적 린트. 실행 전 JMeter 시나리오 파일의 조기사망 위험(stopthread+엄격 어설션), 무한루프, 파라미터 기본값 누락, 상대경로 에셋을 검사. 'jmx 점검', 'lint', '부하 전 검사' 등에서 사용. 프로젝트 루트에 src/jmeter/*.jmx가 있을 때 동작."
---

# JMX Lint

JMeter 시나리오 실행 전 정적 검사. 실행은 하지 않는다 — smoke(고빈도, 런타임)와 상호보완적으로 **저빈도 조기사망 함정**을 파일만 보고 찾는다.

## 실행

```bash
# 단일 파일
python3 "$(dirname "$0")/analyze_jmx.py" src/jmeter/<시나리오>.jmx

# 프로젝트 전체
for f in src/jmeter/*.jmx; do
  echo "== $f"; python3 .../analyze_jmx.py "$f" || true
done
```

(`...`는 이 스킬 디렉토리 경로 — fixtures/analyze_jmx.py가 같은 디렉토리에 있다)

## 판정

- BLOCKER: stopthread 그룹의 엄격 어셔설션 — 실행 전 수정 권고(수정 템플릿이 출력에 포함)
- RISK: 무한루프/기본값 누락/상대경로 — 확인 후 진행

## 근거 사례

- 2-3: 인트로 이미지 404(활성 이미지 부재)가 매 iteration 실패 → 전 스레드 1회 만에 종료 (56s)
- 3-2: 검색 빈 결과 0.2% 빈도로 JSONPath 실패 → 스레드 17→3 누적 소진. 짧은 smoke로는 탐지 불가
```

(frontmatter의 description은 위 텍스트를 한 줄로 이어 쓴다)

- [ ] **Step 6: Commit**

```bash
cd ~/git/ai-agent-skill && git add plugins/jmeter/skills/lint && git commit -m "feat(jmeter): lint 스킬 — JMX 정적 분석기와 실증 픽스처"
```

---

### Task 3: `jmeter:deploy` — 설치·배포·기동 스킬

**Files:**
- Create: `plugins/jmeter/skills/deploy/SKILL.md`

**Interfaces:**
- Consumes: `jmeter.json` 스키마 (spec §3 — master, workers[{host,ip}], remote_path, ssh{user,port,key_ref}, remote_os:"linux")
- Produces: 원격 노드 전원에서 `jmeter --version` 성공 + 자산 동기화됨 + jmeter-server가 **절대경로 remote_path에서 기동** 상태 (run/knee가 이를 전제)

- [ ] **Step 1: SKILL.md 작성**

`plugins/jmeter/skills/deploy/SKILL.md` — 필수 포함 내용(명령 블록은 아래 검증본 그대로):

```markdown
---
name: deploy
description: "JMeter 부하원 원격 설치·배포·기동. 미설치 서버에 JDK17+JMeter 5.6.3을 idempotent하게 설치하고(tarball→/usr/local/bin 심링크), 프로젝트 자산을 rsync(mac/linux)·robocopy(Windows)로 증분 배포한 뒤 jmeter-server를 저장소 루트 CWD로 기동·검증. '부하원 배포', 'jmeter 서버 세팅', 'deploy'에서 사용."
---

# Deploy — 설치·배포·기동

전제: `jmeter.json`(프로젝트 루트, 스키마는 spec §3). 원격은 Linux(remote_os)만 지원 — 로컬 OS만 분기.

## 1. Idempotent 설치 (노드마다)

```bash
ssh <host> 'jmeter --version >/dev/null 2>&1 && java -version 2>&1 | head -1 || echo NEED_INSTALL'
# NEED_INSTALL 시:
ssh <host> 'cd /tmp && curl -sLO https://dlcdn.apache.org/jmeter/binaries/apache-jmeter-5.6.3.tgz \
  && sudo tar -xzf apache-jmeter-5.6.3.tgz -C /opt/ \
  && sudo ln -sf /opt/apache-jmeter-5.6.3/bin/jmeter /usr/local/bin/jmeter \
  && sudo ln -sf /opt/apache-jmeter-5.6.3/bin/jmeter-server /usr/local/bin/jmeter-server \
  && jmeter --version'   # JDK는 OS 패키지 관리자(apt/dnf)로 openjdk-17 설치
# 재실행 시 이미 있으면 no-op — 버전 불일치 시 경고 후 중단(자동 교체 금지)
```

## 2. 자산 동기화 (로컬 OS 분기)

```bash
# mac/Linux — 절대경로 exclude, 증분
rsync -az --exclude=.git --exclude=results --exclude=.mcp.json --exclude='.omc*' \
  ./ <host>:<remote_path>/
# Windows (PowerShell) — robocopy 증분 (/MIR 금지). SMB 미탑재면 scp -r fallback:
# robocopy . \\<host-ip>\<share>\<path> /E /XD .git results
```

## 3. jmeter-server 기동·검증 (양 노드)

```bash
for h in <worker1-host:ip> <worker2-host:ip>; do
  host=${h%%:*}; ip=${h##*:}
  ssh "$host" "pgrep -f 'ApacheJMeter.jar.*server_port' >/dev/null || (cd <remote_path 절대경로> && nohup jmeter-server -Djava.rmi.server.hostname=$ip > /tmp/jmeter-server.log 2>&1 < /dev/null &)"
done
# 검증 — bracket 패턴(자기 자신 cmdline self-match 방지) + /proc cwd
for host in <hosts>; do
  ssh "$host" 'p=$(pgrep -f "[j]ava.*ApacheJMeter" | head -1); echo "'$host': $(readlink /proc/$p/cwd)"'
done
```

## 내장 gotcha (위반 시 5-3 업로드 FileNotFoundException 회귀)

1. Windows ssh 비대화형 명령은 **원격 홈 디렉토리에서 시작** — cd는 항상 절대경로
2. zsh 쌍따옴표 안 `~/`는 로컬로 확장되어 원격 cd 실패 — 절대경로만
3. pgrep 패턴은 ssh bash -c 자기 cmdline에 self-match — `[j]ava` bracket 필수
```

- [ ] **Step 2: SKILL.md 내 bash 블록 문법 검증**

```bash
cd ~/git/ai-agent-skill/plugins/jmeter/skills/deploy
python3 - <<'EOF'
import re, subprocess, tempfile, os
md = open("SKILL.md", encoding="utf-8").read()
blocks = re.findall(r"```bash\n(.*?)```", md, re.S)
assert blocks, "bash 블록 없음"
for i, b in enumerate(blocks):
    # <placeholder> 포함 블록은 치환 후 검증
    t = b.replace("<host>", "h1").replace("<worker1-host:ip>", "a:1").replace("<worker2-host:ip>", "b:2").replace("<remote_path>", "/p").replace("<remote_path 절대경로>", "/p").replace("<hosts>", "h1 h2").replace("<share>", "s").replace("<path>", "p").replace("<host-ip>", "1.2.3.4")
    # PowerShell 라인(# 시작)은 건너뜀
    lines = [l for l in t.splitlines() if not l.strip().startswith("#") and "robocopy" not in l]
    with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as f:
        f.write("\n".join(lines)); p = f.name
    r = subprocess.run(["bash", "-n", p], capture_output=True, text=True)
    os.unlink(p)
    assert r.returncode == 0, f"block {i} syntax error: {r.stderr}"
print(f"bash blocks OK: {len(blocks)}")
EOF
```

Expected: `bash blocks OK: N` (N≥3)

- [ ] **Step 3: Commit**

```bash
cd ~/git/ai-agent-skill && git add plugins/jmeter/skills/deploy && git commit -m "feat(jmeter): deploy 스킬 — idempotent 설치·rsync/robocopy·jmeter-server 기동 검증"
```

---

### Task 4: `jmeter:run` — 1회 실행 스킬

**Files:**
- Create: `plugins/jmeter/skills/run/SKILL.md`
- Create: `plugins/jmeter/skills/run/aggregate.py` (풀가동 집계 — 검증된 스크립트)

**Interfaces:**
- Consumes: deploy가 보장한 기동 상태, `jmeter.json`
- Produces: `results/<시나리오>-T{t}x{n}_R{r}_D{d}-{ts}/` (result.jtl, jmeter.log, run.md) + `results/summary.md` 1행 + `aggregate.py` CLI: `python3 aggregate.py <jtl> <ramp_초>` → stdout 마지막 라인 `풀가동 {span}s: {n} req = {tps} req/s | Err {p}% | p95 {ms}ms | stdev {ms}ms`. **knee는 이 CLI를 재사용한다**

- [ ] **Step 1: aggregate.py 작성 (오늘 실전 검증본)**

```python
#!/usr/bin/env python3
"""풀가동 구간 집계 — 램프 제외, Transaction parent(라벨에 '→' 포함) 제외, HTTP 요청 기준."""
import csv
import statistics
import sys


def main():
    path, ramp = sys.argv[1], int(sys.argv[2]) * 1000
    d = list(csv.reader(open(path, encoding="utf-8")))[1:]
    t0 = int(d[0][0])
    full = [r for r in d if int(r[0]) >= t0 + ramp and "→" not in r[2]]
    if not full:
        print("풀가동 구간 샘플 없음", file=sys.stderr)
        return 2
    span = (int(full[-1][0]) - int(full[0][0])) / 1000
    el = sorted(int(r[1]) for r in full)
    err = sum(1 for r in full if r[7] == "false")
    sd = statistics.stdev(el) if len(el) > 1 else 0.0
    print(f"풀가동 {span:.0f}s: {len(full)} req = {len(full)/span:.1f} req/s | "
          f"Err {100*err/len(full):.2f}% | p95 {el[int(len(el)*.95)]}ms | stdev {sd:.1f}ms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: SKILL.md 작성**

`plugins/jmeter/skills/run/SKILL.md` — 필수 섹션:

```markdown
---
name: run
description: "JMeter 시나리오 1회 실행. jmx + 총 VU + ramp + duration(+ mode x2분산/x1단독)을 받아 T를 계산해 분산 실행하고, 풀가동 집계(TPS/p95/stdev/Err)와 run.md, summary.md 누적까지 자동 생성. '부하 실행', 'jmeter 돌려', '--smoke' 사전검증에서 사용."
---

# Run — 1회 실행

## 인자

- `jmx`(필수), `vu` 총 VU(필수), `ramp`(초, 기본 60), `duration`(초, 기본 180)
- `mode`: `x2`(기본, 분산) / `x1`(단독)
- 옵션: `--smoke` (T1~2·D5~10 사전 실행), `--verify-db` (jmeter.json verify_db로 jtl↔DB 정합)

## T 계산·명명

x2: `T=vu/2` — vu가 홀수면 오류 안내 후 x1 유도. x1: `T=vu`.
폴더: `results/{시나리오명의 하이픈→언더스코어}-T{T}x{n}_R{ramp}_D{d}-$(date +%y%m%d-%H%M%S)` (부하원 타임존)

## 실행 (master에서)

```bash
ssh <master> 'cd <remote_path 절대경로> && OUT=results/<OUT> && mkdir -p "$OUT" \
  && jmeter -n -t src/jmeter/<jmx>.jmx -R "<worker_ips 쉼표결합>" \
     -GTHREADS=$T -GRAMP_TIME=$RAMP -GDURATION=$DUR -l "$OUT/result.jtl" > "$OUT/jmeter.log" 2>&1'
# x1이면 -R/-G 대신 -J 사용, 단독 노드 실행
```

## 실행 후 자동 (3종 — 순서대로)

1. 집계: `python3 aggregate.py <수집된 jtl> <ramp>` (원격에서 직접 실행 가능)
2. run.md 생성: 실행 일시(KST), 명령 전체, 형상(master/workers, JMeter 버전), 프로파일(VU/R/D), 집계 결과, 특이사항
3. summary.md 1행 누적: `| 시나리오 | 단계 | 회차 | T(x{n}) | R | D | 폴더 | 샘플수 | TPS | p95 | stdev | Err% | 특이 |`

## --smoke 통과 기준

Err 0 + worker 분포 균형(편차 <10%) + jmeter.json smoke.expect 라벨·상태코드 충족 (미선언 시 범용 기준만)

## 내장 주의

- 콘솔 `summary =` 는 분산 display 오탐 — 판정은 항상 jtl
- 베이스라인은 T1x2 R0 D60 권장
```

- [ ] **Step 3: bash 블록 문법 검증** (Task 3 Step 2의 검증 스크립트 재사용, 치환 변수에 `$T/$RAMP/$DUR/$OUT/<jmx>/<master>/<worker_ips>` 추가)

- [ ] **Step 4: aggregate.py 동작 검증 (실측 데이터)**

```bash
cd ~/git/ai-agent-skill/plugins/jmeter/skills/run
python3 aggregate.py ~/git/kyolim/ecoai-gwageo/results/2_1-T5x2_R60_D180-260828-083409/result.jtl 60
```

Expected: `풀가동 120s: 78532 req = 653.5 req/s | Err 0.00% | p95 35ms | stdev 9.5ms` (오늘 실측값과 일치)

- [ ] **Step 5: Commit**

```bash
git add plugins/jmeter/skills/run && git commit -m "feat(jmeter): run 스킬 — 분산 실행·풀가동 집계·run.md/summary 누적"
```

---

### Task 5: `jmeter:knee` — 점진 VU 탐색 스킬

**Files:**
- Create: `plugins/jmeter/skills/knee/SKILL.md`

**Interfaces:**
- Consumes: run의 실행·집계 primitive(aggregate.py CLI를 재사용 — 경로는 `../run/aggregate.py`), deploy가 보장한 기동 상태
- Produces: 래더 전체 실행 결과들 + knee·MAX TPS 판정 요약 (report가 summary.md로 소비)

- [ ] **Step 1: SKILL.md 작성** — 필수 섹션:

```markdown
---
name: knee
description: "점진적 VU 상승 래더로 시나리오별 knee(포화 변곡점)와 MAX TPS를 탐색. 판정룰(이상/평탄/진행 우선순위 테이블)과 런 간 드레인 게이트를 내장해 자동 종료. 'knee 찾기', 'MAX TPS', '래더 테스트'에서 사용."
---

# Knee — 점진 VU 탐색

## 인자

`jmx`, `vu_start`(기본 2), `step_policy`(기본 geo2: 2,4,8,16,… / `list:10,30,50` 형식), `ramp`(60), `duration`(180)

## 사이클 (포인트마다 — run 스킬의 실행·집계를 재사용)

1. 현재 VU로 run 실행 + `../run/aggregate.py` 집계
2. 아래 판정표로 단일 판정 (첫 매칭 채택)

| 우선순위 | 판정 | 조건 (직전 대비) | 동작 |
| :-: | :-- | :-- | :-- |
| 1 | 이상 종료 | Err ≥ 5% 또는 절대 p95 ≥ 1s | 즉시 종료 |
| 2 | 이상 종료 | TPS 하락(>5%) + p95 ≥ 직전 2배 | 종료 — 직전 피크가 MAX TPS |
| 3 | 이상 재시 | Err 1~5% (1회만) | 동일 VU 재실행, 재발 시 종료 |
| 4 | 평탄 | TPS -5% ~ +5% | 확인 2포인트 추가 후 종료 (잔여 스텝 생략) |
| 5 | 진행 | TPS +5% 초과 + Err < 1% + p95 < 1s | 다음 스텝 |

상승 구간(5)에서는 p95 배수 미적용. 첫 포인트(직전 없음)는 무조건 진행.

## 런 간 드레인 게이트 (다음 포인트 전)

최소 120s 대기 + 잔여 확인 — `sum(rate(nginx_ingress_controller_requests[1m])) < 1`, `hikaricp_connections_pending == 0` (인스턴트), 4-x 계열 후 `vllm:num_requests_waiting == 0`. 미통과 시 30s 간격 재확인(최대 10회 후 경고하고 진행). 쿼리 창구는 jmeter.json metrics.

## 산출

VU-TPS 곡선 표 + knee(VU)·MAX TPS(req/s) 판정 + 각 포인트 summary.md 누적(run이 처리)
```

- [ ] **Step 2: 판정표 셀 숫자가 spec §4.4와 동일한지 grep 검증**

```bash
grep -c 'Err ≥ 5%\|±\|2배' plugins/jmeter/skills/knee/SKILL.md   # ≥ 3
grep -q 'p95 ≥ 1s' plugins/jmeter/skills/knee/SKILL.md && grep -q '확인 2포인트' plugins/jmeter/skills/knee/SKILL.md && echo 판정표 OK
```

- [ ] **Step 3: bash 블록 문법 검증** (Task 3 Step 2 스크립트 재사용)

- [ ] **Step 4: Commit**

```bash
git add plugins/jmeter/skills/knee && git commit -m "feat(jmeter): knee 스킬 — 판정표 기반 점진 VU 탐색·드레인 게이트"
```

---

### Task 6: `jmeter:collect` — 결과 수집·무결성 스킬

**Files:**
- Create: `plugins/jmeter/skills/collect/SKILL.md`
- Create: `plugins/jmeter/skills/collect/check_integrity.py`

**Interfaces:**
- Consumes: run/knee가 만든 원격 `results/`
- Produces: 로컬 `results/` 동기화본 + 무결성 판정 + (선택) 각 run의 `report/` HTML. `check_integrity.py` CLI: `python3 check_integrity.py <run_dir>` → 라인 출력 + 종료코드 0(양호)/1(중단 의심)

- [ ] **Step 1: check_integrity.py 작성**

```python
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
```

- [ ] **Step 2: 실측 데이터로 검증 (양성·중단 케이스)**

```bash
cd ~/git/ai-agent-skill/plugins/jmeter/skills/collect
# 양성: 오늘 정상 완주 run
python3 check_integrity.py ~/git/kyolim/ecoai-gwageo/results/5_3-T1x2_R0_D60-260828-110204; echo exit=$?
# 중단 케이스: 2-3 첫 실행(56s 조기종료, D180 폴더)
python3 check_integrity.py ~/git/kyolim/ecoai-gwageo/results/2_3-T15x2_R60_D180-260828-091919; echo exit=$?
```

Expected: 양성 exit=0 + `무결성 OK`, 중단 케이스 exit=1 + span 경고. (양성 run에 jmeter.log가 로컬에 없으면 master에서 rsync 후 재검증 — 로컬 results에 이미 수집돼 있음)

- [ ] **Step 3: SKILL.md 작성** — 필수 섹션: 수집(`rsync -az <master>:<remote_path>/results/ ./results/` 증분, Windows는 reverse robocopy), 무결성 3종(스크립트 호출), HTML 리포트(`cd results/<OUT> && jmeter -g result.jtl -o report` — 로컬 생성 규칙, 폴더 비어야 함/치우고 재생성), `--evidence`(원격 로그 수집 보존 — Kakao 500 사례: `kubectl logs --since` + 파일로 저장)

- [ ] **Step 4: bash 블록 문법 검증 + Commit**

```bash
git add plugins/jmeter/skills/collect && git commit -m "feat(jmeter): collect 스킬 — 역수집·무결성 3종·로컬 HTML 리포트"
```

---

### Task 7: `jmeter:report` — 보고서·차트 스킬

**Files:**
- Create: `plugins/jmeter/skills/report/SKILL.md`

**Interfaces:**
- Consumes: `results/summary.md`(run/knee 누적, §4.3 스키마) + 대상 run의 run.md
- Produces: 결과서 마크다운(`docs/` 또는 사용자 지정 경로) + 차트 파일들(SVG/PNG)

- [ ] **Step 1: SKILL.md 작성** — 필수 섹션:

1. **입력**: 시나리오명 또는 결과 폴더 — summary.md에서 해당 시나리오 행 추출, run.md에서 상세
2. **결과서 구조**(자동 생성 목차): 테스트 범위 표(시나리오|VU|Ramp|Duration|실행시각) / VU별 TPS·p95·stdev 추이 표 / **knee·MAX TPS 판정**(knee 스킬 산출 인용) / 라벨별 스텝 분석(aggregate 결과) / run 폴더 역추적 링크
3. **차트**: matplotlib로 VU-TPS 곡선(포인트+값 라벨), VU-p95, 시나리오 비교 막대 — `gen_stress_charts.py` 패턴(단일 스크립트, 스타일 상속 없이 자체 생성)
4. **병목 판정 스켈레톤**: 클라이언트 지표(JMeter) 확정 사실 + 서버 지표 조회 가이드(Grafana: HikariCP active/pending, CPU, vLLM) — 판정은 사용자 확인 후 기입
5. 경고: 차트/수치는 summary.md·run.md에서만 — 재해석·외삽 금지

frontmatter description: "스트레스 테스트 결과 보고서 생성. summary.md와 run 폴더에서 VU별 추이·knee·MAX TPS 결과서와 차트를 자동 생성. '결과 리포트', '결과서'에서 사용."

- [ ] **Step 2: 검증** — SKILL.md에 5개 섹션 키워드 존재 확인:

```bash
grep -c 'knee\|MAX TPS\|차트\|병목\|역추적' plugins/jmeter/skills/report/SKILL.md   # ≥ 5
```

- [ ] **Step 3: Commit**

```bash
git add plugins/jmeter/skills/report && git commit -m "feat(jmeter): report 스킬 — 결과서·차트 자동 생성"
```

---

### Task 8: 플러그인 README + 통합 검증

**Files:**
- Create: `plugins/jmeter/README.md`
- Modify: `README.md`(root — Task 1에서 추가한 행이 링크 깨지지 않는지 확인)

**Interfaces:**
- Consumes: Task 1~7 전체 산출물
- Produces: 배포 가능한 플러그인 최종본

- [ ] **Step 1: plugins/jmeter/README.md 작성** (How-To): 파이프라인 다이어그램(`lint → deploy → run/knee → collect → report`), 스킬 6종 한 줄 설명과 사용 예(각 `/jmeter:<name>` 호출 예문), jmeter.json 최소 예제, 요구사항(원격 Linux, JDK17, JMeter 5.6.3, ssh 접근)

- [ ] **Step 2: 통합 검증**

```bash
cd ~/git/ai-agent-skill
# (a) 6스킬 존재 + frontmatter 유효
for s in lint deploy run knee collect report; do
  f="plugins/jmeter/skills/$s/SKILL.md"
  [ -f "$f" ] && head -1 "$f" | grep -q '^---' && grep -q '^name:' "$f" && grep -q '^description:' "$f" || { echo "FAIL $s"; exit 1; }
done && echo "6 skills OK"
# (b) plugin 스킬 경로 스캔 동작 (plugin.json skills 필드가 가리키는 디렉토리에 6종)
ls plugins/jmeter/skills | wc -l   # 6
# (c) 스크립트 3종 실행 가능
python3 plugins/jmeter/skills/lint/analyze_jmx.py plugins/jmeter/skills/lint/fixtures/2-3-pre.jmx >/dev/null; [ $? -eq 1 ] && echo "lint OK"
# (d) 루트 README 링크 유효
[ -f "$(grep -o '(\./plugins/jmeter/README.md)' README.md | tr -d '()' | sed 's|^\./||')" ] && echo "README link OK"
```

- [ ] **Step 3: 최종 Commit**

```bash
git add -A && git commit -m "feat(jmeter): 플러그인 README 및 통합 검증 완료 — v1.16.0"
```

---

## Self-Review 결과

- **Spec 커버리지**: §2(6스킬·등록·버전)→Task 1·8, §4.1 lint→Task 2, §4.2 deploy→Task 3, §4.3 run→Task 4, §4.4 knee→Task 5, §4.5 collect→Task 6, §4.6 report→Task 7, §5(리포 반영 5건)→Task 1·8, §6(검증)→각 태스크 검증 스텝 + Task 8 통합. 누락 없음.
- **플레이스홀더**: `<host>` 등은 검증 스크립트가 치환해 검사하는 명시적 인자 표기 — TBD/TODO 없음.
- **타입 일치**: `aggregate.py` CLI 시그니처를 Task 4에서 정의하고 Task 5(knee)가 `../run/aggregate.py`로 동일 참조 — 일치. `check_integrity.py` 종료코드 계약 Task 6 내 일관.
