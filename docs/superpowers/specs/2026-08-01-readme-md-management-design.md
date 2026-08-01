# Design Spec: `readme-md-management` Plugin & Skills

- **Date**: 2026-08-01
- **Status**: Draft (Approved Design)
- **Author**: Antigravity & User

---

## 1. Overview & Purpose

`readme-md-management`는 리포지토리의 `README.md` 및 문서 계층 구조를 Audit, 생성, 갱신 관리하는 런타임 중립 AI Agent 플러그인입니다.

### Core Objectives
1. **사람을 위한 프로젝트 요약**: `README.md` 상단에 사람이 직관적으로 이해할 수 있는 100자 내외(핵심 1문장) ~ 500자 이하(종합 요약) 프로젝트 목표 및 소개를 작성 및 검증합니다.
2. **Diátaxis 기반 Document Indexing**: 리포지토리 내 마크다운 문서를 Diátaxis 4분면 체계(Tutorials, How-To Guides, Reference, Explanation)로 분류하고 1줄 설명과 상대 링크를 제공합니다.
3. **계층적 문서 허브(Documentation Hierarchy) 구조 지원**:
   - Root `README.md`: 프로젝트 전체 요약 및 최상위 Diátaxis 문서 인덱스
   - `docs/README.md`: `docs/` 하위 폴더들(`okf/`, `superpowers/` 등)의 역할과 구조를 정의하는 서브 허브 문서
   - `docs/okf/README.md`: OKF 최신 버전 명세 문서들의 자체 인덱스 관리 문서
   - `docs/superpowers/`: AI Agent 작업용 내부 문서(`specs/`, `plans/`)로, 인덱싱 및 고아 검사에서 제외
4. **고아 페이지 (Orphan Pages) & Stale Link Audit**: 허브 문서 어디에도 링크되지 않아 방치된 마크다운 문서 및 깨진 상대 링크를 자동 탐지하여 보고합니다.

---

## 2. Documentation Hierarchy Definition

```text
Repository Root/
├── README.md                      # [Root Hub] 요약 (100~500자) + Diátaxis 최상위 문서 Index
└── docs/
    ├── README.md                  # [Sub-Hub] docs/ 하위 폴더(okf, superpowers 등) 역할 정의 및 설명
    ├── okf/
    │   ├── README.md              # [OKF Hub] docs/okf/ 하위 OKF 최신 명세 문서 자체 인덱스
    │   └── ...                    # OKF 명세 문서들
    └── superpowers/               # [Internal Agent Workspace]
        ├── specs/                 # Agent 디자인 스펙 (README 인덱스 대상 제외)
        └── plans/                 # Agent 실행 계획 (README 인덱스 대상 제외)
```

### Audit & Indexing Rules
- **Root `README.md`**: `docs/README.md`, `docs/okf/README.md` 및 주요 유저/개발자 문서를 Diátaxis 4분면으로 인덱싱.
- **`docs/README.md`**: `docs/okf/`, `docs/superpowers/` 등 하위 디렉토리의 용도와 구성을 정의.
- **`docs/okf/README.md`**: OKF 표준 명세 개별 파일 목록을 자체 관리.
- **`docs/superpowers/`**: AI Agent 내부 산출물이므로 `README.md` 및 `docs/okf/README.md` 인덱싱 및 고아 페이지 검사 대상에서 **제외(Exclude)**.

---

## 3. Plugin Architecture & File Structure

```text
plugins/readme-md-management/
├── README.md                      # 플러그인 안내 문서
├── .claude-plugin/
│   └── plugin.json                # Claude Code 플러그인 매니페스트
├── .codex-plugin/
│   └── plugin.json                # Codex/Agents 플러그인 매니페스트
└── skills/
    ├── readme-md-management/
    │   ├── SKILL.md               # 메인 Audit, 요약 생성, Diátaxis Indexing & Orphan Audit 스킬
    │   └── references/
    │       ├── diataxis-spec.md   # Diátaxis 4분면 분류 규칙 및 가이드라인
    │       └── okf-spec.md        # OKF 명세 및 docs/okf 서브 허브 검사 가이드라인
    └── revise-readme-md/
        └── SKILL.md               # 문서/기능 변경 시 README.md 경량 갱신 스킬
```

