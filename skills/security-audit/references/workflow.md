# Security Audit Workflow

## Step 0: OS/Distro Detection

```bash
uname -s && uname -m
cat /etc/os-release 2>/dev/null | grep -E '^(ID|ID_LIKE)='
```

### brew path
- Darwin → `/opt/homebrew/bin`
- Linux → `/home/linuxbrew/.linuxbrew/bin`

### System package manager (auto-select by ID)

| ID / ID_LIKE | Manager | Audit | Update check | List installed |
|---|---|---|---|---|
| `fedora` / `rhel` | dnf | `dnf updateinfo list security` | `dnf check-update --security` | `dnf list installed` |
| `debian` / `ubuntu` | apt | `apt list --upgradable 2>/dev/null` | `apt list --upgradable` | `dpkg -l` |
| `arch` / `manjaro` | pacman | none (rolling release) | `checkupdates` | `pacman -Q` |
| Darwin | none | `softwareupdate --list` | `softwareupdate --list` | N/A |

### Common PATH

```bash
export PATH="/opt/homebrew/bin:/home/linuxbrew/.linuxbrew/bin:/nix/var/nix/profiles/default/bin:$HOME/.local/bin:$HOME/.local/share/mise/shims:$PATH"
```

**Skip non-existent commands**: `which <cmd> >/dev/null 2>&1` before running.

---

## Step 1: Version Collection

Collect exact installed versions from all available managers:

| Manager | Command |
|---|---|
| mise | `mise list` |
| uv | `uv tool list` |
| pnpm | `pnpm list -g --depth=0` |
| Homebrew | `brew list --formula --versions` |
| pip | `pip list --format=json` |
| npm | `npm list -g --depth=0 --json` |
| nix | `nix profile list` |
| System | `dnf list installed` / `dpkg -l` / `pacman -Q` |

---

## Step 2: Phase 1 — Built-in Security Audit

Run all available built-in audit tools (fast, authoritative):

- `brew audit` (Homebrew)
- `npm audit` (npm, project lockfile only, not global)
- `pip-audit` or `safety check` (pip, if installed)
- `dnf updateinfo list security` (Fedora)

**No built-in audit**: mise, uv tool, pnpm global, nix, pacman → proceed to Phase 2.

---

## Step 3: Phase 2 — Targeted Web Search

### Step 3A: Filter by Outdated Packages

Only search CVEs for packages with available updates. Already-latest packages likely have patches applied.

| Manager | Command |
|---|---|
| mise | `mise outdated` |
| uv | `uv tool list --outdated` |
| pnpm | `pnpm outdated -g` |
| Homebrew | `brew outdated` |
| pip | `pip list --outdated` |
| npm | `npm outdated -g` |
| System | `dnf check-update --security` / `apt list --upgradable` / `checkupdates` |
| nix | Compare collected version vs latest |

### Step 3B: CVE Search (outdated packages only)

- **Skip** packages already flagged in Phase 1 (dedup)
- **Skip** packages with no updates (not outdated)
- Batch queries for efficiency: `[pkg1] [pkg2] CVE vulnerability`
- Search source: GitHub Security Advisories

### Step 3C: NVD Detail (only when CVE found)

- Fetch affected version range from NVD (https://nvd.nist.gov/vuln/detail/[CVE-ID])
- No CVE found → just report as update available

---

## Step 4: CVE Validation (all phases)

**Critical rule**: CVE must affect the installed version range.

1. Get affected versions from CVE/Advisory
2. Compare with installed version (semver)
3. Outside range → **ignore, do not report**
4. Inside range → **report**

Examples:
- CVE affects `<= 2.3.1`, installed is `2.4.0` → **skip**
- CVE affects `>= 1.0.0, < 3.0.0`, installed is `2.5.0` → **report**

---

## Step 5: Report

See response-format.md for templates. Update check data is already collected in Steps 1-3, do not re-run.
