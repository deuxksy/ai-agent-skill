"""Preview and replace user databases between SQLite and Cloudflare D1."""
import argparse
import hashlib
import os
import sqlite3
import tempfile
import tomllib
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import d1


@dataclass(frozen=True)
class Snapshot:
    schema: tuple[tuple[str, str, str], ...]
    counts: dict[str, int]
    fingerprint: str
    data_fingerprint: str


def inspect(db: sqlite3.Connection, sql: Path) -> Snapshot:
    schema = tuple(db.execute("""
        SELECT type, name, sql FROM sqlite_schema
        WHERE name NOT GLOB 'sqlite_*' AND name <> '_cf_KV' AND sql IS NOT NULL
        ORDER BY type, name
    """))
    counts = {
        name: db.execute(f"SELECT COUNT(*) FROM {d1.identifier(name)}").fetchone()[0]
        for kind, name, _ in schema if kind == "table"
    }
    with sql.open("rb") as handle:
        fingerprint = hashlib.file_digest(handle, "sha256").hexdigest()
    content = hashlib.sha256()
    for name in counts:
        rows = db.execute(f"SELECT * FROM {d1.identifier(name)}")
        row_hashes = sorted(hashlib.sha256(repr(row).encode("utf-8")).digest() for row in rows)
        content.update(name.encode("utf-8") + b"\0")
        for row_hash in row_hashes:
            content.update(row_hash)
    return Snapshot(schema, counts, fingerprint, content.hexdigest())


def snapshot_local(path: Path, destination: Path) -> Snapshot:
    if not path.is_file():
        raise FileNotFoundError(path)
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as source:
        with closing(sqlite3.connect(":memory:")) as copy:
            source.backup(copy)
            with destination.open("w", encoding="utf-8") as handle:
                for statement in copy.iterdump():
                    handle.write(statement + "\n")
            snapshot = inspect(copy, destination)
            exported = inspect_sql(destination)
            if snapshot != exported:
                raise ValueError("SQLite data cannot be represented faithfully by this SQL export.")
            return snapshot


def load_sql(db: sqlite3.Connection, source_sql: Path) -> Snapshot:
    db.executescript(source_sql.read_text(encoding="utf-8"))
    if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
        raise ValueError("SQLite integrity check failed")
    if db.execute("PRAGMA foreign_key_check").fetchone():
        raise ValueError("SQLite foreign key check failed")
    return inspect(db, source_sql)


def inspect_sql(source_sql: Path) -> Snapshot:
    with closing(sqlite3.connect(":memory:")) as db:
        return load_sql(db, source_sql)


def restore_local(source_sql: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target.parent) as directory:
        pending = Path(directory) / "replacement.db"
        with closing(sqlite3.connect(pending)) as db:
            load_sql(db, source_sql)
        for suffix in ("-wal", "-shm", "-journal"):
            if target.with_name(target.name + suffix).exists():
                raise ValueError("SQLite sidecar exists. Stop applications using the target database.")
        os.chmod(pending, target.stat().st_mode & 0o777 if target.exists() else 0o600)
        pending.replace(target)


def capture(local: Path, remote: str, directory: Path, *, allow_missing: bool) -> tuple[Snapshot | None, Snapshot]:
    directory.mkdir(mode=0o700)
    local_state = None
    if not allow_missing or local.exists():
        local_state = snapshot_local(local, directory / "local.sql")
    remote_sql = directory / "d1.sql"
    d1.export(remote, remote_sql)
    return local_state, inspect_sql(remote_sql)


def run(config_path: Path, direction: str) -> int:
    config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    account = config.get("d1_account_id")
    if not isinstance(account, str) or not account or os.environ.get("CLOUDFLARE_ACCOUNT_ID") != account:
        raise ValueError("Set CLOUDFLARE_ACCOUNT_ID to the configured d1_account_id before running.")
    pairs = [
        ((config_path.parent / Path(row["local_path"]).expanduser()).resolve(), row["d1_database"])
        for row in config["databases"]
    ]
    if not pairs or any(not isinstance(remote, str) or not remote.strip() or remote.startswith("-")
                        for _, remote in pairs):
        raise ValueError("Configure at least one valid database pair.")
    if any(len(set(values)) != len(pairs) for values in zip(*pairs)):
        raise ValueError("Each local path and D1 database must be unique.")

    push = direction == "local-to-d1"
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        previews = []
        for index, (local, remote) in enumerate(pairs):
            directory = root / f"preview-{index}"
            left, right = capture(local, remote, directory, allow_missing=not push)
            previews.append((left, right))
            print(f"{local} {'→' if push else '←'} D1 {remote}")
            local_counts = left.counts if left else {}
            if left is None:
                print("  Local database does not exist and will be created.")
            for table in sorted(local_counts.keys() | right.counts.keys()):
                print(f"  {table}: Local {local_counts.get(table, 'missing')} / D1 {right.counts.get(table, 'missing')}")
        print("Equal counts do not guarantee equal data.")
        if not push:
            print("Stop applications using the local databases before restoring.")
        if input("Overwrite the targets shown above? Type yes to proceed: ") != "yes":
            return 0

        for index, (local, remote) in enumerate(pairs):
            if capture(local, remote, root / f"current-{index}", allow_missing=not push) != previews[index]:
                raise ValueError("A source or target changed. Run again to review the new counts.")

        backup_root = config_path.parent / "sqlite-d1-backups"
        backup_root.mkdir(mode=0o700, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        backups = Path(tempfile.mkdtemp(prefix=f"{stamp}-", dir=backup_root))
        for index in range(len(pairs)):
            target_file = "d1.sql" if push else "local.sql"
            saved = root / f"current-{index}" / target_file
            if saved.exists():
                (backups / f"{index + 1}-{target_file}").write_bytes(saved.read_bytes())
            else:
                (backups / f"{index + 1}-local-missing.txt").write_text(str(pairs[index][0]) + "\n")
        print(f"Target backups: {backups}")

        for index, (local, remote) in enumerate(pairs):
            directory = root / f"current-{index}"
            target = f"D1 {remote}" if push else str(local)
            source = previews[index][0 if push else 1]
            try:
                if push:
                    d1.replace(remote, directory / "local.sql", directory / "d1.sql")
                    d1.export(remote, directory / "verified.sql")
                    actual = inspect_sql(directory / "verified.sql")
                else:
                    restore_local(directory / "d1.sql", local)
                    actual = snapshot_local(local, directory / "verified.sql")
                if (source.schema, source.counts, source.data_fingerprint) != (
                    actual.schema, actual.counts, actual.data_fingerprint
                ):
                    raise ValueError("Post-copy schema or data differ.")
            except (OSError, ValueError, sqlite3.Error, RuntimeError):
                print(f"Failed or unverified: {target}. Follow the recovery procedure using backup {index + 1} in {backups}.")
                raise
            print(f"Verified: {target}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--direction", choices=("local-to-d1", "d1-to-local"), required=True)
    args = parser.parse_args(argv)
    try:
        return run(args.config.resolve(), args.direction)
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error, RuntimeError, EOFError) as exc:
        # SQL errors can refer to values and commands from the export.
        message = str(exc) if type(exc) in (ValueError, RuntimeError) else type(exc).__name__
        print(f"Sync stopped: {message}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
