---
name: product-planning-dr-pipeline
description: "Turn a GUI, web, or app product idea or early planning material into staged Deep Research artifacts: benchmark research, scoped feature extraction, screen design, technology selection, and execution-ready AI agent documentation. Use when planning a screen-based digital product, converting exploratory research into an MVP plan, or generating AGENTS.md, CONTEXT.md, ROADMAP.md, and DESIGN.md from validated planning outputs."
---

# Product Planning Deep Research Pipeline

## Purpose

제품 아이디어 또는 초기 기획 자료를 단계별 Deep Research 산출물로 발전시키고,
마지막에는 Codex 또는 다른 AI 개발 Agent가 바로 실행할 수 있는 문서 세트로 압축
변환한다.

각 단계는 이전 단계의 병합본만 입력으로 사용한다. 조사 보고서를 그대로 누적하지
말고, 다음 단계의 의사결정에 필요한 정보만 남긴다.

## When to Use

- 신규 GUI, 웹, 앱 제품의 시장 조사부터 MVP 개발 계획까지 연결해야 할 때
- 여러 모델 또는 연구자의 결과를 하나의 기준본으로 병합해야 할 때
- 초기 아이디어에서 기능 범위, IA, 화면 요구사항, 기술 결정을 순차 도출할 때
- 기획 보고서를 AI 개발 Agent용 실행 문서로 변환해야 할 때

이미 확정된 작은 기능의 구현 계획이나 단순 기술 비교에는 이 전체 파이프라인을
사용하지 않는다.

이 파이프라인은 화면 기반 제품을 전제로 한다. CLI, API, 백엔드 서비스, daemon처럼
화면이 핵심 인터페이스가 아닌 제품에는 그대로 적용하지 않는다.

## Inputs

시작 전에 다음 입력을 수집하고 누락 항목은 `미정`으로 명시한다.

- 제품 한 줄 정의
- 해결할 문제와 목표 사용자
- 초기 아이디어, 메모, 인터뷰, 기존 기획 자료
- 반드시 포함할 기능과 명시적 제외 범위
- 일정, 예산, 조직, 규제, 운영 제약
- 기존 저장소 또는 기술 제약
- 참고 제품, 경쟁사, 외부 자료
- 결과물을 저장할 작업 디렉터리

제품 한 줄 정의와 MVP 경계를 모든 단계의 상단에 반복해 범위 이탈을 방지한다.

## Output Naming Convention

각 단계는 요청서, 독립 조사본, 병합본 순으로 파일을 만든다.

- Benchmark Research: `01-dr-rq.md`, `01-dr-chatgpt.md`, `01-dr-gemini.md`,
  `01-dr-merge.md`
- Scope Extraction: `02-dr-rq.md`, `02-dr-chatgpt.md`, `02-dr-gemini.md`,
  `02-dr-merge.md`
- Screen Design: `03-dr-rq.md`, `03-dr-chatgpt.md`, `03-dr-gemini.md`,
  `03-dr-merge.md`
- Technology Selection: `04-dr-rq.md`, `04-dr-chatgpt.md`,
  `04-dr-gemini.md`, `04-dr-merge.md`

모델 이름은 조사 채널을 구분하기 위한 기본값이다. 다른 연구자를 사용해도 파일명은
일관성을 위해 유지하거나, 프로젝트 시작 시 하나의 대체 규칙을 정해 전 단계에
동일하게 적용한다.

기본 파일명은 이 스킬의 출력 계약이므로 ChatGPT 또는 Gemini를 실제로 사용하지
않더라도 유지할 수 있다. 파일명을 대체하면 모든 단계와 최종 문서에서 같은 조사
채널 이름을 사용한다.

독립 조사본 생성 방식을 프로젝트 시작 시 정한다.

- 하위 Agent 또는 서로 격리된 세션을 실행할 수 있으면 동일 요청서를 독립적으로
  전달하고, 서로의 결과를 보지 못하게 한 뒤 각 파일에 저장한다.
- 독립 실행이 불가능하면 사용자가 별도 모델 세션에서 요청서를 실행해 결과 파일을
  제공한다.
- 단일 조사 채널만 가능하면 병합본에 해당 제한과 추가 검증 필요성을 기록한다.

실행 환경에서 가능한 조사 채널과 격리 방식을 먼저 감지하고 가장 독립성이 높은
방식을 자동 선택한다. 감지할 수 없거나 외부 유료 호출처럼 사용자 결정이 필요한
경우에만 조사 채널 수와 실행 방식을 확인한다.

최종 Agent 문서는 다음 이름을 사용한다.

