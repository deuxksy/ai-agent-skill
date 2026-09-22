---
name: server
description: "Unix/Linux 서버 보안 취약점 점검 (KISA U-01~U-73). 읽기 전용 명령으로 계정·파일·서비스·패치·로그 관리 73개 항목 점검 후 양호/취약 판정과 증빙 리포트 생성. `/kisa:server <ip-or-hostname>`."
---

# Server Security Audit (KISA U-01~U-73)

대상 서버에 읽기 전용 명령만 실행해 KISA 주요정보통신기반시설 취약점 점검 체계(U-01~U-73)로 판정한다.

## 핵심 프로세스

```text
대상 접속 확인 → 점검 스크립트 실행 (읽기 전용) → 항목별 판정 (KISA 기준) → 증빙 리포트 md 생성
```

## 사용법

```bash
# 단일 대상
/kisa:server ecoai-cluster-01          # ~/.ssh/config 호스트명
/kisa:server 192.168.10.14             # IP 직접

# 다중 대상은 순차 반복
/kisa:server cluster-01 cluster-02 cluster-03
```

## 절차

### 1. 대상 확인

- `<target>`은 `~/.ssh/config` 별칭 또는 IP. `ssh <target> 'cat /etc/os-release'`로 접속·OS 확인 (Debian/RHEL 계열 Unix)
- Proxmox/K8s 노드 등 원격 접속 경로(ProxyJump·Port)는 ssh config에 정의돼 있어야 함

### 2. 점검 실행 (전부 읽기 전용)

```bash
ssh <target> 'bash -s 2>&1' < scripts/u73-check.sh > /tmp/u-check-<target>-raw.txt
```

- 스크립트는 `@@SEC@@`(항목) / `@@CMD@@`(명령) / `@@END@@` 마커로 명령·결과 원문을 남긴다 — 증빙 재현성 보장
- 사용 명령: `grep`·`cat`·`ls`·`awk`·`find`·`systemctl is-active`·`ss -tnl`·`postconf -h`·`apt list` — 설정 변경 없음

### 3. 판정

각 U-항목의 양호/취약 조건은 [references/verdict-criteria.md](references/verdict-criteria.md) 참조. 요약:

| 그룹 | 항목 | 대표 양호 조건 |
| :--- | :--- | :--- |
| 계정 관리 (U-01~15) | root 원격·패스워드 정책·잠금·su·timeout | `PermitRootLogin no`, pwquality 설정, `pam_faillock`, `TMOUT<=600` |
| 파일·디렉터리 (U-16~35) | 주요 파일 권한·SUID·world writable·UMASK | 소유자 root + 권한 644 이하, `umask>=022` |
| 서비스 관리 (U-36~70) | 불필요 서비스·NFS·RPC·메일·DNS·웹 | 서비스 비활성, `rpcbind` 미구동 |
| 패치·로그 (U-71~73) | 보안패치·로그 검토·로깅 | 패치 최신, 로그 정책 수립 |

**판정 원칙**: 서버 상태가 양호 조건을 문자 그대로 충족할 때만 양호. 확인 불가·설정 부재는 취약 (보수적). 근거는 KISA 상세가이드 (2026판 우선, 체계가 다르면 항목명 매핑).

### 4. 증빙 리포트

출력 경로: **`./report/<target>-<YYMMDDhhmm>.md`** (현재 작업 디렉터리 기준, `report/` 없으면 생성)

```bash
mkdir -p ./report   # 예: ./report/ecoai-cluster-01-2609222310.md
```

출력 형식 (md):

```markdown
# <target> 정보보안점검 증빙 (U-01~U-73)
- 대상: ... - 실행: <일시 KST, 읽기 전용>
- 요약: **양호 N · 취약 M**
## 1. 계정 관리 (U-01~U-23)
### U-01 ... — 판정: **취약**
명령: ```bash ...```
결과: ```text ...```
```

## 안전 규칙

- **읽기 전용만 실행** — 스크립트 외 명령(설정 변경·서비스 조작) 금지. 추가 명령이 필요하면 사용자 승인 후 실행
- 판정은 실측 사실 기반 — 추측으로 양호 판정 금지
- 증빙에는 자격증명(비밀번호·키)이 남지 않는지 확인 후 산출물 저장
- 조치(취약 항목 remediation)는 별도 작업 — 이 스킬은 진단만

## 참고

- 점검 항목 체계: KISA 주요정보통신기반시설 취약점 점검 가이드 (구체계 U-01~73)
- 판정 기준 상세: [references/verdict-criteria.md](references/verdict-criteria.md)
- 관련 스킬: `security:system-audit`(패키지 CVE), `security:backdoor-investigation`(침해 포렌식)
