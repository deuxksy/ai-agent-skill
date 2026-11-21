import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sqlite_d1_sync as sync


class SyncTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.local = self.root / "local.db"
        self.remote = self.root / "remote.db"
        for path, value in ((self.local, "local"), (self.remote, "remote")):
            with sqlite3.connect(path) as db:
                db.executescript("CREATE TABLE works (name TEXT); CREATE INDEX names ON works(name);")
                db.execute("INSERT INTO works VALUES (?)", (value,))

    def test_local_round_trip(self):
        sql = self.root / "dump.sql"
        snapshot = sync.snapshot_local(self.local, sql)
        self.assertEqual(snapshot.counts, {"works": 1})
        sync.restore_local(sql, self.remote)
        with sqlite3.connect(self.remote) as db:
            self.assertEqual(db.execute("SELECT * FROM works").fetchall(), [("local",)])
            self.assertTrue(db.execute("SELECT name FROM sqlite_schema WHERE name='names'").fetchone())

    def test_restore_failure_preserves_target(self):
        sql = self.root / "bad.sql"
        sql.write_text("CREATE TABLE broken;")
        with self.assertRaises(sqlite3.Error):
            sync.restore_local(sql, self.remote)
        with sqlite3.connect(self.remote) as db:
            self.assertEqual(db.execute("SELECT * FROM works").fetchone(), ("remote",))

    def test_missing_is_not_empty(self):
        with self.assertRaises(FileNotFoundError):
            sync.snapshot_local(self.root / "missing.db", self.root / "out.sql")

    def run_sync(self, direction, answer):
        config = self.root / "config.toml"
        config.write_text('d1_account_id = "test-account"\n[[databases]]\nlocal_path = "local.db"\nd1_database = "test"\n')
        with patch.dict("os.environ", {"CLOUDFLARE_ACCOUNT_ID": "test-account"}), \
             patch.object(sync.d1, "export", side_effect=lambda _, dest: sync.snapshot_local(self.remote, dest)), \
             patch.object(sync.d1, "replace", side_effect=lambda _, source, __: sync.restore_local(source, self.remote)) as replace, \
             patch("builtins.input", side_effect=answer):
            result = sync.main(["--config", str(config), "--direction", direction])
            return result, replace.call_count

    def test_decline_makes_no_writes(self):
        self.assertEqual(self.run_sync("local-to-d1", ["no"]), (0, 0))

    def test_changed_snapshot_requires_approval(self):
        def change(_):
            with sqlite3.connect(self.local) as db:
                db.execute("UPDATE works SET name = 'changed'")
            return "yes"
        self.assertEqual(self.run_sync("local-to-d1", change), (1, 0))

    def test_both_directions_verify_counts(self):
        self.assertEqual(self.run_sync("local-to-d1", ["yes"]), (0, 1))
        with sqlite3.connect(self.remote) as db:
            self.assertEqual(db.execute("SELECT * FROM works").fetchone(), ("local",))
            db.execute("UPDATE works SET name = 'remote'")
        self.assertEqual(self.run_sync("d1-to-local", ["yes"]), (0, 0))
        with sqlite3.connect(self.local) as db:
            self.assertEqual(db.execute("SELECT * FROM works").fetchone(), ("remote",))

    def test_pull_to_new_machine(self):
        self.local.unlink()
        self.assertEqual(self.run_sync("d1-to-local", ["yes"]), (0, 0))
        with sqlite3.connect(self.local) as db:
            self.assertEqual(db.execute("SELECT * FROM works").fetchone(), ("remote",))

    def test_remote_sql_removes_extra_objects(self):
        source = self.root / "source.sql"
        target = self.root / "target.sql"
        sync.snapshot_local(self.local, source)
        with sqlite3.connect(self.remote) as db:
            db.execute("CREATE TABLE obsolete (id INTEGER)")
        sync.snapshot_local(self.remote, target)

        def execute(operation, database, argument):
            self.assertEqual((operation, database), ("execute", "test"))
            with sqlite3.connect(self.remote) as db:
                db.executescript(Path(argument.removeprefix("--file=")).read_text())
                self.assertEqual(db.execute("SELECT name FROM works").fetchone(), ("local",))
                self.assertIsNone(db.execute("SELECT name FROM sqlite_schema WHERE name='obsolete'").fetchone())

        with patch.object(sync.d1, "command", side_effect=execute):
            sync.d1.replace("test", source, target)

    def test_remote_drops_restrict_child_before_parent(self):
        source, target = self.root / "source.sql", self.root / "target.sql"
        sync.snapshot_local(self.local, source)
        with sqlite3.connect(self.remote) as db:
            db.executescript("""
                CREATE TABLE a_parent (id INTEGER PRIMARY KEY);
                CREATE TABLE z_child (parent REFERENCES a_parent(id) ON DELETE RESTRICT);
                INSERT INTO a_parent VALUES (1);
                INSERT INTO z_child VALUES (1);
            """)
        sync.snapshot_local(self.remote, target)
        with patch.object(sync.d1, "command") as command:
            sync.d1.replace("test", source, target)
        command.assert_called_once()

    def test_wrangler_import_reuses_cli_approval(self):
        with patch.object(sync.d1.subprocess, "run") as run:
            run.return_value.returncode = 0
            sync.d1.command("execute", "test", "--file=backup.sql")
            sync.d1.command("export", "test", "--output=read.sql")
        self.assertIn("--yes", run.call_args_list[0].args[0])
        self.assertNotIn("--yes", run.call_args_list[1].args[0])

    def test_wrangler_ignores_project_bindings(self):
        def execute(argv, **_):
            config = Path(argv[argv.index("--config") + 1])
            self.assertEqual(config.read_text().strip(), "{}")
            return type("Completed", (), {"returncode": 0})()

        with patch.object(sync.d1.subprocess, "run", side_effect=execute):
            sync.d1.export("test", self.root / "out.sql")

    def test_lossy_sqlite_dump_cannot_be_applied(self):
        with sqlite3.connect(self.local) as db:
            db.execute("INSERT INTO works VALUES (?)", ("before\x00after",))
        self.assertEqual(self.run_sync("local-to-d1", ["yes"]), (1, 0))
