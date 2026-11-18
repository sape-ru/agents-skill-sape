# Инструменты Sape Links MCP

Снимок `tools/list` с `https://mcp-links.sape.ru/mcp` (версия сервера 2.0.0) от 2026-11-13. Источник истины — живой список инструментов в вашей сессии: берите оттуда точные имена параметров. `*` — обязательный параметр. У всех инструментов с параметрами они передаются в одном объекте `args`.

## Проекты, URL и контент

| Инструмент | Что делает | Параметры |
|---|---|---|
| `list_projects` | Список проектов с пагинацией, сортировкой и фильтрами; без аргументов — первая страница | `page`, `limit`, `order_by`, `order_type`, `project_filter`, `projects_ids` |
| `create_project` | Создать проект для домена; заодно создаёт первый URL и анкор по умолчанию | `domain`*, `name` |
| `add_article` | Загрузить статью рекламодателя (формат «Статья», `news`); возвращает `articleId` и `urlId` | `project_id`*, `url`*, `title`*, `body`*, `meta_title`*, `meta_description`, `meta_keywords`, `is_comments_disabled`, `limit_max_usages` |
| `add_texts` | Добавить продвигаемые URL с анкорами (`#a#...#/a#`); возвращает `urlId` и ID текстов | `project_id`*, `urls_texts`* (`url`, `texts[].text`, `keywords`) |
| `get_project_content_list` | Статьи и тексты проекта: статусы, тип, URL, поиск по подстроке | `project_id`, `creation_source`, `substring_text`, `url_ids`, `content_type`, `status`, `content_status_ids`, `from`, `limit`, `order_by`, `order_direction`, `async_url_id`, `show_async_content_load` |
| `set_limits` | Лимит использования анкоров — по ID контента или для всех анкоров URL; `0` — без ограничений | `content_ids`, `url_id`, `limit` |
| `update_url` | Изменить продвигаемый URL: адрес, название, скрытие ссылок от поисковиков. `url` обязателен — если не меняется, передайте текущий | `url_id`*, `url`*, `name`, `link_decoration` |

## Поиск

| Инструмент | Что делает | Параметры |
|---|---|---|
| `search_sites` | Доноры для статейных размещений (`link_type`: `news`, `review`, `link`, `archive`) | `project_id`*, `link_type`*, `page`, `limit`, `order_by`, `order_type`, `price_from`, `price_to`, `language`, `majestic_cf_*`, `majestic_tf_*`, `moz_da_*`, `moz_page_rank_*`, `moz_page_authority_*`, `moz_spam_score_*`, `external_links_to`, `domain_level`, `days_old_whois_from`, `ahrefs_dr_*`, `ahrefs_backlinks_*`, `ahrefs_keywords_*`, `keywords`, `donor_domain`, `avg_placement_time_*`, `placement_probability_*`, `pages_google_*`, `semrush_as_*`, `semrush_domains_*`, `traffic_semrush_from`, `traffic_ahrefs_from`, `favorite_lists_ids`, `is_in_favorite_lists` |
| `search_rent_sites` | Доноры для арендных блочных ссылок, по URL; асинхронный, до ~150 с. Возвращает `data.resultList` со страницами (`pages[].id`) и значения `searchId`, `forceSeoWait`, `mosSites`, `pagesExtra` | `url_id`*, `price_rent_*`, `yandex_sqi_*`, `majestic_cf_*`, `majestic_tf_*`, `moz_da_*`, `moz_spam_score_*`, `ahrefs_dr_*`, `ahrefs_backlinks_*`, `ahrefs_keywords_*`, `semrush_as_*`, `traffic_semrush_from`, `traffic_ahrefs_from`, `traffic_system_from`, `traffic_yandex_from`, `domain_level`, `site_languages`, `domain_zones`, `keywords`, `donor_domain`, `external_links_to`, `days_old_whois_from`, `avg_placement_time_*`, `placement_probability_*`, `nof_pages_google_*`, `nof_pages_yandex_*`, `is_credit_available`, `favorite_lists_ids`, `is_in_favorite_lists`, `search_rent_order`, `page`, `limit` |
| `search_context_sites` | Доноры для арендных контекстных ссылок, по URL и ключевым словам; асинхронный. У страниц есть `snippets[]` — фрагменты текста, куда можно вставить ссылку | `url_id`*, `keywords`*, остальные — как у `search_rent_sites` |
| `get_site_info` | Карточка площадки: метрики, цены по форматам, статус, языки, статистика, Избранное | `site_id`* |

