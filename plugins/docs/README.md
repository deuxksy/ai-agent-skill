# docs

Runtime-neutral AI Agent skills for auditing, structuring, and updating repository `README.md` files and documentation hierarchy based on the Diátaxis framework, OKF standards, and orphan document detection.

## Skills

- `docs-md-management`: Audits `README.md` and overall project documentation under `docs/`, verifies 100~500 char summary, builds Diátaxis document indexes, verifies sub-hubs, and detects orphan docs.
- `revise-readme-md`: Lightly updates `README.md` index and summary when new documentation or features are added.

## Claude Code

```bash
claude plugin install docs@zzizily
```

호출:

```text
/docs:docs-md-management
/docs:revise-readme-md
```