---

## 4. Detailed Skill Workflows

### 4.1. `readme-md-management` Skill Workflow

1. **Discovery (탐색 및 파일 분류)**
   - Root `README.md`, `docs/README.md`, `docs/okf/README.md` 존재 확인
   - `docs/` 이하 및 리포지토리 내 마크다운 스캔
   - **제외 대상**: `.git`, `node_modules`, `dist`, `build`, `docs/superpowers/`, `.ai/`, `.claude/`, `.gemini/`
2. **Project Goal & Summary Audit**
   - Codebase 및 기존 문서 분석
   - 100자 내외 핵심 1문장 목표 작성/점검
   - 500자 이하 종합 요약 작성/점검 (100~500자 범주 엄격 준수)
3. **Diátaxis 4-Quadrant Indexing**
   - 탐색된 유효 마크다운 문서를 Diátaxis 기준 분류:
     - **Tutorials**: `getting-started.md`, `quickstart.md`, 입문용 가이드
     - **How-To Guides**: `deployment.md`, `contributing.md`, 실무/작업 가이드
     - **Reference**: `docs/README.md`, `docs/okf/README.md`, API 명세, CLI 참조
     - **Explanation**: `architecture.md`, `concepts.md`, 디자인/배경 설명
   - 각 링크는 상대 경로 (`[문서 제목](./path/to/doc.md)`) 및 1줄 설명 포함
4. **Orphan Page & Stale Link Detection**
   - 기존 `README.md` 내 깨진 상대 링크(Stale Link) 탐지
   - 적절한 허브 문서(`README.md`, `docs/README.md`, `docs/okf/README.md`)에 링크되어 있지 않은 마크다운 파일을 고아 페이지(Orphan Page)로 감지하고 적절한 카테고리 추천
5. **Quality Report & Approval Gate**
   - 발견 파일 수, 요약 글자수, Diátaxis 인덱스 diff, 고아 페이지 목록 보고
   - 사용자 명시적 승인 전 파일 생성/수정 금지

### 4.2. `revise-readme-md` Skill Workflow

- 신규 기능/문서 추가 후 `README.md` 경량 갱신:
  - 100~500자 요약 유효성 재확인
  - 신규 문서의 Diátaxis 카테고리 판별 및 `README.md` (또는 `docs/okf/README.md`) 해당 섹션에 Hunk 단위 diff 제안
  - 기존 커스텀 섹션(뱃지, 설치법, 라이선스 등)은 보존

---

## 5. Safety & Quality Criteria

1. **Surgical Edits Only**: `README.md` 전체를 새로 쓰지 않고, 요약 및 Index 섹션만 정교하게 수정/갱신.
2. **Symlink / Non-Git Safety**: Symlink 대상 파일 수정 금지, Non-Git 환경 시 검사 한계 명시.
3. **No Secret Leakage**: 절대경로, 로컬 환경 변수, 개인 토큰이 문서에 유출되지 않도록 검증.
4. **Approval Gate**: 사용자 승인 없이 파일 내용을 변경하지 않음.

---

## 6. Verification Plan

1. **Diátaxis Classification Test**: 다양한 마크다운 문서 샘플에 대해 4분면 분류가 정확한지 확인.
2. **Summary Length Constraint Test**: 100자 내외 요약 및 500자 이하 글자수 제약 충족 검증.
3. **Orphan Detection Test**: 링크되지 않은 마크다운 파일 추가 후 고아 페이지로 정상 탐지되는지 확인 (`docs/superpowers/` 제외 확인).
4. **Link Drift Test**: 존재하지 않는 문서 링크 작성 시 Stale Link 경고 출력 확인.
