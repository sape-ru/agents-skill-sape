# Agents skill: Sape Links SEO

Репозиторий для **Agent Skills** — портативных пакетов навыков по открытому стандарту
[Agent Skills](https://agentskills.io). Каждый навык — это папка с файлом `SKILL.md`
(с метаданными `name` + `description`) и опциональными `references/`, `scripts/`, `assets/`.
Любой совместимый агент может их загружать: Claude, OpenCode, Cursor, OpenAI Codex,
Gemini CLI и многие другие.

## Навыки

| Навык | Описание |
|-------|----------|
| [`sape-links-seo`](skills/sape-links-seo) | Покупка SEO-статей и ссылочных размещений на проверенных площадках-донорах через платформу Sape Links. |

---

## Sape Links SEO

Этот навык позволяет агенту автоматизировать закупку ссылочной массы через
[Sape](https://sape.ru): создавать проекты, искать и фильтровать площадки-доноры по
DR / трафику / цене / языку, загружать статьи, покупать размещения и управлять их
жизненным циклом. Требуется подключённый к агенту **Sape Links MCP-сервер**.

### Возможности

- Создание проектов для продвигаемых сайтов
- Поиск и фильтрация доноров (цена, DR, трафик, язык, метрики Majestic/Moz/Ahrefs/Semrush, …)
- Загрузка статей для модерации (формат `news`)
- Покупка четырёх типов размещений: `news`, `review`, `link`, `archive`
- Управление купленными размещениями (одобрение, отмена, расторжение, …) со встроенными финансовыми ограничениями

### 1. Подключите Sape Links MCP

Sape Links MCP — размещённый **streamable HTTP** сервер. Подключается только по URL —
аутентификация выполняется через встроенный OAuth-поток, поэтому токен API не нужно
вставлять в конфиг агента.

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

Навык — это папка `skills/sape-links-seo/`. Чтобы загрузить в агента, упакуйте её так, чтобы
**папка была корнем** архива (по спецификации Agent Skills):

```bash
zip -r sape-links-seo.zip skills/sape-links-seo
```

Затем, например в Claude, перейдите в *Customize → Skills* и загрузите архив. Другие агенты,
поддерживающие стандарт, принимают тот же пакет — см. список [Agent Skills clients](https://agentskills.io).

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
├── .gitignore
└── skills/sape-links-seo/                 # пакет навыка
    ├── SKILL.md                           # метаданные + инструкции workflow
    └── references/
        └── placement_actions.md           # справочник действий и статусов размещений
```

## Смотрите также

- [Стандарт Agent Skills](https://agentskills.io) — открытый формат, которому следуют эти навыки
- [Как создавать собственные навыки (Claude Help Center)](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- Документация API Sape Links: [https://api-links.sape.ru/api/](https://api-links.sape.ru/api/)
- Приложение Sape Links: [https://api-links.sape.ru](https://api-links.sape.ru)
