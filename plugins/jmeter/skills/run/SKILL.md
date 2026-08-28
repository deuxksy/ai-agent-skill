---
name: run
description: "JMeter 시나리오 1회 실행. jmx + 총 VU + ramp + duration(+ mode x2분산/x1단독)을 받아 T를 계산해 분산 실행하고, 풀가동 집계(TPS/p95/stdev/Err)와 run.md, summary.md 누적까지 자동 생성. '부하 실행', 'jmeter 돌려', '--smoke' 사전검증에서 사용."
---

# Run — 1회 실행

> **부하 발사 원칙 (절대 — spec §3)**: 부하는 항상 **원격 부하원**(keco-train-01/02 등 master→workers)에서만 발사한다. 아래 "실행 (master에서)" 명령이 그 구현이다. 로컬(맥/Windows)에서 JMeter를 실행해 부하를 발사하는 것을 금지한다. 로컬 `jmeter` 바이너리는 `-g`(jtl→HTML 리포트) **후처리 전용**으로만 사용한다.

## 인자

- `jmx`(필수), `vu` 총 VU(필수), `ramp`(초, 기본 60), `duration`(초, 기본 120)
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

Err 0 + worker 분산 균형(편차 <10%) + jmeter.json smoke.expect 라벨·상태코드 충족 (미선언 시 범용 기준만)

## 내장 주의

- 콘솔 `summary =` 는 분산 display 오탐 — 판정은 항상 jtl
- 베이스라인(vu=2)은 **R=10, D=30** 기본 (2026-08-28 사용자 확정 — 실행 시간 단축)
