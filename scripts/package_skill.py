#!/usr/bin/env python3
"""Собирает ZIP-архивы навыков из skills/ для GitHub Releases.

    python3 scripts/package_skill.py               # собрать в dist/
    python3 scripts/package_skill.py --output DIR  # собрать в DIR
    python3 scripts/package_skill.py --version     # только напечатать версию

Перед сборкой проверяет:
- версия совпадает в SKILL.md каждого навыка, .claude-plugin/plugin.json,
  .claude-plugin/marketplace.json и .codex-plugin/plugin.json;
- описание в SKILL.md не длиннее 1024 символов (стандарт Agent Skills);
- у каждого навыка есть короткое описание для claude.ai
  (packaging/claude-web-descriptions.json) — одной строкой, не длиннее 200 символов.

Для каждого навыка собирает два архива, в каждом папка навыка — корень архива:
- <навык>-<версия>.zip            — исходный навык, для Claude Code, Cursor, Codex, ChatGPT и др.
- <навык>-claude-web-<версия>.zip — то же, но с коротким описанием для загрузки в claude.ai
и копии без версии в имени (<навык>.zip, <навык>-claude-web.zip) для ссылки
releases/latest/download/... в README. Папка evals/ в архивы не попадает:
это проверки для разработчиков, установленному навыку они не нужны.
"""
import argparse
import json
import pathlib
import re
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
WEB_DESC_FILE = ROOT / "packaging" / "claude-web-descriptions.json"
PLUGIN = "sape-links"  # имя плагина в манифестах
MAX_DESC = 1024
MAX_WEB_DESC = 200
# Не кладём в архив: служебные файлы и проверки для разработчиков.
EXCLUDED_DIRS = {"evals", "__pycache__"}
# Фиксированная дата файлов в архиве: одинаковый исходник даёт одинаковый архив.
ZIP_DATE = (2020, 1, 1, 0, 0, 0)


def fail(msg):
    sys.exit(f"ошибка: {msg}")


def skill_names():
    names = sorted(p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md"))
    if not names:
        fail("в skills/ нет ни одного навыка")
    return names


def read_skill(name):
    # Приводим переводы строк к LF: при сборке на Windows git может отдать файл с CRLF.
    return (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8").replace("\r\n", "\n")


def read_frontmatter(text, name):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        fail(f"skills/{name}/SKILL.md: нет frontmatter")
    return m


def fm_field(fm, key):
    m = re.search(rf"^{key}:[ \t]*(.+)$", fm, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else None


def load_json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def check_versions(texts):
    versions = {}
    for name, text in texts.items():
        versions[f"skills/{name}/SKILL.md"] = fm_field(read_frontmatter(text, name).group(1), "version")
    versions[".claude-plugin/plugin.json"] = load_json(".claude-plugin/plugin.json").get("version")
    market = load_json(".claude-plugin/marketplace.json")
    entry = next((p for p in market.get("plugins", []) if p.get("name") == PLUGIN), None)
    if entry is None:
        fail(f".claude-plugin/marketplace.json: нет плагина {PLUGIN}")
    versions[".claude-plugin/marketplace.json"] = entry.get("version")
    versions[".codex-plugin/plugin.json"] = load_json(".codex-plugin/plugin.json").get("version")
    if len(set(versions.values())) != 1 or None in versions.values():
        lines = "\n".join(f"  {path}: {v}" for path, v in versions.items())
        fail(f"версии не совпадают — поднимите их одинаково во всех файлах:\n{lines}")
    return versions[".claude-plugin/plugin.json"]


def web_descriptions(names):
    rel = WEB_DESC_FILE.relative_to(ROOT).as_posix()
    descs = json.loads(WEB_DESC_FILE.read_text(encoding="utf-8"))
    extra = sorted(set(descs) - set(names))
    if extra:
        fail(f"{rel}: описания для несуществующих навыков: {', '.join(extra)}")
    for name in names:
        desc = str(descs.get(name, "")).strip()
        if not desc:
            fail(f"{rel}: нет короткого описания для навыка {name}")
        if "\n" in desc:
            fail(f"{rel}: описание {name} должно быть одной строкой")
        if len(desc) > MAX_WEB_DESC:
            fail(f"{rel}: описание {name} — {len(desc)} символов, для claude.ai нужно не больше {MAX_WEB_DESC}")
        descs[name] = desc
    return descs


def web_skill_text(text, name, desc):
    quoted = '"' + desc.replace("\\", "\\\\").replace('"', '\\"') + '"'
    m = read_frontmatter(text, name)
    fm, n = re.subn(r"^description:.*$", lambda _: f"description: {quoted}", m.group(1), count=1, flags=re.M)
    if n != 1:
        fail(f"skills/{name}/SKILL.md: в frontmatter нет строки description")
    return f"---\n{fm}\n---\n" + text[m.end():]


def validate_skills():
    """Все предсборочные проверки. Возвращает (версия, {навык: (текст, текст для claude.ai)})."""
    names = skill_names()
    texts = {name: read_skill(name) for name in names}
    version = check_versions(texts)
    webs = web_descriptions(names)
    result = {}
    for name, text in texts.items():
        desc = fm_field(read_frontmatter(text, name).group(1), "description") or ""
        if not 1 <= len(desc) <= MAX_DESC:
            fail(f"skills/{name}/SKILL.md: описание — {len(desc)} символов, допустимо 1–{MAX_DESC}")
        result[name] = (text, web_skill_text(text, name, webs[name]))
    return version, result


def skill_files(name):
    skill_dir = SKILLS_DIR / name
    for path in sorted(skill_dir.rglob("*")):
        rel = path.relative_to(skill_dir)
        if path.is_file() and not any(p.startswith(".") or p in EXCLUDED_DIRS for p in rel.parts):
            yield path, rel


def write_zip(target, name, skill_md_text):
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, rel in skill_files(name):
            info = zipfile.ZipInfo(f"{name}/{rel.as_posix()}", ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            data = skill_md_text.encode("utf-8") if rel.as_posix() == "SKILL.md" else path.read_bytes()
            zf.writestr(info, data)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--output", default=str(ROOT / "dist"), help="папка для архивов (по умолчанию dist/)")
    ap.add_argument("--version", action="store_true", help="проверить и напечатать версию, ничего не собирая")
    args = ap.parse_args()

    version, skills = validate_skills()

    if args.version:
        print(version)
        return

    out = pathlib.Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    for name, (text, web_text) in skills.items():
        builds = {
            f"{name}-{version}.zip": text,
            f"{name}.zip": text,
            f"{name}-claude-web-{version}.zip": web_text,
            f"{name}-claude-web.zip": web_text,
        }
        for zip_name, skill_md in builds.items():
            write_zip(out / zip_name, name, skill_md)
            print(f"собран {out / zip_name}")
    print(f"версия {version}")


if __name__ == "__main__":
    main()
