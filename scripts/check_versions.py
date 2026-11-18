#!/usr/bin/env python3
"""Проверки PR перед релизом — аналог check-versions.mjs из marketingskills.

    python3 scripts/check_versions.py --base origin/main

Проверяет:
- версия совпадает в SKILL.md каждого навыка, .claude-plugin/plugin.json,
  .claude-plugin/marketplace.json и .codex-plugin/plugin.json, описания в лимитах
  (общие проверки scripts/package_skill.py: 1024 символа в SKILL.md, 200 в коротком
  описании для claude.ai);
- таблица в VERSIONS.md содержит текущую версию каждого навыка;
- в VERSIONS.md есть раздел `### X.Y.Z (дата)` — из него release-воркфлоу берёт
  заголовок и заметки релиза vX.Y.Z;
- PR, меняющий файлы навыка или упаковки (skills/**, packaging/**), поднимает версию
  относительно base.

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
from package_skill import ROOT, fail


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


def check_versions_md(version, names):
    path = ROOT / "VERSIONS.md"
    if not path.exists():
        fail("VERSIONS.md: файла нет — добавьте таблицу версий и раздел изменений")
    text = path.read_text(encoding="utf-8")

    for name in names:
        row = re.search(rf"^\|\s*{re.escape(name)}\s*\|\s*([^\s|]+)\s*\|", text, re.M)
        if not row:
            fail(f"VERSIONS.md: в таблице нет строки навыка `{name}`")
        if row.group(1) != version:
            fail(f"VERSIONS.md: у `{name}` в таблице версия {row.group(1)}, а в файлах навыков — {version}")

    if not re.search(rf"^### {re.escape(version)} \([^)]+\)\s*$", text, re.M):
        fail(f"VERSIONS.md: нет раздела '### {version} (дата)' — из него release-воркфлоу "
             "берёт заголовок и заметки релиза")


def check_bump(version, base, changed):
    if not any(p.startswith(("skills/", "packaging/")) for p in changed):
        return
    base_version = version_at(base)
    if base_version and parse_version(version) <= parse_version(base_version):
        fail(
            f"PR меняет файлы навыка или упаковки (skills/**, packaging/**), но версия "
            f"не поднята: {base_version} → {version}. Поднимите версию одинаково в "
            "SKILL.md каждого навыка, .claude-plugin/plugin.json, "
            ".claude-plugin/marketplace.json и .codex-plugin/plugin.json и опишите "
            "изменения в VERSIONS.md."
        )


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default="origin/main",
                    help="база для сравнения — ветка или коммит (по умолчанию origin/main)")
    args = ap.parse_args()

    # Совпадение версий во всех файлах и лимиты описаний — как при сборке архивов.
    version, skills = package_skill.validate_skills()

    check_versions_md(version, list(skills))
    check_bump(version, args.base, changed_files(args.base))

    print(f"ок: версия {version} согласована, VERSIONS.md актуален")


if __name__ == "__main__":
    main()
