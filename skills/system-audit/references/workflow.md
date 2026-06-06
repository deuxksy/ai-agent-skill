# System Audit Workflow

## Step 0: OS/Distro Detection

```bash
uname -s && uname -m
cat /etc/os-release 2>/dev/null | grep -E '^(ID|ID_LIKE)='
```

### brew path

| OS | 경로 |
|---|---|
| Darwin | `/opt/homebrew/bin` |
| Linux | `/home/linuxbrew/.linuxbrew/bin` |

### System package manager (auto-select by ID)

| ID / ID_LIKE | Manager | Update check | List installed |
|---|---|---|---|
| `fedora` / `rhel` | dnf | `dnf check-update 2>/dev/null \|\| [ $? -eq 100 ]` | `dnf list installed` |
| `debian` / `ubuntu` | apt | `apt list --upgradable` | `dpkg -l` |
| `arch` / `manjaro` | pacman | `checkupdates` | `pacman -Q` |
| Darwin | 없음 | `softwareupdate --list` | N/A |

> **Fedora 주의**: `dnf check-update`는 업데이트 있을 때 exit code 100 반환. 정상 처리 필요.

### Common PATH

```bash
export PATH="/opt/homebrew/bin:/home/linuxbrew/.linuxbrew/bin:/nix/var/nix/profiles/default/bin:$HOME/.local/bin:$HOME/.local/share/mise/shims:$PATH"
```

**존재하지 않는 명령어는 스킵**: 실행 전 `which <cmd> >/dev/null 2>&1` 로 확인.

---

## Step 1: Version Collection

모든 매니저에서 설치된 패키지 버전 수집.

| Manager | Command |
|---|---|
| mise | `mise list` |
| uv | `uv tool list` |
| pnpm | `pnpm list -g --depth=0` |
| Homebrew | `brew list --formula --versions` |
| Homebrew (cask) | `brew list --cask --versions` |
| pip | `pip list --format=json` |
| npm | `npm list -g --depth=0 --json` |
| nix | `nix profile list` |
| System | `dnf list installed` / `dpkg -l` / `pacman -Q` |

---

## Step 2: Phase 1 — Built-in Audit

사용 가능한 내장 audit 도구 실행.

- `npm audit` (npm, 프로젝트 lockfile만, 글로벌 아님)
- `pip-audit` 또는 `safety check` (pip, 설치된 경우)
- `dnf updateinfo list security` (Fedora)

> **주의**: `brew audit`은 formula 스타일 검사기이지 CVE 스캐너가 아님. 사용하지 않음.
> macOS에서 패키지 CVE 스캔이 필요하면 `trivy` 또는 `grype` 사용 (설치된 경우).

**내장 audit 없는 매니저**: mise, uv tool, pnpm global, nix, pacman → Phase 3 진행.

---

## Step 3: Phase 2 — Outdated Package Filtering

CVE 검색 대상 패키지 필터링. 두 그룹으로 분리:

### 그룹 A: 구버전 패키지 (업데이트 가능)

| Manager | Command |
|---|---|
| mise | `mise outdated` |
| uv | `uv tool list --outdated` |
| pnpm | `pnpm outdated -g` |
| Homebrew | `brew outdated` |
| pip | `pip list --outdated` |
| npm | `npm outdated -g` |
| System | `dnf check-update 2>/dev/null \|\| [ $? -eq 100 ]` / `apt list --upgradable` / `checkupdates` |
| nix | 수집된 버전 vs 최신 비교 |

### 그룹 B: 최신 패키지 (CVE 없음 확인 안 함)

> **주의**: 최신 버전이라도 CVE가 존재할 수 있음 (패치 미출시). 하지만 대부분의 경우 최신 버전은 패치가 적용되어 있음.
> 시간 제약상 구버전 패키지를 우선 스캔. 사용자가 전체 스캔을 요청하면 그룹 B도 포함.

Phase 1에서 이미 탐지된 패키지는 중복 검색하지 않음.

---

## Step 4: Phase 3 — CVE → NVD → CVSS → CISA KEV

구버전 패키지에 대해 4단계 분석 수행.

### Step 4A: CISA KEV 카탈로그 다운로드

세션당 1회만 다운로드하여 로컬 캐시.

```bash
# CISA KEV 전체 카탈로그 (API 키 불필요)
CISA_KEV_FILE=$(mktemp)
curl -sf "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json" \
  -o "$CISA_KEV_FILE"
```

### Step 4B: CVE 검색 (구버전 패키지만)

- **스킵**: Phase 1에서 이미 탐지됨
- **스킵**: 최신 버전 (그룹 B, 기본)
- 검색 소스: GitHub Security Advisories, OSSEC advisory

