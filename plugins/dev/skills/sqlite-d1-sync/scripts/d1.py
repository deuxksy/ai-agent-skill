"""Cloudflare D1 transport using Wrangler's SQL export and import."""
import sqlite3
import subprocess
import tempfile
from contextlib import closing
from pathlib import Path


def identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def command(operation: str, database: str, argument: str) -> None:
    argv = ["wrangler", "d1", operation, database, "--remote", argument]
    if operation == "execute":
        argv.append("--yes")
    with tempfile.TemporaryDirectory() as directory:
        config = Path(directory) / "wrangler.json"
        config.write_text("{}\n", encoding="utf-8")
        result = subprocess.run(
            [*argv, "--config", str(config)],
            stdin=subprocess.DEVNULL, capture_output=True, check=False,
        )
    if result.returncode:
        raise RuntimeError(f"Wrangler d1 {operation} failed (exit {result.returncode}).")


def export(database: str, destination: Path) -> None:
    command("export", database, f"--output={destination}")


def replacement_drops(
    db: sqlite3.Connection, objects: list[tuple[str, str]]
) -> list[str]:
    drops = [
        f"DROP {kind.upper()} IF EXISTS {identifier(name)};"
        for kind, name in objects if kind != "table"
    ]
    tables = {name: set() for kind, name in objects if kind == "table"}
    canonical_names = {name.lower(): name for name in tables}
    for child in tables:
        for _, _, parent, *_ in db.execute(f"PRAGMA foreign_key_list({identifier(child)})"):
            name = canonical_names.get(parent.lower())
            if name is not None and name != child:
                tables[name].add(child)
    while tables:
        children = set(tables)
        leaves = sorted(name for name, references in tables.items() if not references & children)
        # Deferred foreign keys can permit cycles. The SQLite preflight checks the result.
        for name in leaves or [min(tables)]:
            drops.append(f"DROP TABLE IF EXISTS {identifier(name)};")
            del tables[name]
    return drops


def replace(database: str, source_sql: Path, target_sql: Path) -> None:
    with closing(sqlite3.connect(":memory:")) as target:
        target.executescript(target_sql.read_text(encoding="utf-8"))
        objects = target.execute("""
            SELECT type, name FROM sqlite_schema
            WHERE type IN ('trigger', 'view', 'table')
              AND name NOT GLOB 'sqlite_*' AND name <> '_cf_KV'
            ORDER BY CASE type WHEN 'trigger' THEN 0 WHEN 'view' THEN 1 ELSE 2 END
        """).fetchall()
        drops = replacement_drops(target, objects)
        target.execute("PRAGMA foreign_keys = ON")

        script = source_sql.read_text(encoding="utf-8")
        start = "BEGIN TRANSACTION;\n"
        end = "COMMIT;\n"
        if not script.startswith(start) or not script.endswith(end):
            raise ValueError("Unexpected SQLite dump format.")
        payload = "\n".join(["PRAGMA defer_foreign_keys = ON;", *drops, script[len(start):-len(end)]])
        target.executescript("BEGIN;\n" + payload + "\nCOMMIT;")
        if target.execute("PRAGMA foreign_key_check").fetchone():
            raise ValueError("Replacement SQL failed foreign key validation.")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "replacement.sql"
            path.write_text(payload, encoding="utf-8")
            command("execute", database, f"--file={path}")
