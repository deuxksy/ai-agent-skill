#!/bin/bash
# 백도어 조사 증거 수집 스크립트 (read-only, 원본 미변경)
# 원격 실행: ssh <host> 'bash -s' < collect-evidence.sh
# 출력: /tmp/backdoor-evidence-<hostname>-<timestamp>.tar.gz
set -u
umask 077    # shadow 등 민감 파일 보호 (기본 022 노출 방지)

HOSTNAME=$(hostname)
DATE=$(date +%Y%m%d-%H%M%S)
DIR="/tmp/backdoor-evidence-$HOSTNAME-$DATE"
mkdir -p "$DIR" && chmod 700 "$DIR"

# 시스템 정보
uname -a > "$DIR/uname.txt"
uptime > "$DIR/uptime.txt"

# 프로세스
ps auxf > "$DIR/ps-tree.txt" 2>&1
ps auxw > "$DIR/ps-wide.txt" 2>&1

# 네트워크
ss -tuln > "$DIR/ss-listen.txt" 2>&1
ss -tnp > "$DIR/ss-established.txt" 2>&1
ip addr show > "$DIR/ip-addr.txt" 2>&1
ip route show > "$DIR/ip-route.txt" 2>&1
iptables -L -n -v > "$DIR/iptables.txt" 2>&1

# 로그인 기록
last > "$DIR/last.txt" 2>&1
lastb > "$DIR/lastb.txt" 2>&1
who -a > "$DIR/who.txt" 2>&1

# 파일 시스템 (read-only, 사본)
find /etc -mtime -7 -type f -ls > "$DIR/etc-changed.txt" 2>/dev/null
ls -la /etc/init.d/ > "$DIR/initd.txt" 2>&1
cat /etc/crontab > "$DIR/crontab.txt" 2>&1
cat /etc/passwd > "$DIR/passwd.txt" 2>&1
cat /etc/shadow > "$DIR/shadow.txt" 2>&1

# 사용자 크론
crontab -l > "$DIR/user-crontab.txt" 2>&1

# 백도어 흔적
find / -name '*libudev*' -ls > "$DIR/libudev-files.txt" 2>/dev/null
find / -name 'gcc.sh' -ls > "$DIR/gcc-sh.txt" 2>/dev/null
find /tmp -type f -perm /111 -ls > "$DIR/tmp-exec.txt" 2>/dev/null

# 로그
journalctl -b > "$DIR/journal.log" 2>/dev/null
tail -1000 /var/log/auth.log > "$DIR/auth.log" 2>/dev/null
tail -1000 /var/log/syslog > "$DIR/syslog.log" 2>/dev/null

# 압축 (원본 $DIR 디렉토리는 증거 보존을 위해 유지)
tar czf "$DIR.tar.gz" -C /tmp "$(basename "$DIR")" 2>/dev/null

echo "EVIDENCE: $DIR.tar.gz"
echo "DIR: $DIR"
echo "SIZE: $(du -h "$DIR.tar.gz" 2>/dev/null | cut -f1)"
