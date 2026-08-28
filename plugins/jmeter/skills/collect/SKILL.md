---
name: collect
description: "JMeter 원격 실행 결과 수집·무결성 검증. master의 results/를 로컬로 증분 역수집(rsync/robocopy)하고, 무결성 3종(필드수·span·summary)으로 중단 run을 걸러내며, 로컬에서 jmeter -g HTML 리포트를 생성. '--evidence'로 원격·클러스터 로그 증거 보존. '결과 수집', 'jtl 받아', '리포트 생성'에서 사용."
---

# Collect — 결과 수집·무결성

전제: run/knee가 master의 `<remote_path>/results/`에 만든 실행 결과. 수집 대상은 파일 단위 증분 — 이미 로컬에 있는 run은 다시 받지 않는다.

> **부하 발사 원칙 준수**: 이 스킬의 로컬 `jmeter` 호출은 `-g`(jtl→HTML 리포트) 후처리뿐이다. 수집·판정·리포트 생성 외 목적으로 로컬에서 JMeter를 실행하지 않는다.

## 1. 수집 (master → 로컬, 증분)

```bash
rsync -az --exclude=summary.md <master>:<remote_path 절대경로>/results/ ./results/
# Windows는 reverse robocopy (원격→로컬, /MIR 금지):
# robocopy \\<master-ip>\<share>\results .\results /E /XD .git summary.md
# SMB 미탑재면 scp -r fallback
```

`summary.md`는 로컬에서 누적 편집 후 push하는 단방향 파일이다 — pull에 포함하면 원격 구버전이 로컬 편집분을 되돌린다 (2026-08-28 실측 회귀: knee 사이클 중 pull이 세션 블록 행을 삭제). run.md는 폴더 단위라 충돌 없음.

수집 직후 jtl만 누락된 run이 없는지 `ls results/*/result.jtl` 대응점검.

## 2. 무결성 3종 (run 폴더마다 — check_integrity.py)

```bash
python3 check_integrity.py results/<OUT>; echo exit=$?
```

| 검사 | 대상 파일 | 판정 |
| :-- | :-- | :-- |
| ① 마지막 라인 필드수 = 헤더 | result.jtl | 불일치 시 중단 |
| ② 샘플 span ≈ DURATION±20% (폴더명 `_D{d}` 추출) | result.jtl | 이탈 시 중단 의심 |
| ③ 최종 summary 라인 존재 | jmeter.log | 부재 시 중단 의심 |

- 종료코드: `0` 양호 / `1` 중단 의심 — `1`이면 해당 run은 집계·보고에서 제외하고 원인(run.md 특이사항, jmeter.log 끝)을 확인
- 검사 대상 파일 분리 원칙: `summary =`는 콘솔(jmeter.log) 항목이지 jtl(CSV)에는 없다 — jtl에 summary가 없다고 오경고하지 않는다
- **특정 라벨 전체가 일관되게 필드수가 다르면 중단이 아니라 JMX 출력 특성**이다 — 마지막 라인 불일치가 특정 라벨(예: 3.4.1, Connect 필드 미출력으로 17≠18)의 전체 패턴이고 span 검사②·jmeter.log 정상 종료가 확인되면 run 유효로 판정한다 (2026-08-29 3-4 사례: 두 run 연속 동일 경고, 데이터 온전)

## 2.5 소급 집계 (실행 완료·집계 전 중단 run)

무결성 통과 run 중 `run.md`가 없는 것(세션 중단으로 실행만 원격에 남은 경우)은 run 스킬의 "실행 후 자동 3종"을 소급 수행한다 — 집계 → run.md 생성(특이사항에 "소급 작성" 명시, 실행 일시는 폴더 타임스탬프 부하원 TZ에서 KST 환산) → summary.md 누적. 무효(무결성 exit=1) run은 표에 `베이스라인(무효)`·`래더(무효)`로 기록해 재실행 대상임을 남긴다 (2026-08-28 실측 — 세션 중단 11건 복구).

## 3. HTML 리포트 (로컬 생성)

```bash
cd results/<OUT> && jmeter -g result.jtl -o report
```

- `-o` 대상 폴더는 **비어 있어야 함** — 기존 report가 있으면 치우고 재생성
- 로컬 자원 절약상 대량 run은 필수 run만 선택 생성

## 4. --evidence (원격 로그 수집 보존)

장애·오류 run은 수집 파일만으로 원인이 안 보일 수 있다 (Kakao 500 사례 — 클라이언트 jtl에는 500만 보이고 서버 로그에 실제 예외). 실행 직후 시각을 run.md에서 확인해 아래를 수집·파일로 저장:

```bash
kubectl logs <pod> --since=2h > results/<OUT>/evidence-<pod>.log
ssh <worker> 'tail -200 /tmp/jmeter-server.log' > results/<OUT>/evidence-jmeter-server.log
```

## 내장 주의

- 중단 run의 jtl은 span 검사(②)가 잡는다 — 무결성 스킵은 금지 (2-3 첫 실행 56s 조기종료 사례)
- 역수집은 증분이 원칙 — `-p`/`--checksum` 불필요, 파일 mtime 신뢰
