#!/usr/bin/env python3
"""Проверки PR перед релизом — аналог check-versions.mjs из marketingskills.

    python3 scripts/check_versions.py --base origin/main

Проверяет:
- версия совпадает в skills/sape-links-seo/SKILL.md, .claude-plugin/plugin.json
  и .claude-plugin/marketplace.json, описания в лимитах (общие проверки
  scripts/package_skill.py: 1024 символа в SKILL.md, 200 в коротком описании);
- таблица в VERSIONS.md содержит текущую версию навыка;
- в VERSIONS.md есть раздел `### X.Y.Z (дата)` — из него release-воркфлоу берёт
  заголовок и заметки релиза vX.Y.Z;
- PR, меняющий файлы навыка (skills/**), поднимает версию относительно base.

Любое расхождение завершает скрипт с ошибкой — так PR-проверка падает
с понятным сообщением.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import package_skill
from package_skill import ROOT, SKILL, SKILL_DIR, fail


def changed_files(base):
    """Файлы, добавленные, изменённые или переименованные этим PR относительно base."""
    out = subprocess.check_output(
        ["git", "diff", "--name-only", "--diff-filter=ACMR", f"{base}...HEAD"],
        cwd=ROOT, text=True,
    )
    return [line.strip() for line in out.splitlines() if line.strip()]


def version_at(ref):
    """Версия плагина в .claude-plugin/plugin.json на коммите ref (или None)."""
    try:
        text = subprocess.check_output(
            ["git", "show", f"{ref}:.claude-plugin/plugin.json"], cwd=ROOT, text=True)
        return json.loads(text).get("version")
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def parse_version(v):
    parts = str(v).split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        fail(f"версия {v!r} не в формате X.Y.Z")
    return tuple(int(p) for p in parts)


def check_versions_md(version):
    path = ROOT / "VERSIONS.md"
    if not path.exists():
        fail("VERSIONS.md: файла нет — добавьте таблицу версий и раздел изменений")
    text = path.read_text(encoding="utf-8")

    row = re.search(rf"^\|\s*{re.escape(SKILL)}\s*\|\s*([^\s|]+)\s*\|", text, re.M)
    if not row:
        fail(f"VERSIONS.md: в таблице нет строки навыка `{SKILL}`")
    if row.group(1) != version:
        fail(f"VERSIONS.md: в таблице версия {row.group(1)}, а в файлах навыка — {version}")

    if not re.search(rf"^### {re.escape(version)} \([^)]+\)\s*$", text, re.M):
        fail(f"VERSIONS.md: нет раздела '### {version} (дата)' — из него release-воркфлоу "
             "берёт заголовок и заметки релиза")


def check_bump(version, base, changed):
    if not any(p.startswith("skills/") for p in changed):
        return
    base_version = version_at(base)
    if base_version and parse_version(version) <= parse_version(base_version):
        fail(
            f"PR меняет файлы навыка (skills/**), но версия не поднята: "
            f"{base_version} → {version}. Поднимите версию одинаково в "
            "skills/sape-links-seo/SKILL.md, .claude-plugin/plugin.json и "
            ".claude-plugin/marketplace.json и опишите изменения в VERSIONS.md."
        )


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default="origin/main",
                    help="база для сравнения — ветка или коммит (по умолчанию origin/main)")
    args = ap.parse_args()

    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").replace("\r\n", "\n")

    # Совпадение версий в трёх файлах и лимиты описаний — как при сборке архивов.
    version, _ = package_skill.validate_skill(skill_text)

    check_versions_md(version)
    check_bump(version, args.base, changed_files(args.base))

    print(f"ок: версия {version} согласована, VERSIONS.md актуален")


if __name__ == "__main__":
    main()
