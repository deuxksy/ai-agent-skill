# ARAG Studio Example

이 예시는 AI 기반 연구 및 워크플로우 스튜디오 제품 아이디어를
`product-planning-dr-pipeline`으로 발전시키는 방법을 보여준다. 실제 제품 요구사항을
확정하는 문서가 아니라 파이프라인 사용 예시다.

## Starting Brief

- Product definition: 여러 연구 Agent의 작업을 구성, 실행, 검토하는 스튜디오
- Target users: 반복적인 심층 조사를 수행하는 제품 기획자와 연구자
- Core outcome: 사용자가 연구 워크플로우를 만들고 실행 결과와 근거를 검토한다
- Initial boundary: 워크플로우 작성, 실행 상태, 결과/근거 검토에 집중
- Non-goals: 범용 프로젝트 관리, 전체 데이터 플랫폼, 엔터프라이즈 과금

## Example Flow

1. `01-dr-rq.md`에서 AI 연구 도구, 워크플로우 빌더, 관측성 UI를 비교한다.
2. `01-dr-merge.md`에서 반복 패턴과 과잉 기능을 분리한다.
3. `02-dr-merge.md`에서 MVP를 워크플로우 작성, 실행, 결과 검토로 잠근다.
4. `03-dr-merge.md`에서 프로젝트 목록, 워크플로우 편집기, 실행 상세, 근거 뷰를
   정의한다.
5. `04-dr-merge.md`에서 캔버스, 상태관리, 폼, trace UI에 필요한 최소 기술만
   결정한다.
6. 네 병합본을 실행형 `AGENTS.md`, `CONTEXT.md`, `ROADMAP.md`, `DESIGN.md`로
   압축한다.

## Expected Project Output

```text
arag-studio-planning/
├─ 01-dr-rq.md
├─ 01-dr-chatgpt.md
├─ 01-dr-gemini.md
├─ 01-dr-merge.md
├─ 02-dr-rq.md
├─ 02-dr-chatgpt.md
├─ 02-dr-gemini.md
├─ 02-dr-merge.md
├─ 03-dr-rq.md
├─ 03-dr-chatgpt.md
├─ 03-dr-gemini.md
├─ 03-dr-merge.md
├─ 04-dr-rq.md
├─ 04-dr-chatgpt.md
├─ 04-dr-gemini.md
├─ 04-dr-merge.md
├─ AGENTS.md
├─ CONTEXT.md
├─ ROADMAP.md
└─ DESIGN.md
```

## File Purpose Summary

| 파일 | 목적 |
| :--- | :--- |
| `01-dr-rq.md` | 경쟁 및 유사 솔루션 조사 범위와 질문 고정 |
| `01-dr-chatgpt.md` | 첫 번째 독립 벤치마크 조사본 |
| `01-dr-gemini.md` | 두 번째 독립 벤치마크 조사본 |
| `01-dr-merge.md` | 범위 추출에 사용할 벤치마크 기준본 |
| `02-dr-rq.md` | 기능 분류 기준과 MVP 경계 고정 |
| `02-dr-chatgpt.md` | 첫 번째 독립 기능 범위 제안 |
| `02-dr-gemini.md` | 두 번째 독립 기능 범위 제안 |
| `02-dr-merge.md` | 확정 MVP, 후순위, 제외 범위 기준본 |
| `03-dr-rq.md` | 화면설계 범위와 필수 산출물 정의 |
| `03-dr-chatgpt.md` | 첫 번째 독립 IA 및 화면설계안 |
| `03-dr-gemini.md` | 두 번째 독립 IA 및 화면설계안 |
| `03-dr-merge.md` | 구현 기술선정에 사용할 화면설계 기준본 |
| `04-dr-rq.md` | 기술 결정 영역, 제약, 검증 기준 고정 |
| `04-dr-chatgpt.md` | 첫 번째 독립 기술선정안 |
| `04-dr-gemini.md` | 두 번째 독립 기술선정안 |
| `04-dr-merge.md` | 확정, 조건부, 보류 기술 결정 기준본 |
| `AGENTS.md` | 개발 Agent의 작업, 범위, 검증 규칙 |
| `CONTEXT.md` | 제품 정의, MVP, 결정, 가정, 미정 사항 |
| `ROADMAP.md` | 사용자 결과 중심 구현 순서와 완료 조건 |
| `DESIGN.md` | ARAG Studio 전용 UI 및 상호작용 구현 규칙 |

## Template Purpose Summary

| 템플릿 | 목적 |
| :--- | :--- |
| `01-benchmark-rq.md` | 근거 중심 벤치마크 조사 요청서 생성 |
| `02-scope-extraction-rq.md` | 벤치마크에서 제품 범위만 추출 |
| `03-screen-design-rq.md` | 고정 MVP를 IA와 화면 요구사항으로 변환 |
| `04-tech-selection-rq.md` | 화면 요구사항에서 최소 기술 결정 도출 |
| `AGENTS.template.md` | 실행 가능한 개발 Agent 규칙 생성 |
| `CONTEXT.template.md` | 압축된 제품 및 의사결정 컨텍스트 생성 |
| `ROADMAP.template.md` | 결과와 완료 조건 중심 로드맵 생성 |
| `DESIGN.template.md` | 외부 브랜드를 복제하지 않는 제품 전용 디자인 규칙 생성 |

## Scope Guard Example

벤치마크에서 실시간 협업, 마켓플레이스, 과금, 조직 분석 기능이 발견되어도 ARAG
Studio의 초기 제품 정의와 핵심 여정에 필요하지 않으면 `후순위` 또는 `제외`로
분류한다. 화면설계와 기술선정에는 확정 MVP만 전달한다.
