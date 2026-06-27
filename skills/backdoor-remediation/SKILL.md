---
name: backdoor-remediation
description: "Linux 서버 백도어 제거·복구·예방 대응. 백도어 파일 삭제 rm, 프로세스 종료 kill, 역외 차단 iptables, 암호 변경 passwd, 크론/init.d 정리, SSH 강화, Fail2Ban/OSSEC 설치. Use when backdoor-investigation 스킬이 백도어 침해를 확인한 후. 전 명령 서버 파괴적 변경이므로 사용자 승인 후 실행."
---

# Backdoor Remediation

백도어 제거·복구·예방. **전 명령 서버 파괴적 변경** → 승인 후 실행.

## 핵심 원칙

- **증거 보존 완료 전 미실행**: 진단 스킬(`backdoor-investigation`) Phase 3-4 완료 후에만.
- **전 명령 승인**: 각 명령 실행 전 사용자 확인. Claude 임의 실행 금지.
- **합의 기반**: 진단 결과(IOC·파일·프로세스·IP)를 Claude/사람이 함께 검토 후 조치.

## When to Use

- `backdoor-investigation` 스킬이 백도어 확인 후
- 증거 수집·로컬 다운로드 완료 후

## 사전 확인 (진단 결과 입력)

진단 보고서에서 아래를 확보해 둘 것:

- 백도어 파일 목록 (예: `/lib/libudev.so`, `/etc/cron.hourly/gcc.sh`)
- 악성 프로세스 PID/이름
- 공격자/역외 IP
- 백도어 유형 (Mirai/cron/init.d/SSH키/rc.local)

## 1. 즉시 조치 (승인 후)

```bash
# 역외 연결 차단 (-I 로 최상단 INSERT. -A 는 기존 ACCEPT 뒤면 무효)
ssh <host> 'iptables -I INPUT -s <공격자IP> -j DROP'
ssh <host> 'iptables -I OUTPUT -d <공격자IP> -j DROP'

# 백도어 프로세스 종료
ssh <host> 'kill -9 <PID>'
ssh <host> 'pkill -f libudev.so'

# 백도어 파일 삭제
ssh <host> 'rm -f /lib/libudev.so /usr/bin/<백도어>'
```

서버 격리(네트워크 단절)는 공유기/상위 방화벽 단에서 사용자 직접 수행.

## 2. 복구 (승인 후)

```bash
# 암호 변경 (-t TTY 필수, 없으면 hang)
ssh <host> -t 'passwd root'

# SSH 키 재발급 - 의심 키 삭제 (새 키 배포는 사용자 로컬에서)
ssh <host> 'rm -f ~/.ssh/authorized_keys'

# 크론 정리
ssh <host> 'sed -i "/gcc.sh/d" /etc/crontab'
ssh <host> 'rm -f /etc/cron.hourly/gcc.sh'

# init.d 정리
ssh <host> 'rm -f /etc/init.d/<백도어스크립트>'
ssh <host> 'update-rc.d -f <백도어스크립트> remove'
```

## 3. 예방 (승인 후)

```bash
# SSH 강화 (/etc/ssh/sshd_config)
#   PermitRootLogin no
#   PasswordAuthentication no
#   PubkeyAuthentication yes
#   AllowUsers <허용사용자>
ssh <host> 'systemctl restart ssh'

# Fail2Ban (무차별 대입 차단)
ssh <host> 'apt install -y fail2ban'

# OSSEC (파일 무결성 모니터링)
ssh <host> 'apt install -y ossec-hids-server'
```

## 승인 프로토콜

1. Claude가 명령 + 영향 범위(대상 파일/PID/IP) 보고
2. 사용자 승인 또는 거부/수정
3. 승인된 명령만 실행
4. 실행 결과 보고

## 금지 (자동 실행)

- 어떤 명령도 사전 승인 없이 실행 금지
- `rm`/`kill`/`iptables`/`passwd`/`sed -i`/`apt install` 전부 승인 게이트 통과 후
- **정책 정합**: OpsHub "삭제 금지"는 DB `DROP`/`TRUNCATE`·`kubectl delete` 컨텍스트. 백도어 파일 `rm`은 사고 대응의 본질이므로 **승인 후 허용**

## 참고

- 가이드 원본: `docs/Mirai/backdoor-investigation-guide.md` §8-9
- 진단(§1-7)은 `backdoor-investigation` 스킬
