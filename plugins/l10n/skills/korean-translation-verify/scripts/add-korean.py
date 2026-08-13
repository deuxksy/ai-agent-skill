#!/usr/bin/env python3
"""
One-time script to add Korean (ko) language support to GL.iNet docs.
Run from repository root: python scripts/add-korean.py
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from ruamel.yaml import YAML

REPO_ROOT = Path(__file__).parent.parent
DOCS_DIR = REPO_ROOT / "docs"
EN_DIR = DOCS_DIR / "en"
KO_DIR = DOCS_DIR / "ko"
LANGUAGES = ["en", "de", "es", "jp"]


def create_directory_structure():
    print("Creating directory structure...")
    (KO_DIR / "docs").mkdir(parents=True)
    (KO_DIR / "overrides").mkdir(parents=True)
    print(f"  Created: {KO_DIR}/docs/")
    print(f"  Created: {KO_DIR}/overrides/")


def copy_english_docs():
    print("Copying English documentation files...")
    en_docs = EN_DIR / "docs"
    ko_docs = KO_DIR / "docs"

    for item in en_docs.iterdir():
        dest = ko_docs / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
            print(f"  Copied directory: {item.name}/")
        else:
            shutil.copy2(item, dest)
            print(f"  Copied file: {item.name}")

    en_overrides = EN_DIR / "overrides"
    ko_overrides = KO_DIR / "overrides"

    if en_overrides.exists():
        ko_overrides.rmdir()
        shutil.copytree(en_overrides, ko_overrides)
        print(f"  Copied: overrides/")


def generate_mkdocs_yml():
    print("Generating mkdocs.yml...")
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = True

    with open(EN_DIR / "mkdocs.yml", "r", encoding="utf-8") as f:
        config = yaml.load(f)

    config["site_url"] = config["site_url"].replace("/en/", "/ko/")
    config["theme"]["language"] = "ko"

    if "extra" in config and "alternate":
        for alt in config["extra"]["alternate"]:
            if alt.get("lang") == "en":
                korean_entry = {
                    "name": "한국어",
                    "link": "/router/ko/4/",
                    "lang": "ko"
                }
                config["extra"]["alternate"].append(korean_entry)
                break

    with open(KO_DIR / "mkdocs.yml", "w", encoding="utf-8") as f:
        yaml.dump(config, f)
    print(f"  Created: {KO_DIR / 'mkdocs.yml'}")


def update_alternate_links():
    print("Updating alternate links in existing mkdocs.yml files...")
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = True

    korean_entry = {
        "name": "한국어",
        "link": "/router/ko/4/",
        "lang": "ko"
    }

    for lang in LANGUAGES:
        yml_path = DOCS_DIR / lang / "mkdocs.yml"
        backup_path = Path(str(yml_path) + ".bak")
        shutil.copy2(yml_path, backup_path)
        print(f"  Backup: {backup_path}")

        with open(yml_path, "r", encoding="utf-8") as f:
            config = yaml.load(f)

        if "extra" in config and "alternate":
            has_korean = any(
                alt.get("lang") == "ko"
                for alt in config["extra"]["alternate"]
            )
            if not has_korean:
                config["extra"]["alternate"].append(korean_entry)
                print(f"  Added Korean to: {lang}/mkdocs.yml")
            else:
                print(f"  Korean already in: {lang}/mkdocs.yml (skipping)")

        with open(yml_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f)


def commit_changes():
    print("Committing changes...")
    subprocess.run(["git", "add", "docs/ko/"], check=True)
    print("  Staged: docs/ko/")

    for lang in LANGUAGES:
        yml_path = DOCS_DIR / lang / "mkdocs.yml"
        subprocess.run(["git", "add", str(yml_path)], check=True)
        print(f"  Staged: docs/{lang}/mkdocs.yml")

    result = subprocess.run(
        ["git", "commit", "-m", "feat: add Korean (ko) language support"],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"\n  Committed: {result.stdout.strip()}")
    else:
        print(f"\n  Commit failed: {result.stderr}")


def main():
    print("=== Adding Korean Language Support ===\n")

    if KO_DIR.exists():
        print(f"ERROR: {KO_DIR} already exists. Aborting.")
        sys.exit(1)

    create_directory_structure()
    print()
    copy_english_docs()
    print()
    generate_mkdocs_yml()
    print()
    update_alternate_links()
    print()
    commit_changes()

    print()
    print("=== Korean Language Support Added Successfully ===")
    print()
    print("Next steps:")
    print("1. Preview: mkdocs serve -f docs/ko/mkdocs.yml")
    print("2. Translate: docs/ko/TRANSLATING-ko.md")
    print("3. Push: git push origin master")


if __name__ == "__main__":
    main()
