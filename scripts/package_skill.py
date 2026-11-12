#!/usr/bin/env python3
"""Собирает ZIP-архивы навыка sape-links-seo для GitHub Releases.

    python3 scripts/package_skill.py               # собрать в dist/
    python3 scripts/package_skill.py --output DIR  # собрать в DIR
    python3 scripts/package_skill.py --version     # только напечатать версию

Перед сборкой проверяет:
- версия совпадает в SKILL.md, .claude-plugin/plugin.json и .claude-plugin/marketplace.json;
- описание в SKILL.md не длиннее 1024 символов (стандарт Agent Skills);
- короткое описание для claude.ai (packaging/claude-web-description.txt) не длиннее 200 символов.

Собирает два архива, в каждом папка навыка — корень архива:
- sape-links-seo-<версия>.zip            — исходный навык, для Claude Code, Cursor, Codex и др.
- sape-links-seo-claude-web-<версия>.zip — то же, но с коротким описанием для загрузки в claude.ai
и копии без версии в имени (sape-links-seo.zip, sape-links-seo-claude-web.zip) для ссылки
releases/latest/download/... в README.
"""
import argparse
import json
import pathlib
import re
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = "sape-links-seo"
SKILL_DIR = ROOT / "skills" / SKILL
WEB_DESC_FILE = ROOT / "packaging" / "claude-web-description.txt"
MAX_DESC = 1024
MAX_WEB_DESC = 200
# Фиксированная дата файлов в архиве: одинаковый исходник даёт одинаковый архив.
ZIP_DATE = (2020, 1, 1, 0, 0, 0)


def fail(msg):
    sys.exit(f"ошибка: {msg}")


def read_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        fail(f"{SKILL_DIR / 'SKILL.md'}: нет frontmatter")
    return m


def fm_field(fm, key):
    m = re.search(rf"^{key}:[ \t]*(.+)$", fm, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else None


def check_versions(skill_text):
    fm = read_frontmatter(skill_text).group(1)
    versions = {"skills/sape-links-seo/SKILL.md": fm_field(fm, "version")}
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    versions[".claude-plugin/plugin.json"] = plugin.get("version")
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    entry = next((p for p in market.get("plugins", []) if p.get("name") == SKILL), None)
    if entry is None:
        fail(f".claude-plugin/marketplace.json: нет плагина {SKILL}")
    versions[".claude-plugin/marketplace.json"] = entry.get("version")
    if len(set(versions.values())) != 1 or None in versions.values():
        lines = "\n".join(f"  {path}: {v}" for path, v in versions.items())
        fail(f"версии не совпадают — поднимите их одинаково во всех трёх файлах:\n{lines}")
    return versions[".claude-plugin/plugin.json"]


def web_skill_text(skill_text):
    desc = WEB_DESC_FILE.read_text(encoding="utf-8").strip()
    if "\n" in desc:
        fail(f"{WEB_DESC_FILE.relative_to(ROOT)}: описание должно быть одной строкой")
    if not 1 <= len(desc) <= MAX_WEB_DESC:
        fail(f"{WEB_DESC_FILE.relative_to(ROOT)}: {len(desc)} символов, для claude.ai нужно не больше {MAX_WEB_DESC}")
    quoted = '"' + desc.replace("\\", "\\\\").replace('"', '\\"') + '"'
    m = read_frontmatter(skill_text)
    fm, n = re.subn(r"^description:.*$", lambda _: f"description: {quoted}", m.group(1), count=1, flags=re.M)
    if n != 1:
        fail("в frontmatter SKILL.md нет строки description")
    return f"---\n{fm}\n---\n" + skill_text[m.end():]


def validate_skill(skill_text):
    """Все предсборочные проверки. Возвращает (версия, текст навыка для claude.ai)."""
    version = check_versions(skill_text)
    desc = fm_field(read_frontmatter(skill_text).group(1), "description") or ""
    if not 1 <= len(desc) <= MAX_DESC:
        fail(f"описание в SKILL.md — {len(desc)} символов, допустимо 1–{MAX_DESC}")
    web_text = web_skill_text(skill_text)
    return version, web_text


def skill_files():
    for path in sorted(SKILL_DIR.rglob("*")):
        rel = path.relative_to(SKILL_DIR)
        if path.is_file() and not any(p.startswith(".") or p == "__pycache__" for p in rel.parts):
            yield path, rel


def write_zip(target, skill_md_text):
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, rel in skill_files():
            info = zipfile.ZipInfo(f"{SKILL}/{rel.as_posix()}", ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            data = skill_md_text.encode("utf-8") if rel.as_posix() == "SKILL.md" else path.read_bytes()
            zf.writestr(info, data)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--output", default=str(ROOT / "dist"), help="папка для архивов (по умолчанию dist/)")
    ap.add_argument("--version", action="store_true", help="проверить и напечатать версию, ничего не собирая")
    args = ap.parse_args()

    # Приводим переводы строк к LF: при сборке на Windows git может отдать файл с CRLF.
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    version, web_text = validate_skill(skill_text)

    if args.version:
        print(version)
        return

    out = pathlib.Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    builds = {
        f"{SKILL}-{version}.zip": skill_text,
        f"{SKILL}.zip": skill_text,
        f"{SKILL}-claude-web-{version}.zip": web_text,
        f"{SKILL}-claude-web.zip": web_text,
    }
    for name, text in builds.items():
        write_zip(out / name, text)
        print(f"собран {out / name}")
    print(f"версия {version}")


if __name__ == "__main__":
    main()
