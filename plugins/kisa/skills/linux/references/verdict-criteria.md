# U-01~U-73 판정 기준 (KISA 기반)

- 근거: 주요정보통신기반시설 기술적 취약점 분석·평가 방법 상세가이드 (2026.12판 우선, 항목명 매핑) 및 구체계 점검 가이드
- 원칙: **양호 조건을 문자 그대로 충족할 때만 양호. 설정 부재·확인 불가는 취약 (보수적 판정)**
- 실측 환경: Debian 13 + Proxmox VE (2026-09 ecoai 6대 전수 — 전 서버 양호 56·취약 17 동일)

## 판정표

| U | 항목 | 양호 조건 | 취약 실측 예 (Debian/Proxmox 표준) |
| :--- | :--- | :--- | :--- |
| U-01 | root 원격 접속 제한 | 원격터미널 미사용 또는 root 직접접속 차단 (`PermitRootLogin no` + securetty pts 제거) | `PermitRootLogin yes` |
| U-02/07 | 패스워드 복잡성·최소 길이 | pwquality.conf 설정 (복잡성+minlen) | `/etc/security/pwquality.conf` 부재 |
| U-03 | 계정 잠금 임계값 | `pam_faillock` 임계값 10회 이하 | pam_faillock 미설정 |
| U-04/18/19 | passwd/shadow 보호 | passwd 644 root:root, shadow 640 root:shadow | (Debian 표준=양호) |
| U-05 | root 외 UID 0 | root만 UID 0 | — |
| U-06 | root SU 제한 | su 특정 그룹(pam_wheel) 제한. 단 root-only 운영은 예외 주석 | pam_wheel 주석 처리 |
| U-08/09 | 패스워드 사용기간 | MAX≤90일, MIN≥1일 | MAX 99999 / MIN 0 |
| U-10~14 | 계정·그룹·shell | 불필요 계정 제거, 관리자 그룹 최소, UID/GID 중복 없음 | (Debian 표준=양호) |
| U-15 | Session Timeout | TMOUT 600초 이하 | TMOUT 미설정 |
| U-16~21/23/25 | 주요 파일 권한 | 소유자 root(또는 bin/sys), 644/755 이하 | (Debian 표준=양호) |
| U-22 | syslog 설정 권한 | `/etc/(r)syslog.conf` root 소유 640 이하 | rsyslog.conf 부재 — journald 운영은 기준 미명시 → 취약 (보수적) |
| U-24 | SUID/SGID | 불필요 SUID/SGID 제거 | 표준 시스템 바이너리만 → 양호 |
| U-26 | world writable | 불필요 world writable 없음 (/tmp 제외) | 없음 → 양호 |
| U-28 | .rhosts/hosts.equiv | 파일 부재 | 부재 → 양호 |
| U-29 | 접속 IP·포트 제한 | hosts.allow/deny 또는 sshd AllowUsers 등 설정 | 전부 미설정 |
| U-31/45 | NIS | NIS 미설치·비활성 | 비활성 → 양호 |
| U-32 | UMASK | 022 이상 | Debian 기본 `0002` (신규 파일 664) → 취약 |
| U-33~35 | 홈 디렉터리·숨김 파일 | 소유자·권한 적정, 위험 숨김 파일 없음 | (표준=양호) |
| U-36~40/46 | finger·FTP·r계열·DoS·tftp | 해당 서비스 전부 비활성 | 비활성 → 양호 |
| U-41/42/68 | NFS | NFS 서버 비활성, /etc/exports 없음 | 비활성 → 양호 |
| U-43 | automountd | autofs 비활성 | 비활성 → 양호 |
| U-44 | RPC | 불필요 RPC 비활성 | rpcbind `0.0.0.0:111` LISTEN (NFS 미사용) → 취약 |
| U-47~49 | 메일 (postfix) | 최신 버전, 릴레이 제한, 일반 실행 방지 | postfix Debian 최신판 → 양호 |
| U-50/51 | DNS | DNS 서비스 미사용 또는 최신·ZoneTransfer 제한 | 미사용 → 양호 |
| U-52~58/70 | 웹서버 | 웹서비스 미설치 또는 Apache 기준 충족 | 미설치(K8s 노드) → 양호(해당없음) |
| U-59 | ssh 원격접속 | SSH2 (Telnet 비활성) | 미지정=SSH2 전용 → 양호 |
| U-60~64 | FTP·at | 서비스 미사용 | 미사용 → 양호 |
| U-65/66 | SNMP | SNMP 비활성 또는 community 복잡·v3 | 비활성 → 양호 |
| U-67 | 경고 메시지 | 로그온 시 법적 경고 문구 설정 | Debian 기본 안내 문구뿐 → 취약 |
| U-69 | expn/vrfy | `disable_vrfy_command=yes` (noexpn/novrfy) | postfix 미지정 → 취약 |
| U-71 | 보안패치 | 패치 정책 수립·주기 적용 | upgradable 다수(security 포함) → 취약 |
| U-72 | 로그 정기 검토 | 정기 검토·분석·보고 체계 | 체계 부재 → 취약 |
| U-73 | 시스템 로깅 | 로그 정책 수립 + 기록 | journald 영구저널 운영하나 정책 미수립 → 취약 (보수적) |

## Debian/Proxmox 표준 구성 판정 참고

동일 provisioning 서버군은 취약 목록이 동일하게 나온다 (2026-09 ecoai 실측):

```text
취약 17: U-01,02,03,06,07,08,09,15 (계정 8) / U-22,29,32,44 (파일·서비스 4) / U-67,69,71,72,73 (로그·패치 5)
```

- `/etc/opasswd` 경로 주의: KISA 구가이드는 `/etc/opasswd`로 표기하나 PAM 표준 경로는 `/etc/security/opasswd` (pam_unix remember 옵션 시 생성)
- umask는 설정 파일뿐 아니라 로그인 셸 실측(`umask` 명령)으로 확인 — 신규 파일 권한(664 등)으로 검증
