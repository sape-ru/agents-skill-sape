#!/usr/bin/env python3
"""Проверяет каждый навык по стандарту Agent Skills и правилам репозитория.

    python3 scripts/validate_skills.py

Проверки: есть frontmatter; `name` совпадает с папкой (строчные латинские буквы, цифры,
одиночные дефисы, 1–64 символа); `description` 1–1024 символа; `version` совпадает с
.claude-plugin/plugin.json (версия у репозитория одна); SKILL.md не длиннее 500 строк;
каждый файл из references/ упомянут в своём SKILL.md; evals/evals.json, если есть, — валидный JSON.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_LINES = 500
MAX_DESC = 1024


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else None


def field(fm, key):
    m = re.search(rf"^{key}:[ \t]*(.+)$", fm, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else None


def main():
    plugin_version = json.loads(
        (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")).get("version")
    errors = []
    skills = sorted(ROOT.glob("skills/*/SKILL.md"))
    if not skills:
        sys.exit("нет ни одного skills/*/SKILL.md")
    for skill in skills:
        folder = skill.parent
        rel = skill.relative_to(ROOT)
        text = skill.read_text(encoding="utf-8").replace("\r\n", "\n")
        fm = frontmatter(text)
        if fm is None:
            errors.append(f"{rel}: нет frontmatter")
            continue
        name = field(fm, "name")
        if name != folder.name or not name or not NAME_RE.match(name) or len(name) > 64:
            errors.append(f"{rel}: name {name!r} должен совпадать с папкой {folder.name!r} и быть kebab-case")
        desc = field(fm, "description") or ""
        if not 1 <= len(desc) <= MAX_DESC:
            errors.append(f"{rel}: description — {len(desc)} символов, допустимо 1–{MAX_DESC}")
        version = field(fm, "version")
        if version != plugin_version:
            errors.append(f"{rel}: version {version!r}, а в plugin.json — {plugin_version!r}")
        lines = text.count("\n") + 1
        if lines > MAX_LINES:
            errors.append(f"{rel}: {lines} строк, больше {MAX_LINES} — вынесите детали в references/")
        refs = folder / "references"
        if refs.is_dir():
            for ref in sorted(refs.iterdir()):
                if ref.is_file() and f"references/{ref.name}" not in text:
                    errors.append(f"{rel}: references/{ref.name} не упомянут в SKILL.md")
        evals = folder / "evals" / "evals.json"
        if evals.exists():
            try:
                json.loads(evals.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                errors.append(f"{evals.relative_to(ROOT)}: невалидный JSON: {e}")
        print(f"проверен {rel} ({lines} строк)")
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print("ок: все навыки прошли проверку")


if __name__ == "__main__":
    main()
