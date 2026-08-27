# AGENTS.md

> **[IMPORTANT]** Before starting work in this repository, read `.ai/RULES.md` for shared repository rules, commit conventions, and core guidelines.

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## 프로젝트 개요

**zzizily** — 10개 독립 도메인 플러그인을 통합 제공하는 개인 자동화 AI Agent Skill 마켓플레이스.

- Author: Crong (kyolim)
- GitHub Repository: `deuxksy/ai-agent-skill`
- 통합 버전: `1.15.0`

## 구조

```
.
├── .claude-plugin/
│   └── marketplace.json     # 10개 전체 도메인 플러그인 등록 마켓플레이스 (v1.15.0)
├── agents/                  # AI 에이전트 지침 및 어댑터
└── plugins/
    ├── security/            # 코드/시스템 보안 감사
    ├── infra/               # 인프라 프로비저닝
    ├── trackers/            # 자동화/트래커
    ├── sessions/            # 세션 워크플로우
    ├── l10n/                # 콘텐츠/번역
    ├── git/                 # Git 워크플로우
    ├── rules/               # 에이전트 지침 관리
    ├── docs/                # README 및 문서 관리
    ├── review/              # 교차 검증
    ├── dev/                 # 빌드/배포
    └── meridian/            # 원격 미디어 파이프라인 (마켓 미등록·로컬 전용)
```

## 개발 명령

플러그인 자체는 빌드/테스트 과정이 없음. Skill 파일(SKILL.md)을 직접 편집 후 커밋.

새 Skill 추가 시:
1. `plugins/<domain-name>/<skill-name>/SKILL.md` 생성
2. `.claude-plugin/marketplace.json` 해당 도메인 플러그인 메타데이터 확인 및 동기화