### Step 4C: NVD API v2.0 상세 조회 (CVE 발견 시)

```bash
# NVD API v2.0 — rate limit: 무인증 5 req/30s
# 6초 간격으로 호출하여 rate limit 회피
sleep 6
curl -sf "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-XXXX-XXXXX"
```

> **Rate limit 대응**: NVD 무인증 API는 30초당 5회. 연속 호출 시 6초 간격 필수.
> `503 Service Unavailable` 시 최대 3회 재시도 (30초 간격).
> API 키 발급 시 50 req/30s 가능: https://nvd.nist.gov/developers/request-an-api-key

NVD 응답에서 추출:

| 필드 | 경로 | 용도 |
|---|---|---|
| CVE ID | `vulnerabilities[].cve.id` | 식별자 |
| CVSS v3.1 | `metrics.cvssMetricV31[].cvssData.baseScore` | 심각도 (0.0~10.0) |
| CVSS v3.1 등급 | `metrics.cvssMetricV31[].cvssData.baseSeverity` | Critical/High/Medium/Low |
| CVSS v4 | `metrics.cvssMetricV40[].cvssData.baseScore` | 있으면 우선 사용 |
| 영향 버전 | `configurations[].nodes[].cpeMatch[]` | 설치 버전과 비교 |
| 설명 | `descriptions[].value` | 취약점 요약 |

> **주의**: CVE에 따라 CVSS v4, v3.1, v3.0, v2, 또는 메트릭 없음 가능.
> 우선순위: v4 > v3.1 > v3.0 > v2. 없으면 "심각도 미정" 표시.

### Step 4D: CISA KEV 확인 (CVE 발견 시)

```bash
# KEV 카탈로그에서 CVE ID 검색
python3 -c "
import json, sys
with open('$CISA_KEV_FILE') as f:
    kev = json.load(f)
cve_id = 'CVE-XXXX-XXXXX'
for vuln in kev.get('vulnerabilities', []):
    if vuln.get('cveID') == cve_id:
        print(f\"KEV: YES | {vuln.get('vendorProject')} | {vuln.get('product')} | Due: {vuln.get('dueDate')}\")
        sys.exit(0)
print('KEV: NO')
"
```

> CISA KEV `dueDate`는 미국 연방기관 조치 기한. 사용자 환경의 실제 위험도와 다를 수 있음.

CISA KEV에 포함된 취약점 = **실제 공격에 악용 중** → 최우선 보고.

### Step 4E: CVSS 분류

| CVSS 점수 | 등급 | 보고 우선순위 |
|---|---|---|
| 9.0~10.0 | Critical | 최우선 |
| 7.0~8.9 | High | 높음 |
| 4.0~6.9 | Medium | 보통 |
| 0.1~3.9 | Low | 낮음 |

KEV + Critical = 최상위 우선순위.

---

## Step 5: CVE Validation (all phases)

**핵심 규칙**: CVE가 설치 버전의 영향 범위 내인지 필수 확인.

### 버전 비교 주의사항

> **Semver 범용 비교 불가**: 배포판마다 버전 체계가 다름.
> - Debian: epoch 포함 (예: `1:2.3.4-1`)
> - RPM: EVR (Epoch:Version-Release)
> - Python: PEP 440 (예: `1.0.0.post1`)
> - Nix: 임의 버전 문자열
>
> 가능하면 NVD의 `cpeMatch` 결과(`vulnerable: true/false`)를 직접 활용.
> 불가능하면 패키지 매니저의 공식 채널(advisory)로 확인.

### CPE 매칭 시 고려 사항

- `versionStartIncluding` / `versionEndIncluding` (포함)
- `versionStartExcluding` / `versionEndExcluding` (제외)
- `vulnerable: false`인 항목은 제외
- 복합 노드(AND/OR) 고려

범위 외 → **무시, 보고하지 않음**
범위 내 → **보고**

예시:

- CVE 영향 `<= 2.3.1` (endIncluding), 설치 `2.4.0` → **스킵**
- CVE 영향 `< 3.0.0` (endExcluding), 설치 `2.5.0` → **보고**
- CVE 영향 `>= 1.0.0, < 3.0.0`, 설치 `2.5.0` → **보고**

---

## Step 6: Report

[response-format.md](response-format.md) 참조. 보고 순서:

1. **KEV + Critical/High** — 최우선
2. **Critical/High** (KEV 제외)
3. **Medium/Low**
4. **업데이트만 가능** (CVE 없음)

Step 1~4에서 이미 수집한 데이터 사용, 재실행하지 않음.
