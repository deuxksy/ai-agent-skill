---
name: update-openapi
description: Use when OpenAPI/Swagger 스펙 파일을 최신 버전으로 갱신할 때. 스펙 URL(/v3/api-docs, swagger.json)에서 원문을 받아 기존 파일과 버전·엔드포인트 diff 비교 후 교체. 'openapi 갱신', '스펙 업데이트'에서 사용.
---

# OpenAPI 스펙 갱신

## 개요

프로젝트에 보관 중인 OpenAPI/Swagger 스펙 파일을 API 서버의 최신 원문으로 동기화한다. URL 하나만 받으면 동작하며, 교체 전에 버전·엔드포인트 diff로 변경 범위를 먼저 보고한다.

스펙 URL 탐색: 문서 사이트(swagger-ui) HTML의 `url:` 설정이 실제 스펙을 가리킨다. `/v3/api-docs` 경로가 문서 도메인이 아니라 **API 서버 도메인**에 있는 경우가 많다.

## 절차

1. 인자 수집 (모르면 사용자에게 확인):
   - 스펙 URL — 예: `https://api-dev.example.com/v3/api-docs`
   - 대상 파일 — 기본 `docs/archive/OpenAPI.json`
2. 다운로드 (원문 보존 — 파이프로 가공하지 않고 파일로):

   ```bash
   curl -fsS -m 15 "<URL>" -o /tmp/openapi_new.json
   ```

3. 버전·규모 확인과 기존 파일 diff — 도구는 자유 (아래는 예시):

   ```bash
   # 버전
   grep -o '"version":"[^"]*"' /tmp/openapi_new.json | head -1
   # 엔드포인트 키 diff (jq 있으면)
   diff <(jq -r '.paths|keys[]' <대상파일> | sort) <(jq -r '.paths|keys[]' /tmp/openapi_new.json | sort)
   ```

   minified JSON이면 `grep -o '"/[^"]*":{'` 근사 추출도 가능하다. 정밀 diff가 필요하면 `python3 -c` 한 줄로.
4. diff(버전 상승·엔드포인트 증감)를 사용자에게 보고하고 교체 승인을 받는다.
5. 교체: `mv /tmp/openapi_new.json <대상파일>`
6. 커밋:

   ```text
   chore: OpenAPI.json v0.10.63->v0.10.92 갱신 — <URL> 원문 (paths N, 엔드포인트 증감 X)
   ```

## 규칙

- 원문 바이트를 그대로 저장한다 (재직렬화 금지 — 서버 스펙과 바이트 일치).
- 버전이 동일하면 교체하지 않는다.
- diff 출력의 추가/삭제 엔드포인트는 기존 테스트 시나리오(Talend/JMX) 대상 영향 검토에 활용한다.
