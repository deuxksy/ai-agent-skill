---
name: deploy
description: "JMeter 부하원 원격 설치·배포·기동. 미설치 서버에 JDK17+JMeter 5.6.3을 idempotent하게 설치하고(tarball→/usr/local/bin 심링크), 실행 자산 src/jmeter를 rsync(mac/linux)·robocopy(Windows)로 미러 동기화한 뒤 jmeter-server를 저장소 루트 CWD로 기동·검증. '부하원 배포', 'jmeter 서버 세팅', 'deploy'에서 사용."
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

원격 부하원은 **실행 자산 `src/jmeter/`만** 보관한다 (2026-09-04 변경 — 이전에는 저장소 전체를 exclude 증분 배포). 원격 폴더(`~/git/ecoai-gwageo`)는 빈 뼈대만 있으면 되고, run 스킬이 `results/`는 `mkdir -p`로 자동 생성한다.

```bash
# mac/Linux — src/jmeter만 미러 동기화 (상위 폴더 선보장)
ssh <host> 'mkdir -p <remote_path 절대경로>/src/jmeter'
rsync -az --delete ./src/jmeter/ <host>:<remote_path 절대경로>/src/jmeter/
# Windows (PowerShell) — src/jmeter 한정이면 /MIR 안전. SMB 미탑재면 scp -r fallback:
# robocopy .\src\jmeter \\<host-ip>\<share>\<path>\src\jmeter /MIR
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