`*_from` / `*_to` — границы диапазона; `_*` в таблице означает оба.

## Избранное

| Инструмент | Что делает | Параметры |
|---|---|---|
| `favorites_add_list` | Создать список; возвращает его ID | `name`* |
| `favorites_get_lists` | Все списки с количеством доменов | — |
| `favorites_rename_list` | Переименовать список | `list_id`*, `list_name`* |
| `favorites_delete_list` | Удалить список; `is_delete_sites=false` (по умолчанию) переносит домены в общий список | `list_id`*, `is_delete_sites` |
| `favorites_get_domains` | Домены списка по секциям, с пагинацией и фильтрами | `favorite_list_id`*, `page`, `limit`, `order_name`, `domain_zones`, `is_available_to_buy` |
| `favorites_add_domains` | Добавить домены в списки по ID доменов, ID сайтов или именам | `lists_ids`*, `domains_ids`, `sites_ids`, `domains_names` |
| `favorites_delete_domains` | Убрать домены; без `list_ids` — из всех списков | `domain_ids`*, `list_ids` |
| `favorites_move_domains` | Перенести домены между списками | `domain_ids`*, `from_list_id`*, `to_list_id`* |

## Чёрный список

| Инструмент | Что делает | Параметры |
|---|---|---|
| `blacklist_get` | Домены чёрного списка по секциям; по умолчанию общий, с `project_id` — проекта | `project_id`, `page`, `limit`, `order_type` |
| `blacklist_add_domains` | Добавить домены по ID и/или именам; с `project_ids` — в списки проектов. Возвращает результат по каждому домену | `domains_ids`, `domains_names`, `project_ids` |
| `blacklist_delete_domains` | Убрать домены (только по `domainId` из `blacklist_get`); с `project_ids` — только из списков проектов | `domain_ids`*, `project_ids` |

## Покупка — тратит деньги

| Инструмент | Что делает | Параметры |
|---|---|---|
| `purchase_placement` | Купить статейное размещение на площадке | `project_id`*, `site_id`*, `link_type`*, `url_id`, `text_id`, `article_id`, `search_history_id` (всегда `""`), `is_content_need_approval` |
| `purchase_rent_placement` | Купить арендные блочные ссылки на страницах из `search_rent_sites`; значения `search_id`, `force_seo_wait`, `mos_sites`, `pages_extra` — из того же поиска; каждая страница — `page_id`, `url_id`, `text_id` | `project_id`*, `search_id`*, `force_seo_wait`, `mos_sites`, `pages_extra`, `pages`*, `link_type_id` (по умолчанию `1`; не меняйте) |
| `purchase_context_placement` | Купить контекстные ссылки на страницах из `search_context_sites`; каждая страница — `page_id`, `url_id`, `text` (анкор из фрагмента дословно, без `#a#`), `full_text` (фрагмент без изменений, с тегами) | `project_id`*, `search_id`*, `force_seo_wait`, `mos_sites`, `pages_extra`, `pages`* |

## Размещения и аккаунт

| Инструмент | Что делает | Параметры |
|---|---|---|
| `get_project_placements` | Все размещения проекта со статусами | `project_id`* |
| `perform_placement_action` | Действие над размещениями (одобрить, отменить, заморозить…). Может двигать деньги — см. [placement_actions.md](placement_actions.md) | `action`*, `placement_ids`* |
| `get_user_info` | Пользователь, баланс (`balance`), счётчики `seoCounters`. Пополнение — https://passport.sape.ru/deposit/ | — |
