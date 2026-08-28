---
name: lint
description: "JMX 정적 린트. 실행 전 JMeter 시나리오 파일의 조기사망 위험(stopthread+엄격 어설션), 무한루프, 파라미터 기본값 누락, 상대경로 에셋을 검사. 'jmx 점검', 'lint', '부하 전 검사' 등에서 사용. 프로젝트 루트에 src/jmeter/*.jmx가 있을 때 동작."
---

# JMX Lint

JMeter 시나리오 실행 전 정적 검사. 실행은 하지 않는다 — smoke(고빈도, 런타임)와 상호보완적으로 **저빈도 조기사망 함정**을 파일만 보고 찾는다.

## 실행

```bash
# 단일 파일
python3 "$(dirname "$0")/analyze_jmx.py" src/jmeter/<시나리오>.jmx

# 프로젝트 전체
for f in src/jmeter/*.jmx; do
  echo "== $f"; python3 .../analyze_jmx.py "$f" || true
done
```

(`...`는 이 스킬 디렉토리 경로 — fixtures/analyze_jmx.py가 같은 디렉토리에 있다)

## 판정

- BLOCKER: stopthread 그룹의 엄격 어설션 중 실증적으로 조기사망을 일으킨 형태 — 선택적 리소스 엔드포인트(image/asset 등)의 단일값 응답코드 어설션, 배열 인덱스(`$[0].x`) JSONPath 존재 강제. 실행 전 수정 권고(수정 템플릿이 출력에 포함)
- RISK: 그 외 단일값 응답코드/JSONPath 존재 강제(스키마 고정 API는 실증상 무해), 무한루프/기본값 누락/상대경로 — 확인 후 진행

## 근거 사례

- 2-3: 인트로 이미지 404(활성 이미지 부재)가 매 iteration 실패 → 전 스레드 1회 만에 종료 (56s)
- 3-2: 검색 빈 결과 0.2% 빈도로 JSONPath 실패 → 스레드 17→3 누적 소진. 짧은 smoke로는 탐지 불가

## 픽스처

`fixtures/2-3-pre.jmx`, `fixtures/3-2-pre.jmx` — 위 사례의 수정 전 원본(ecoai-gwageo 커밋 스냅숏). BLOCKER 1건(exit=1)이 나와야 정상이며, 스크립트 회귀 점검용 도그푸드 케이스다.
