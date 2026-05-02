---
name: security-audit
description: "Daily security vulnerability and update check across multiple package managers. Cross-platform support for macOS (Homebrew), Fedora/Debian/Arch Linux (dnf/apt/pacman), and language-specific managers (mise, uv, pnpm, pip, npm, nix). Use when running scheduled security audits, checking for CVEs and package updates, creating or updating security audit cron jobs, or user asks about package security or vulnerabilities. Optimized with 2-phase approach: built-in audit tools first, then targeted web search only for outdated packages."
---

# Security Audit

Cross-platform security vulnerability and update checker.

## Quick Start

```bash
# Collect all versions first, then run built-in audits, then targeted web search
# See references/workflow.md for complete procedure
```

## Workflow

Follow the complete procedure in [references/workflow.md](references/workflow.md). Summary:

1. **OS/Distro detect** → auto-select system package manager
2. **Version collect** → all installed package versions
3. **Phase 1: Built-in audit** → `brew audit`, `npm audit`, `pip-audit`, `dnf updateinfo`
4. **Phase 2: Targeted web search** → only for outdated packages not caught by Phase 1
5. **CVE validation** → verify affected version range against installed version before reporting

## Package Manager Priority

1. mise
2. uv tool
3. pnpm
4. Homebrew (if installed)
5. pip
6. npm
7. nix (if installed)
8. System package manager (auto-detected: dnf/apt/pacman)

## Response Format

See [references/response-format.md](references/response-format.md) for Telegram card format templates.

## Key Rules

- **No false positives**: CVE must affect installed version range (semver check)
- **No redundant searches**: skip packages already flagged by built-in audit
- **No version-stable packages**: skip packages with no available updates
- **Include action URL**: always provide NVD/GHSA link + fix command
- **Report in Korean**
