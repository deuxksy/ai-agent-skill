---
name: backdoor-investigation
description: "Linux 서버 백도어/맬웨어 침해 포렌식 진단. read-only 명령(ps/ss/find/strings/lsof/stat/journalctl)으로 프로세스·네트워크·파일·로그 조사 후 증거 수집·로컬 다운로드·보고서 자동 생성. Use when 백도어 의심 증상 - CPU 급증, 역외 연결, 모르는 계정, /etc 변경, 로그인 실패 급증, libudev.so/gcc.sh 흔적, Mirai. 서버 변경(rm/kill/iptables)은 backdoor-remediation 스킬."
---

# Backdoor Investigation

Linux 서버 백도어 침해 포렌식 진단. **read-only 명령만 사용**해 서버를 변경하지 않고 조사 → 증거 보존 → 보고서 생성. 대응(제거)은 별도 스킬.

## 핵심 원칙

- **증거 보존 우선**: 원본 파일 수정/삭제 금지. 원격 `/tmp`는 임시 수집 단계, **최종 증거는 `scp`로 로컬(`~/forensic/`)에 보존**.
- **read-only 자동 실행**: Phase 1-5 명령은 서버 변경 없음. Claude가 `ssh <host>`로 직접 실행.
- **대응 분리**: rm/kill/iptables/passwd 등 파괴적 조치는 `backdoor-remediation` 스킬에서 승인 후.

## When to Use

- 백도어 의심 증상: CPU/메모리 급증, 설명 안 되는 프로세스
- 역외 네트워크 연결, 알 수 없는 포트 리스닝
- 모르는 계정, 암호 변경 실패, 로그인 실패 급증
- 시스템 파일 변경(`/etc`, `/bin`, `/usr/bin`), 이상한 파일
- Mirai 흔적(`libudev.so`, `gcc.sh`, `/etc/init.d/` 랜덤이름)

## 사용법

```text
/zzizily:backdoor-investigation <host>
```

- `<host>`: `~/.ssh/config` Host alias 또는 `/etc/hosts` 호스트명
- **스킬에 IP/접속정보 하드코딩 없음** — alias는 `~/.ssh/config`가 SoT. ProxyJump도 거기 정의됨

## 실행 흐름

```dot
graph TD
    A[1. triage 1분 진단] --> B{의심 징후}
    B -- 없음 --> F[5. 보고서 생성]
    B -- 있음 --> C[2. 심층 진단]
    C --> D[3. 증거 수집]
    D --> E[4. 로컬 다운로드]
    E --> F
    F --> G[대응 필요시 remediation 스킬]
```

## Phase 1 — triage (1분, read-only)

```bash
ssh <host> 'ps auxf | head -100'
ssh <host> 'ss -tuln; echo ---; ss -tnp | grep ESTAB'
ssh <host> 'who -a; echo ---; last -20; echo ---; lastb -20 2>/dev/null'
ssh <host> 'uptime; echo ---; dmesg | tail'
```

분석: 의심 프로세스, 역외 ESTAB, 모르는 접속자, 최근 커널 메시지.

## Phase 2 — 심층 진단 (read-only)

```bash
# 최근 7일 /etc·/bin 변경
ssh <host> 'find /etc /bin /usr/bin -mtime -7 -type f -ls 2>/dev/null'

# 크론
ssh <host> 'crontab -l 2>/dev/null; echo ---; ls /etc/cron.*; echo ---; cat /etc/crontab'

# 백도어 파일 흔적 - Mirai 전형
ssh <host> 'find / -name "*libudev*" -o -name "gcc.sh" 2>/dev/null'

# 최근 설치된 의심 실행파일 - 백도어 랜덤이름 (예: imzfhjbuof)
ssh <host> 'find /usr/bin /usr/sbin /bin /sbin -mtime -30 -type f -perm /111 -ls 2>/dev/null'

# init.d 백도어 - 최근 추가된 비표준 스크립트 (랜덤이름)
ssh <host> 'find /etc/init.d/ -mtime -30 -type f -ls 2>/dev/null'
ssh <host> 'find /tmp -type f -perm /111 -ls 2>/dev/null'

# 프로세스 실행 파일 경로
ssh <host> 'for p in $(ps -eo pid); do ls -la /proc/$p/exe 2>/dev/null; done'

# 의심 PID 상세 - 열린 파일/소켓
ssh <host> 'lsof -p <PID> 2>/dev/null'

# Mirai 지문 - libudev.so strings (XOR *6F62 / 자동시작 / C2 / nameserver)
ssh <host> 'strings /lib/libudev.so 2>/dev/null | grep -E "POST|GET|Host:|\\*6F62|update-rc|chkconfig|/proc/net/tcp|nameserver" | head'
ssh <host> 'md5sum /lib/libudev.so 2>/dev/null'

# 네트워크 심층 - 사설/CGNAT 대역 제외 역외 필터 (10/172.16-31/192.168/169.254/100.64-127/127)
ssh <host> 'ss -tnp | awk "\$5 !~ /^(10\\.|192\\.168\\.|172\\.(1[6-9]|2[0-9]|3[01])\\.|169\\.254\\.|100\\.(6[4-9]|[7-9][0-9]|1[01][0-9]|12[0-7])\\.|127\\.)/"'
ssh <host> 'ip addr show; ip route show; iptables -L -n -v'
```