- `AGENTS.md`
- `CONTEXT.md`
- `ROADMAP.md`
- `DESIGN.md`

## Pipeline Stages

### 0. Initialize

1. 별도 작업 디렉터리를 만든다.
2. 입력 자료를 읽고 제품 정의, 목표 사용자, MVP 경계, 제약을 고정한다.
3. 알 수 없는 사실과 검증이 필요한 가정을 분리한다.
4. 각 단계의 완료 조건과 다음 단계 입력 조건을 선언한다.
5. 조사 채널 수, 격리 방식, 출력 파일명을 기록한다.

### 1. Benchmark Research

`templates/01-benchmark-rq.md`를 사용해 `01-dr-rq.md`를 만든다.

- 경쟁 및 유사 솔루션을 조사한다.
- 시장, 핵심 기능, UX, IA, 운영 패턴을 비교한다.
- 관찰된 사실, 해석, 제품 적용 제안을 분리한다.
- 출처와 확인 날짜를 기록한다.
- 기준본과 보강본을 병합해 `01-dr-merge.md`를 만든다.

완료 조건: 후속 기능 범위 판단에 필요한 패턴, 차별화 기회, 주의점이 근거와 함께
요약되어 있다.

### 2. Scope Extraction

`templates/02-scope-extraction-rq.md`를 사용해 `02-dr-rq.md`를 만든다.
입력은 `01-dr-merge.md`와 고정된 제품 정의다.

- 벤치마킹 기능을 복제하지 말고 제품 문제에 필요한 기능만 추출한다.
- 각 기능을 `MVP`, `1차 고도화`, `후순위`, `제외`로 분리한다.
- 사용자 가치, 제품 적합성, 의존성, 구현 복잡도, 운영 비용을 판단 근거로 쓴다.
- 병합 결과를 `02-dr-merge.md`로 만든다.

완료 조건: MVP 기능마다 포함 이유, 제외 경계, 핵심 수용 기준이 있고 후순위 항목이
MVP에 섞이지 않는다.

### 3. Screen Design

`templates/03-screen-design-rq.md`를 사용해 `03-dr-rq.md`를 만든다.
입력은 `02-dr-merge.md`의 MVP 범위다.

- IA, 메뉴 구조, 화면 목록, 사용자 흐름을 정의한다.
- 화면별 목적, 진입점, 주요 동작, 데이터, 상태, 오류, 권한 요구사항을 정의한다.
- MVP 기능과 화면 간 추적성을 유지한다.
- 병합 결과를 `03-dr-merge.md`로 만든다.

완료 조건: 모든 MVP 기능이 하나 이상의 흐름 또는 화면에 연결되고, 화면 구현자가
핵심 상태와 동작을 추측하지 않아도 된다.

### 4. Technology Selection

`templates/04-tech-selection-rq.md`를 사용해 `04-dr-rq.md`를 만든다.
입력은 `03-dr-merge.md`, 저장소 제약, 팀 역량이다.

- 프론트엔드, UI, 상태관리, 폼, 테이블, 권한, 관측성, 문서 뷰어 등을 결정한다.
- 각 결정에 요구사항, 선택안, 대안, 근거, 위험, 검증 방법을 기록한다.
- 화면설계가 요구하지 않는 백엔드, 인프라, 런타임 전체 아키텍처는 확정하지 않는다.
- 병합 결과를 `04-dr-merge.md`로 만든다.

완료 조건: MVP 화면 구현에 필요한 기술 결정은 실행 가능하며, 불확실한 결정은
실험 또는 보류 항목으로 분리되어 있다.

### 5. Agent Documentation

`04-dr-merge.md`를 그대로 복사하지 않는다. 네 개 병합본의 결정 사항을 개발 Agent가
작업할 수 있도록 압축 변환한다.

- `templates/AGENTS.template.md`를 기반으로 `AGENTS.md`를 만든다.
- `templates/CONTEXT.template.md`를 기반으로 `CONTEXT.md`를 만든다.
- `templates/ROADMAP.template.md`를 기반으로 `ROADMAP.md`를 만든다.
- `templates/DESIGN.template.md`를 기반으로 `DESIGN.md`를 만든다.

템플릿 구조를 유지하되 제품에 해당하지 않는 항목은 `해당 없음`과 이유를 기록한다.
각 문서는 다음 역할을 갖는다.

- `AGENTS.md`: 작업 규칙, 범위 게이트, 검증 명령, 문서 우선순위
- `CONTEXT.md`: 제품 정의, 사용자, 문제, MVP, 제약, 결정, 미해결 질문
- `ROADMAP.md`: 결과 중심 단계, 의존성, 완료 조건, 후순위
- `DESIGN.md`: 제품 전용 시각 및 상호작용 구현 규칙

