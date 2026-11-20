# Навыки Sape Links для ИИ-агентов

Навыки учат ИИ-агента работать с биржей ссылок [Sape](https://sape.ru): искать площадки,
покупать размещения и следить за ними. Навыки сделаны по открытому стандарту
[Agent Skills](https://agentskills.io): каждый навык — папка с файлом `SKILL.md` и справочниками.
Их понимают Claude, Cursor, OpenAI Codex, Gemini CLI, OpenCode и другие агенты.

> **Обновляетесь с 2.0?** В версии 2.1.0 плагин и навыки переименованы: `sape-links-seo` →
> `sape-links`, `sape-link-placements` → `sape-seo`. Удалите старый плагин или навыки и
> поставьте новые — команды в разделе [«Переход с 2.0»](#переход-с-20).

## Навыки

| Навык | Описание |
|-------|----------|
| [`sape-links`](skills/sape-links) | Основной навык: подключение Sape Links MCP, проекты и анкоры, поиск доноров, покупка статейных и арендных размещений, Избранное, чёрный список, управление размещениями. Перед любой тратой агент показывает смету и ждёт подтверждения. |
| [`sape-seo`](skills/sape-seo) | SEO-задачи через Sape, сейчас — подбор площадок: проверить список доноров, найти похожие площадки, подобрать доноров под проект, тестовый заказ и проверка ссылок после публикации. |

Общие правила для агентов (подключение, траты, баланс, ошибки) — в [`llms.txt`](llms.txt); каждый навык
содержит их копию между маркерами `<!-- sape-rules:start -->` и `<!-- sape-rules:end -->`.

---

## Что умеют навыки

Агент закупает ссылки через Sape сам: создаёт проекты, ищет и фильтрует площадки-доноры
по DR, трафику, цене и языку, загружает статьи, покупает размещения и ведёт их до публикации.
Для работы агенту нужен подключённый **MCP-сервер Sape Links** — через него агент вызывает
функции платформы.

### Возможности

- Создание проектов для продвигаемых сайтов
- Поиск и фильтрация доноров (цена, DR, трафик, язык, метрики Majestic/Moz/Ahrefs/Semrush, …)
- Загрузка статей для модерации (формат «Статья», `news`), URL и анкоров, лимиты анкоров
- Статейные размещения: статья, обзор, ссылка в новости, ссылка в архиве
- Арендные ссылки: блочные и контекстные (помесячная оплата)
- Избранное и чёрный список доноров
- Проверка списка доноров и поиск похожих площадок (`sape-seo`)
- Управление купленными размещениями: одобрение, отмена, снятие ссылки, заморозка аренды. Всё, что тратит деньги, — только после подтверждения пользователя

## Установка

Нужны две вещи: **навыки** (что и как делать) и **подключение к Sape Links MCP** (через него
агент вызывает функции биржи). Где можно, ставьте плагин `sape-links` — он приносит и то и
другое сразу.

| Вариант | Ассистент | Навыки | Подключение к Sape |
|---|---|---|---|
| [1](#вариант-1-claude-claudeai-и-claude-desktop) | **Claude** (claude.ai, Claude Desktop) | плагин или ZIP-архивы | вкладка Connectors |
| [2](#вариант-2-claude-code) | **Claude Code** (терминал, десктоп, VS Code) | плагин | в составе плагина |
| [3](#вариант-3-codex) | **Codex** | плагин | в составе плагина |
| [4](#вариант-4-chatgpt) | **ChatGPT** | ZIP-архивы (где доступны навыки) | пользовательский коннектор |
| [5](#вариант-5-cursor-gemini-cli-opencode-windsurf-и-другие) | **Cursor, Gemini CLI, OpenCode, Windsurf и другие** | `npx skills add` | вручную, адрес сервера |

Вход в Sape одинаковый везде: при первом обращении к Sape откроется страница входа, на ней
нужны email аккаунта и API-токен из [Паспорт → Безопасность](https://passport.sape.ru/security/token/).
Вписывать токен в настройки агента не нужно. Нужен аккаунт Sape для SEO-оптимизатора — заказчика ссылок.

### Вариант 1. Claude (claude.ai и Claude Desktop)

**Плагином:** *Customize → Plugins → Add → Add marketplace*, вставьте
`https://github.com/sape-ru/agents-skill-sape` и добавьте плагин `sape-links`. Затем откройте
плагин → вкладка **Connectors** → добавьте и подключите `sape` и войдите в аккаунт Sape — без
этого навыки установлены, но агент не может работать с Sape.

**Архивами:** скачайте оба архива и загрузите каждый через *Customize → Skills → Upload a skill*:

- [`sape-links-claude-web.zip`](https://github.com/sape-ru/agents-skill-sape/releases/latest/download/sape-links-claude-web.zip) — основной навык;
- [`sape-seo-claude-web.zip`](https://github.com/sape-ru/agents-skill-sape/releases/latest/download/sape-seo-claude-web.zip) — SEO-задачи: подбор площадок.

В архивах `-claude-web` короткое описание навыка — оно укладывается в лимит claude.ai (200 символов).
Подключение добавьте в *Settings → Connectors → Add custom connector* с адресом
`https://mcp-links.sape.ru/mcp`.

### Вариант 2. Claude Code

```bash
claude plugin install sape-links --marketplace sape-ru/agents-skill-sape
```

Или внутри сессии:

```bash
/plugin marketplace add sape-ru/agents-skill-sape
/plugin install sape-links@sape
```

Плагин ставит оба навыка и подключение к Sape Links MCP. Вторая команда откроет карточку
плагина — выберите область установки (user / project / local).

### Вариант 3. Codex

```bash
codex plugin marketplace add sape-ru/agents-skill-sape
codex plugin add sape-links@sape
```

Плагин `sape-links` ставит оба навыка и подключение к Sape Links MCP. Вместо второй команды
можно в сессии Codex открыть `/plugins` и установить плагин оттуда. Новые навыки и инструменты
появятся в новой сессии.

### Вариант 4. ChatGPT

- **Подключение к Sape:** добавьте `https://mcp-links.sape.ru/mcp` как пользовательский
  коннектор (приложение) в настройках ChatGPT. Сейчас ChatGPT разрешает свои коннекторы не на
  всех тарифах — в рабочих пространствах это включает администратор.
- **Навыки:** где в ChatGPT доступны навыки, скачайте архивы со
  [страницы релизов](https://github.com/sape-ru/agents-skill-sape/releases/latest) —
  [`sape-links.zip`](https://github.com/sape-ru/agents-skill-sape/releases/latest/download/sape-links.zip)
  и [`sape-seo.zip`](https://github.com/sape-ru/agents-skill-sape/releases/latest/download/sape-seo.zip)
  — и загрузите каждый в разделе Skills (*Upload from your computer*). Если навыков нет, агент всё равно работает с
  Sape через коннектор, но без подсказок навыков.

### Вариант 5. Cursor, Gemini CLI, OpenCode, Windsurf и другие

Навыки — через [`npx skills`](https://github.com/vercel-labs/skills); программа сама найдёт
установленных агентов и спросит, куда ставить:

```bash
npx skills add sape-ru/agents-skill-sape
```

Подключение к Sape добавьте в настройках MCP агента: адрес `https://mcp-links.sape.ru/mcp`,
имя `sape`. Например, в Cursor — *Settings → MCP → Add new MCP server* или в `mcp.json`:

```json
{
  "mcpServers": {
    "sape": {
      "url": "https://mcp-links.sape.ru/mcp"
    }
  }
}
```

Если команда `npx skills` недоступна, скачайте архивы
[`sape-links.zip`](https://github.com/sape-ru/agents-skill-sape/releases/latest/download/sape-links.zip)
и [`sape-seo.zip`](https://github.com/sape-ru/agents-skill-sape/releases/latest/download/sape-seo.zip)
и распакуйте их в папку навыков вашего агента.

> Если Sape Links MCP у вас уже подключён вручную, а потом вы поставили плагин, отключите одно
> из двух подключений, чтобы инструменты не дублировались. Старый агент не принимает
> `"type": "http"` — используйте `"type": "sse"`.

<details>
<summary>Собрать архивы самостоятельно</summary>

```bash
python3 scripts/package_skill.py   # архивы появятся в dist/
```

Скрипт проверяет, что версия совпадает во всех файлах, и кладёт папку навыка **корнем** архива,
как требует спецификация Agent Skills. В каждом релизе есть и архивы с версией в имени
(например, `sape-links-2.1.0.zip`), если нужна конкретная версия.
</details>

## Обновление

Ставили версию 2.0 (плагин или навыки `sape-links-seo`, `sape-link-placements`)? Обновление
не сработает — навыки переименованы. Сделайте [«Переход с 2.0»](#переход-с-20).

Навыки сами подскажут, что вышла новая версия: раз за сессию они сверяются с
[`VERSIONS.md`](VERSIONS.md) и пишут об этом одной строкой в конце ответа (если агент умеет
открывать веб-страницы). Обновляется навык так:

| Как ставили | Как обновить |
|---|---|
| Плагин в Claude Code | `claude plugin update sape-links@sape` или `/plugin` → **Update now**. Чтобы обновлялся сам: `/plugin` → **Marketplaces** → `sape` → **Enable auto-update** |
| Плагин в Claude Desktop, claude.ai | откройте плагин в *Customize → Plugins* и обновите его |
| Плагин в Codex | `codex plugin marketplace upgrade sape`, затем новая сессия |
| `npx skills` | `npx skills update` (для навыков, поставленных с `-g`, — `npx skills update -g`) |
| Архивы (claude.ai, ChatGPT, вручную) | скачайте архивы заново по ссылкам из «Установки» и загрузите поверх старых |

Новая версия начинает работать в новой сессии агента. Что изменилось — в [`VERSIONS.md`](VERSIONS.md)
и в [Releases](https://github.com/sape-ru/agents-skill-sape/releases).

## Переход с 2.0

В версии 2.1.0 плагин и навыки получили новые имена. Содержание навыков не менялось, но
старые имена больше не обновляются, поэтому старое удалите и поставьте новое.

| Было (2.0) | Стало (2.1) |
|---|---|
| плагин `sape-links-seo@sape` | плагин `sape-links@sape` (каталог прежний — `sape`) |
| навык `sape-links-seo` | навык `sape-links` |
| навык `sape-link-placements` | навык `sape-seo` |

Подключение к Sape Links MCP (сервер `sape`) и вход не меняются.

**Claude Code:**

```bash
claude plugin uninstall sape-links-seo@sape
claude plugin marketplace update sape
claude plugin install sape-links@sape
```

**Codex:**

```bash
codex plugin remove sape-links-seo@sape
codex plugin marketplace upgrade sape
codex plugin add sape-links@sape
```

**Claude Desktop и claude.ai:** в *Customize → Plugins* удалите плагин `sape-links-seo` или в
*Customize → Skills* — навыки `sape-links-seo` и `sape-link-placements`. Затем поставьте плагин
`sape-links` или архивы — [вариант 1](#вариант-1-claude-claudeai-и-claude-desktop).

**`npx skills` (Cursor и другие):**

```bash
npx skills remove sape-links-seo sape-link-placements
npx skills add sape-ru/agents-skill-sape
```

Ставили навыки с `-g` — добавьте `-g` к обеим командам.

**ChatGPT и ручная установка:** удалите навыки `sape-links-seo` и `sape-link-placements` (в
ChatGPT — в разделе Skills, вручную — их папки) и загрузите архивы `sape-links.zip` и
`sape-seo.zip` по ссылкам из [варианта 4](#вариант-4-chatgpt).

## Использование

Спросите агента естественным языком, например: *«Найди доноров с DR 30+ для моего сайта
example.com и купи гостевой пост до 5000 ₽.»* Навык проведёт агента по шагам, а перед любой
покупкой или действием, которое тратит деньги, агент попросит подтверждения.

Пополнить баланс можно на <https://passport.sape.ru/deposit/>.

## Содержимое репозитория

```
agents-skill-sape/
├── README.md                              # этот файл (уровень репо, не входит в пакет навыка)
├── AGENTS.md                              # правила для AI-агентов, работающих в репозитории
├── CLAUDE.md                              # отсылка к AGENTS.md для Claude Code (импорт @AGENTS.md)
├── LICENSE                                # лицензия MIT
├── VERSIONS.md                            # версии навыков и заметки релизов (по нему навыки проверяют обновления)
├── .gitignore
├── .claude-plugin/
│   ├── marketplace.json                   # каталог плагинов Claude (маркетплейс «sape»)
│   └── plugin.json                        # манифест плагина sape-links
├── .codex-plugin/
│   └── plugin.json                        # манифест плагина для Codex (те же навыки и .mcp.json)
├── .agents/plugins/
│   └── marketplace.json                   # каталог плагинов для Codex (маркетплейс «sape»)
├── .mcp.json                              # подключение Sape Links MCP в составе плагина
├── .github/workflows/
│   ├── release.yml                        # тег vX.Y.Z, сборка архивов и релиз (push в main)
│   ├── check-versions.yml                 # проверка версий и описаний (PR)
│   └── check-skills.yml                   # проверка правил и навыков (PR, push)
├── packaging/
│   └── claude-web-descriptions.json       # короткие описания навыков для claude.ai (≤ 200 символов)
├── llms.txt                               # общие правила для агентов — источник для всех навыков
├── scripts/
│   ├── package_skill.py                   # проверка версий и сборка ZIP-архивов
│   ├── check_versions.py                  # PR-проверки: версии, VERSIONS.md, лимиты описаний
│   ├── sync_rules.py                      # копирует правила из llms.txt в навыки
│   └── validate_skills.py                 # проверка навыков по стандарту Agent Skills
└── skills/
    ├── sape-links/                        # основной навык
    │   ├── SKILL.md
    │   ├── evals/                         # сценарии проверки поведения (в архивы не входят)
    │   └── references/
    │       ├── tools.md                   # все инструменты MCP с параметрами
    │       └── placement_actions.md       # действия и статусы размещений
    └── sape-seo/                          # навык по задаче: SEO через Sape (подбор и покупка)
        ├── SKILL.md
        ├── evals/
        └── references/
            └── similar-sites.md           # как искать похожие площадки
```

## Выпуск новой версии

1. Поднимите версию **одинаково везде**: `version` в `SKILL.md` каждого навыка,
   в `.claude-plugin/plugin.json`, у плагина в `.claude-plugin/marketplace.json`
   и в `.codex-plugin/plugin.json`.
   Меняли правила — правьте `llms.txt` и запустите `python3 scripts/sync_rules.py`
   (в навыках блок правил вручную не редактируют). Проверка навыков —
   `python3 scripts/validate_skills.py`.
2. Обновите `VERSIONS.md`: версию и дату в таблице и добавьте сверху раздел
   `### X.Y.Z (дата)` с изменениями. Первая строка раздела станет заголовком релиза
   (`vX.Y.Z — …`), остальное — описанием. Он публичный: пишите для пользователей, без имён.
3. Если менялось описание навыка (`description` в `SKILL.md`), обновите и его короткое описание
   в `packaging/claude-web-descriptions.json` — его видит claude.ai. Новому навыку тоже нужна
   строка в этом файле, иначе сборка архивов остановится с ошибкой.
4. Влейте PR в `main`. GitHub Actions сам поставит тег `vX.Y.Z`, соберёт архивы каждого навыка
   из коммита тега и создаст релиз; заметки возьмёт из `VERSIONS.md`. Пользователи узнают о
   новой версии из `VERSIONS.md` в `main` — поэтому версию поднимают в каждом PR, меняющем навыки.

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

## Лицензия

[MIT](LICENSE)
