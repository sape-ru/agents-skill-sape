# Agents skill: Sape Links SEO

Репозиторий для **Agent Skills** — портативных пакетов навыков по открытому стандарту
[Agent Skills](https://agentskills.io). Каждый навык — это папка с файлом `SKILL.md`
(с метаданными `name` + `description`) и опциональными `references/`, `scripts/`, `assets/`.
Любой совместимый агент может их загружать: Claude, OpenCode, Cursor, OpenAI Codex,
Gemini CLI и многие другие.

## Навыки

| Навык | Описание |
|-------|----------|
| [`sape-links-seo`](skills/sape-links-seo) | Платформенный навык: подключение Sape Links MCP, проекты и анкоры, поиск доноров, покупка статейных и арендных размещений, Избранное, чёрный список, управление размещениями с безопасными тратами. |
| [`sape-link-placements`](skills/sape-link-placements) | Навык по задаче: проверить список доноров, найти похожие площадки, подобрать доноров под проект, тестовый заказ и проверка ссылок после публикации. |

Общие правила для агентов (подключение, траты, баланс, ошибки) — в [`llms.txt`](llms.txt); каждый навык
содержит их копию между маркерами `<!-- sape-rules:start -->` и `<!-- sape-rules:end -->`.

---

## Sape Links SEO

Этот навык позволяет агенту автоматизировать закупку ссылочной массы через
[Sape](https://sape.ru): создавать проекты, искать и фильтровать площадки-доноры по
DR / трафику / цене / языку, загружать статьи, покупать размещения и управлять их
жизненным циклом. Требуется подключённый к агенту **Sape Links MCP-сервер**.

### Возможности

- Создание проектов для продвигаемых сайтов
- Поиск и фильтрация доноров (цена, DR, трафик, язык, метрики Majestic/Moz/Ahrefs/Semrush, …)
- Загрузка статей для модерации (формат «Статья», `news`), URL и анкоров, лимиты анкоров
- Статейные размещения: статья, обзор, ссылка в новости, ссылка в архиве
- Арендные ссылки: блочные и контекстные (помесячная оплата)
- Избранное и чёрный список доноров
- Проверка списка доноров и поиск похожих площадок (`sape-link-placements`)
- Управление купленными размещениями (одобрение, отмена, расторжение, …) со встроенными финансовыми ограничениями

### Быстрая установка в Claude (плагин)

Репозиторий одновременно является маркетплейсом плагинов Claude. Плагин `sape-links-seo`
содержит и навык, и подключение Sape Links MCP.

- **claude.ai / Claude Desktop:** *Customize → Plugins → Add → Add marketplace*, вставьте
  `https://github.com/sape-ru/agents-skill-sape` и добавьте плагин `sape-links-seo`.
  Затем откройте плагин → вкладка **Connectors** → добавьте и подключите `sape` (вход через
  OAuth) — без этого навык установлен, но инструменты Sape недоступны.
- **Claude Code (CLI, десктоп-приложение, VS Code):**

  ```bash
  /plugin marketplace add sape-ru/agents-skill-sape
  /plugin install sape-links-seo@sape
  ```

  Вторая команда откроет карточку плагина — выберите область установки (user / project / local).
  При первом обращении к инструментам Sape откроется вход через OAuth.

Плагины из сторонних маркетплейсов не обновляются автоматически — обновляйте через
`/plugin` → **Update now** или `claude plugin update sape-links-seo@sape`.

Если Sape Links MCP у вас уже подключён вручную, отключите один из двух, чтобы инструменты
не дублировались.

Для других агентов и для claude.ai (загрузка навыка архивом) используйте ручную установку ниже.

### 1. Подключите Sape Links MCP

Sape Links MCP — размещённый **streamable HTTP** сервер. Подключается только по URL —
аутентификация выполняется через встроенный OAuth-поток, поэтому токен API не нужно
вставлять в конфиг агента. На странице входа понадобятся email аккаунта и API-токен из
[Паспорт → Безопасность](https://passport.sape.ru/security/token/).

```
https://mcp-links.sape.ru/mcp
```

Способ добавления зависит от вашего агента. Например, в **Claude Desktop** откройте
*Settings → Developer → Edit Config* и добавьте в `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sape": {
      "type": "http",
      "url": "https://mcp-links.sape.ru/mcp"
    }
  }
}
```

> На старых клиентах без поддержки streamable HTTP используйте `"type": "sse"` вместо `"http"`.
> На claude.ai добавьте через *Settings → Connectors* тем же URL.

### 2. Установите навык

Готовые архивы навыка лежат в [Releases](https://github.com/sape-ru/agents-skill-sape/releases/latest).
Паковать самому не нужно — скачайте подходящий:

| Куда ставите | Архив |
|---|---|
| **claude.ai / Claude Desktop** (*Customize → Skills → Upload a skill*) | [`sape-links-seo-claude-web.zip`](https://github.com/sape-ru/agents-skill-sape/releases/latest/download/sape-links-seo-claude-web.zip) — с коротким описанием, укладывается в лимит claude.ai (200 символов) |
| **Другие агенты** со стандартом [Agent Skills](https://agentskills.io) (Cursor, Codex, Gemini CLI и др.) | [`sape-links-seo.zip`](https://github.com/sape-ru/agents-skill-sape/releases/latest/download/sape-links-seo.zip) — исходный навык без изменений |

В каждом релизе есть и архивы с версией в имени (например, `sape-links-seo-1.2.0.zip`), если нужна
конкретная версия. Для Claude Code удобнее ставить плагином — см. «Быстрая установка» выше.

<details>
<summary>Собрать архив самостоятельно</summary>

```bash
python3 scripts/package_skill.py   # архивы появятся в dist/
```

Скрипт проверяет, что версия совпадает во всех файлах, и кладёт папку навыка **корнем** архива,
как требует спецификация Agent Skills.
</details>

### 3. Используйте

Спросите агента естественным языком, например: *«Найди доноров с DR 30+ для моего сайта
example.com и купь гостевой пост до 5000 ₽.»* Навык проведёт агента по workflow и
потребует подтверждения перед любой покупкой или действием, двигающим деньги.

Вам также понадобится аккаунт **рекламодателя** Sape; API-токен создаётся в
[Паспорт → Безопасность](https://passport.sape.ru/security/token/). Пополнить баланс можно на
<https://passport.sape.ru/deposit/>.

## Содержимое репозитория

```
agents-skill-sape-seo/
├── README.md                              # этот файл (уровень репо, не входит в пакет навыка)
├── AGENTS.md                              # правила для AI-агентов, работающих в репозитории
├── CLAUDE.md                              # отсылка к AGENTS.md для Claude Code (импорт @AGENTS.md)
├── VERSIONS.md                            # версии навыка и заметки релизов
├── .gitignore
├── .claude-plugin/
│   ├── marketplace.json                   # каталог плагинов Claude (маркетплейс «sape»)
│   └── plugin.json                        # манифест плагина sape-links-seo
├── .mcp.json                              # подключение Sape Links MCP в составе плагина
├── .github/workflows/
│   ├── release.yml                        # тег vX.Y.Z, сборка архивов и релиз (push в main)
│   ├── check-versions.yml                 # проверка версий и описаний (PR)
│   └── check-skills.yml                   # проверка правил и навыков (PR, push)
├── packaging/
│   └── claude-web-description.txt         # короткое описание навыка для claude.ai (≤ 200 символов)
├── llms.txt                               # общие правила для агентов — источник для всех навыков
├── scripts/
│   ├── package_skill.py                   # проверка версий и сборка ZIP-архивов
│   ├── check_versions.py                  # PR-проверки: версии, VERSIONS.md, лимиты описаний
│   ├── sync_rules.py                      # копирует правила из llms.txt в навыки
│   └── validate_skills.py                 # проверка навыков по стандарту Agent Skills
└── skills/
    ├── sape-links-seo/                    # платформенный навык
    │   ├── SKILL.md
    │   └── references/
    │       ├── tools.md                   # все инструменты MCP с параметрами
    │       └── placement_actions.md       # действия и статусы размещений
    └── sape-link-placements/              # навык по задаче: подбор и покупка
        ├── SKILL.md
        └── references/
            └── similar-sites.md           # как искать похожие площадки
```

## Выпуск новой версии

1. Поднимите версию **одинаково везде**: `version` в `SKILL.md` каждого навыка,
   в `.claude-plugin/plugin.json` и у плагина в `.claude-plugin/marketplace.json`.
   Меняли правила — правьте `llms.txt` и запустите `python3 scripts/sync_rules.py`
   (в навыках блок правил вручную не редактируют). Проверка навыков —
   `python3 scripts/validate_skills.py`.
2. Обновите `VERSIONS.md`: версию и дату в таблице и добавьте сверху раздел
   `### X.Y.Z (дата)` с изменениями. Первая строка раздела станет заголовком релиза
   (`vX.Y.Z — …`), остальное — описанием. Он публичный: пишите для пользователей, без имён.
3. Если менялось описание навыка (`description` в `SKILL.md`), обновите и короткое описание
   в `packaging/claude-web-description.txt` — его видит claude.ai.
4. Влейте PR в `main`. GitHub Actions сам поставит тег `vX.Y.Z`, соберёт архивы из коммита
   тега и создаст релиз; заметки возьмёт из `VERSIONS.md`.

На каждом PR workflow *Check Versions* проверяет без публикации: совпадение версий во всех
файлах, строку и раздел в `VERSIONS.md`, лимиты описаний (1024 символа в `SKILL.md` и 200
в коротком описании для claude.ai) и что PR, меняющий файлы навыка или упаковки (`skills/`,
`packaging/`), поднимает версию. Изменения без новой версии релиз не создают: если после
тега текущей версии менялись `skills/` или `packaging/`, а версия не поднята, релизный
workflow упадёт с ошибкой. Повторный запуск релизного workflow не двигает существующий
тег — пересобирает и заменяет только ZIP-архивы релиза. Ветка `main` защищена правилом
«изменения только через PR», поэтому проверки пропустить нельзя.

## Смотрите также

- [Стандарт Agent Skills](https://agentskills.io) — открытый формат, которому следуют эти навыки
- [Как создавать собственные навыки (Claude Help Center)](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- Документация API Sape Links: [https://api-links.sape.ru/api/](https://api-links.sape.ru/api/)
- Приложение Sape Links: [https://api-links.sape.ru](https://api-links.sape.ru)