완료 조건: Agent가 보고서를 다시 해석하지 않고도 다음 구현 작업을 선택하고,
범위를 지키며, 완료 여부를 검증할 수 있다.

## Merge Rules

각 단계의 병합 시 다음 순서를 지킨다.

1. 기준본과 보강본을 먼저 정한다.
2. 기준본의 구조와 논리 흐름을 우선 유지한다.
3. 보강본에서는 근거가 있거나 실행 가능성을 높이는 디테일만 선별한다.
4. 중복, 모순, 과도하게 단정적인 표현을 제거한다.
5. 범위를 초과한 기술 또는 기능은 후순위나 제외 항목으로 이동한다.
6. 다음 단계 입력에 필요한 내용으로 압축한다.
7. 출처가 불명확한 수치, 라이선스, 시장 점유율은 확정 표현으로 쓰지 않는다.
8. 충돌을 임의로 숨기지 말고 `결정`, `보류`, `추가 검증`으로 분류한다.

첫 번째 조사본을 기본 기준본으로 사용한다. 다른 조사본의 근거 충실도, 구조
완결성, 제품 적합성이 명확히 더 높으면 기준본을 바꿀 수 있으며 선택 근거를
병합본에 기록한다.

병합본에는 최소한 다음을 포함한다.

- 제품 정의와 현재 단계 범위
- 핵심 결정과 근거
- 채택하지 않은 제안과 이유
- 불확실성 및 추가 검증 항목
- 다음 단계에 전달할 입력 요약

각 요청서 템플릿의 `Expected Merge Structure`를 사용해 병합본의 공통 구조를
유지한다.

## Feedback and Iteration Rules

- 후속 단계에서 이전 단계 결정의 오류, 누락, 범위 충돌을 발견하면 진행을 멈춘다.
- 문제가 발생한 이전 단계의 병합본을 최소 범위로 수정한다.
- 수정 이유, 영향받는 결정과 ID, 다시 검증할 후속 산출물을 병합본에 기록한다.
- 수정된 병합본의 완료 조건을 재검증한 뒤 영향받는 후속 단계만 다시 실행한다.
- 단순 선호 변경으로 이전 범위를 넓히지 않는다.

## Validation Rules

- 각 단계 시작 전 이전 단계 병합본의 존재와 완료 조건을 확인한다.
- 모든 핵심 결론을 `근거 있음`, `가정`, `제안` 중 하나로 구분한다.
- 외부 사실은 출처 URL과 확인 날짜를 기록한다.
- MVP 기능이 화면, 기술 결정, 로드맵까지 추적되는지 확인한다.
- 병합본 내부의 모순, 중복, 미정 항목을 검사한다.
- 최종 Agent 문서가 보고서 설명이 아니라 명령, 제약, 완료 조건을 제공하는지 확인한다.
- `markdownlint-cli2` 또는 사용 가능한 표준 markdown lint 도구로 생성된 Markdown
  전체를 검사한다.
- 최종 파일 트리를 출력하고 누락 파일을 확인한다.
- 완료 응답에 실행한 검증, 결과, 실행 불가 사유를 `Validation Report`로 기록한다.

연구 도구나 인터넷 접근이 없으면 외부 사실을 만들어내지 말고, 해당 항목을
`추가 조사 필요`로 남긴다.

## Scope Control Rules

- 모든 단계에서 제품 정의를 고정한다.
- MVP 범위를 벗어난 기능은 구현 대상으로 넣지 않는다.
- 벤치마크의 기능 수를 제품 완성도의 기준으로 사용하지 않는다.
- 화면설계 단계에서 고해상도 시안이나 구현 세부사항으로 과도하게 확장하지 않는다.
- 기술선정 단계에서 백엔드, 인프라, 런타임 전체 아키텍처를 과도하게 확정하지 않는다.
- 관측성과 테스트 결정은 화면 및 클라이언트 요구사항에 필요한 범위로 제한한다.
- 미정 사항은 추측으로 닫지 말고 검증 작업으로 전환한다.
- 개발 Agent 문서는 보고서가 아니라 실행 규칙이어야 한다.

## Deliverables

표준 이중 조사 채널 실행의 산출물은 최대 20개다.

- 단계별 요청서 4개: `01-dr-rq.md`부터 `04-dr-rq.md`
- 단계별 독립 조사본 최대 8개: `*-dr-chatgpt.md`, `*-dr-gemini.md`
- 단계별 병합본 4개: `01-dr-merge.md`부터 `04-dr-merge.md`
- Agent 문서 4개: `AGENTS.md`, `CONTEXT.md`, `ROADMAP.md`, `DESIGN.md`

