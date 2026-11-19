#!/usr/bin/env python3
"""Копирует блок «## Правила для агентов» из llms.txt во все SKILL.md между маркерами.

Один источник правил для всех навыков Sape: меняете правило в llms.txt, запускаете скрипт —
и все навыки обновлены.

    python3 scripts/sync_rules.py           # обновить навыки
    python3 scripts/sync_rules.py --check   # только проверить, что навыки не разошлись с llms.txt
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RULES_SRC = ROOT / "llms.txt"
SECTION = "## Правила для агентов"
START, END = "<!-- sape-rules:start -->", "<!-- sape-rules:end -->"


def rules_block():
    text = RULES_SRC.read_text(encoding="utf-8").replace("\r\n", "\n")
    m = re.search(rf"^{re.escape(SECTION)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        sys.exit(f"llms.txt: нет раздела '{SECTION}'")
    body = m.group(1).strip()
    return ("## Правила Sape для агентов (общие)\n\n"
            "<!-- Скопировано из llms.txt скриптом scripts/sync_rules.py. Не редактируйте здесь. -->\n\n"
            "Эти правила действуют во всех навыках Sape. Если этот блок и остальной текст навыка "
            "расходятся, следуйте этому блоку.\n\n" + body)


def main():
    check = "--check" in sys.argv
    block = f"{START}\n{rules_block()}\n{END}"
    stale = []
    skills = sorted(ROOT.glob("skills/*/SKILL.md"))
    if not skills:
        sys.exit("нет ни одного skills/*/SKILL.md")
    for skill in skills:
        text = skill.read_text(encoding="utf-8").replace("\r\n", "\n")
        new, n = re.subn(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
        if n != 1:
            sys.exit(f"{skill.relative_to(ROOT)}: нужен ровно один блок правил, найдено {n}")
        if new != text:
            stale.append(skill)
            if not check:
                skill.write_text(new, encoding="utf-8", newline="\n")
        print(f"{'УСТАРЕЛ' if new != text else 'ок     '} {skill.relative_to(ROOT)}")
    if check and stale:
        sys.exit("блок правил расходится с llms.txt — запустите python3 scripts/sync_rules.py")


if __name__ == "__main__":
    main()
