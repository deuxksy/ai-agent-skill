# Repository Common Rules (.ai/RULES.md)

This document serves as the Single Source of Truth (SSoT) for all runtime AI agents working in this repository.

## Project Overview

- **Project**: `zzizily` — Personal automation AI Agent Skill marketplace providing 10 domain plugins.
- **Repository**: `deuxksy/ai-agent-skill`
- **Unified Version**: `1.12.0`
- **Author**: Crong (kyolim)

## Versioning & Commit Convention

- **SemVer**: Follow Semantic Versioning (`1.12.0`). All plugin manifests (`.claude-plugin/marketplace.json`) and catalog tables must stay in sync.
- **Conventional Commits**: Commit tag in English (e.g. `feat`, `fix`, `docs`, `chore`), commit message in Korean.

## Core Guidelines

1. **Runtime Neutrality**: Skills must remain runtime-neutral and cross-compatible across Claude, Gemini/Antigravity, and Codex.
2. **SKILL.md Specification**: Every skill folder under `plugins/<domain>/` must contain a `SKILL.md` with standard YAML frontmatter:
   ```yaml
   ---
   name: <skill-name>
   description: <one-line summary>
   ---
   ```
3. **No Hardcoded Secrets/Paths**: Never commit credentials, personal absolute paths, or unverified environment configurations.