독립 조사 채널을 하나만 사용할 수 있으면 누락된 조사본을 빈 파일로 만들지 않는다.
대신 병합본에 단일 조사 채널 사용과 검증 한계를 기록한다.

## Templates

- `templates/01-benchmark-rq.md`: 경쟁 및 유사 솔루션 조사 요청서
- `templates/02-scope-extraction-rq.md`: 제품 기능 범위 추출 요청서
- `templates/03-screen-design-rq.md`: MVP 화면설계 요청서
- `templates/04-tech-selection-rq.md`: 화면 기반 기술선정 요청서
- `templates/AGENTS.template.md`: AI 개발 Agent 작업 규칙
- `templates/CONTEXT.template.md`: 제품 및 결정 컨텍스트
- `templates/ROADMAP.template.md`: 결과 중심 구현 로드맵
- `templates/DESIGN.template.md`: 제품 전용 UI 구현 기준

요청서 템플릿의 대괄호 플레이스홀더를 실제 입력으로 교체한다. 정보가 없으면
삭제하지 말고 `미정` 또는 `추가 조사 필요`로 표시한다.

## Example Workflow

ARAG Studio 형태의 AI 워크플로우 제품을 기획한다면 다음 순서로 실행한다.

1. 아이디어와 초기 자료를 정리하고 `01-dr-rq.md`를 작성한다.
2. 두 개의 독립 조사 결과를 만든 뒤 기준본을 정해 `01-dr-merge.md`로 병합한다.
3. 벤치마크 기능을 제품 목표에 맞춰 분류하고 `02-dr-merge.md`에서 MVP를 잠근다.
4. 잠긴 MVP만 사용해 IA와 화면 요구사항을 `03-dr-merge.md`에 정의한다.
5. 화면 요구사항을 충족하는 최소 기술 결정을 `04-dr-merge.md`에 기록한다.
6. 네 병합본을 실행형 Agent 문서 네 개로 변환한다.
7. 범위 추적성, 파일 구조, markdown lint를 검증한다.

구체적인 예시와 파일 목적은 `examples/arag-studio/README.md`를 참고한다.

## Do / Don't

### Do

- 독립 조사 결과를 비교한 뒤 기준본과 보강본을 명시한다.
- 제품 문제와 MVP 경계를 모든 단계의 판단 기준으로 사용한다.
- 사실, 해석, 제안을 분리한다.
- 불확실성을 명시하고 작은 검증 작업으로 바꾼다.
- 다음 단계가 소비하기 쉬운 형태로 병합본을 압축한다.
- 최종 문서에 명령, 금지사항, 완료 조건, 검증 방법을 쓴다.

### Don't

- 경쟁 제품의 기능 목록을 그대로 제품 범위로 채택하지 않는다.
- 출처 없는 수치나 라이선스 조건을 사실로 단정하지 않는다.
- 후순위 기능을 MVP 화면 또는 구현 로드맵에 숨겨 넣지 않는다.
- 화면설계 전에 기술 스택을 고정하지 않는다.
- `04-dr-merge.md`를 최종 Agent 문서에 그대로 복사하지 않는다.
- 외부 브랜드의 `DESIGN.md`를 복제하지 않는다.

## Final Checklist

- [ ] 제품 정의, 목표 사용자, MVP 경계가 전 단계에서 일관된다.
- [ ] `01`부터 `04`까지 요청서와 병합본이 존재한다.
- [ ] 선택한 조사 채널 수와 실행 방식이 기록되고 해당 조사본이 존재한다.
- [ ] 각 병합본에 기준본, 보강 내용, 제외 내용, 불확실성이 기록되어 있다.
- [ ] 모든 MVP 기능이 화면설계와 로드맵에 추적된다.
- [ ] 기술 결정이 화면 요구사항 및 저장소 제약과 연결된다.
- [ ] 백엔드와 인프라가 근거 없이 과도하게 확정되지 않았다.
- [ ] `AGENTS.md`, `CONTEXT.md`, `ROADMAP.md`, `DESIGN.md`가 실행형 문서다.
- [ ] `DESIGN.md`가 제품 전용 규칙이며 필수 디자인 섹션을 포함한다.
- [ ] 출처 없는 확정 표현과 범위 초과 항목을 제거했다.
- [ ] markdown lint와 파일 트리 검증을 실행했거나 실행 불가 사유를 기록했다.