분석: /etc 변경 시간, 크론 악용, libudev.so Mirai 지문, `/usr/bin`·init.d 랜덤이름 바이너리, 역외 IP.

## 백도어 패턴 식별표

| 유형 | 특징 | 위치 |
| :--- | :--- | :--- |
| Mirai | libudev.so 위장, C2 통신 | /lib/libudev.so, /usr/bin/[랜덤] |
| cron 백도어 | 크론 주기 실행 | /etc/cron.hourly/gcc.sh |
| init.d 백도어 | 부팅 시 자동 시작 | /etc/init.d/[랜덤이름] |
| SSH 키 | 인증키 몰래 추가 | ~/.ssh/authorized_keys |
| rc.local | 부팅 스크립트 | /etc/rc.local |

## 타임라인 재구성 (§4)

원본 로그가 소실된 경우 파일 mtime이 핵심 증거(cluster-06 사고가 mtime 기반으로 재구성됨):

```bash
# 의심 파일 정확 생성/수정 시각
ssh <host> 'stat /lib/libudev.so /etc/cron.hourly/gcc.sh 2>/dev/null'

# 최근 변경 전체 타임라인 (시각순)
ssh <host> 'find /etc /usr/bin /lib -mtime -7 -type f -exec stat -c "%y %n" {} \; 2>/dev/null | sort'

# 인증 로그 기반 타임라인
ssh <host> 'grep -E "Accepted|Failed|session opened" /var/log/auth.log 2>/dev/null | tail -50'
```

## 하이퍼바이저/K8s 노드 추가 점검

PVE 하이퍼바이저 (cluster-06 사고 경로 - PVE Web UI 8006 무차별 대공격 → root@pam 침해):

```bash
ssh <host> 'qm list 2>/dev/null'
ssh <host> 'cat /etc/pve/user.cfg 2>/dev/null'   # 백도어 계정(root@pam 외 추가) 확인
ssh <host> 'journalctl -b | grep -E "pvedaemon|pveproxy" | grep -iE "auth|login|Failed|successful" | tail -50'
```

K8s 노드:

```bash
ssh <host> 'crictl ps -a 2>/dev/null | head -50'
ssh <host> 'ls /etc/kubernetes/manifests/ 2>/dev/null'
ssh <host> 'systemctl status kubelet 2>/dev/null | head'
```

## Phase 3 — 증거 수집

```bash
ssh <host> 'bash -s' < scripts/collect-evidence.sh
# 원격 /tmp/backdoor-evidence-<host>-<ts>.tar.gz 생성
# 스크립트 출력의 EVIDENCE: <경로> 를 Phase 4에서 사용
```

스크립트는 read-only 수집만. 원본 미변경.

## Phase 4 — 로컬 다운로드

```bash
mkdir -p ~/forensic/<host>-<ts>/
chmod 700 ~/forensic/<host>-<ts>/
# collect-evidence.sh 출력 EVIDENCE: 경로를 정확히 사용 (와일드카드 금지 - 이전 수집물 섞임 방지)
scp <host>:/tmp/backdoor-evidence-<host>-<ts>.tar.gz ~/forensic/<host>-<ts>/
md5sum ~/forensic/<host>-<ts>/*.tar.gz > ~/forensic/<host>-<ts>/md5.txt
```

## Phase 5 — 보고서 자동 생성

수집 결과를 바탕으로 보고서 작성:

- **TL;DR**: 침해 일자·백도어 유형·심각도·현재 상태
- **IOC**: 악성 파일 해시·목록·공격자 IP
- **타임라인**: 접속/수정/실행 이벤트 시계열
- **백도어 분석**: 구조·통신·C2
- **영향도**: 시스템 변경 사항·침해 범위
- **대응 권고**: `/zzizily:backdoor-remediation` 안내

## 금지 (안전 정책)

아래는 전부 `backdoor-remediation`에서 승인 후 실행:

- 원본 파일 `rm`/`mv`/`sed -i` (사본만 `/tmp`)
- `kill`/`pkill` (프로세스 관찰만)
- `iptables`/`ufw` 변경 (조회만)
- `passwd`/`useradd`

## 참고

- 가이드 원본: `docs/Mirai/backdoor-investigation-guide.md` §1-7
- 실제 사고 사례: `docs/Mirai/incident-report-cluster-06-backdoor.md`
- 대응(§8-9)은 `backdoor-remediation` 스킬
