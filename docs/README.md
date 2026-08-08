# Documentation Hub (`docs/`)

본 디렉토리는 `ai-agent-skill` 프로젝트의 하위 문서 및 규격을 체계적으로 정리하는 서브 문서 허브입니다.

---

## 📁 디렉토리 구조 및 역할 정의

```text
docs/
├── README.md                      # [Sub-Hub] docs/ 하위 디렉토리 역할 및 문서 체계 정의
├── archive/                       # [Reference Archive] 직접 관리하지 않는 참조 기획 문서(화면설계서, 요구서), API 명세(openapi.json, swagger.json), Figma 토큰 등
├── okf/
│   └── README.md                  # [OKF Hub] OKF 명세 문서 허브 및 Diátaxis 작성 가이드
└── superpowers/                   # [Internal Agent Workspace]
    ├── specs/                     # AI Agent 디자인 스펙 (README 인덱싱 대상 제외)
    └── plans/                     # AI Agent 실행 계획 (README 인덱싱 대상 제외)
```

---

## 🧭 문서 작성 표준

- **Diátaxis 프레임워크**: 모든 사용자의 행동 및 목적 중심 문서 분류 적용 ([`docs/okf/README.md`](./okf/README.md) 참조)
- **OKF 표준**: `docs/okf/` 하위 명세 문서는 OKF 최신 가이드라인에 맞추어 `docs/okf/README.md` 내에서 인덱싱 관리
