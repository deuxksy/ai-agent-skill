---
name: deploy
description: "JMeter 부하원 원격 설치·배포·기동. 미설치 서버에 JDK17+JMeter 5.6.3을 idempotent하게 설치하고(tarball→/usr/local/bin 심링크), 프로젝트 자산을 rsync(mac/linux)·robocopy(Windows)로 증분 배포한 뒤 jmeter-server를 저장소 루트 CWD로 기동·검증. '부하원 배포', 'jmeter 서버 세팅', 'deploy'에서 사용."
---

# Deploy — 설치·배포·기동

> **부하 발사 원칙 (절대 — spec §3)**: 부하는 항상 **원격 부하원**(master에서 `-R workers` 분산, 또는 단독 부하원)에서만 발사한다. 로컬(맥/Windows)에서 JMeter를 실행해 부하를 발사하는 것을 금지한다. 로컬 `jmeter` 바이너리는 `-g`(jtl→HTML 리포트) **후처리 전용**으로만 사용한다. 이 스킬이 세팅·기동하는 원격 노드가 곧 부하원이다.

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
