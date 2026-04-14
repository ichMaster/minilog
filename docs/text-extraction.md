# Text Extraction — minilog extract

Перетворення текстів у бази знань minilog.

---

## Огляд

`minilog extract` — набір CLI-команд для перетворення текстів (URL, PDF, DOCX, EPUB тощо) у бази знань minilog.

Повний workflow:
1. **download** — завантажити і конвертувати джерела в Markdown
2. **detect-domains** — виявити предметні області через LLM
3. **propose-schema** — запропонувати предикати через LLM з grounding check
4. **extract-facts** — витягти факти з тексту через LLM
5. **propose-rules** / **generate-rules** — індукція правил через LLM
6. **finalize** — зібрати фінальний `<name>.ml`
7. **run-all** — виконати кроки 2-7 однією командою
8. **clean** — видалити результати кроків 2-7, залишити джерела

---

## Структура папки книги

```
knowledge_bases/<name>/
  ├── <name>.md              # Об'єднаний Markdown усіх джерел
  ├── metadata.txt           # Метадані (назва, автор, мова, дата)
  ├── .session.json          # Стан workflow (автоматично)
  ├── source/                # Завантажені оригінали (Step 1)
  │   ├── slug.html          # Оригінал HTML
  │   ├── slug.md            # Конвертований Markdown
  │   ├── slug.pdf           # Оригінал PDF
  │   └── ...
  └── kb/                    # Результати extraction (Steps 2-7)
      ├── <name>.ml           # Фінальна база знань
      └── artifacts/          # Проміжні файли
          ├── detected_domains.json
          ├── domains.md
          ├── schema.ml
          ├── grounding.json
          ├── facts.ml
          └── rules.ml
```

---

## Команда download

```bash
minilog extract download --name <name> --sources <source1,source2,...> [--title T] [--author A] [--language L]
```

| Параметр | Обов'язковий | Опис |
|----------|-------------|------|
| `--name` | Так | Назва папки книги |
| `--sources` | Так | Джерела через кому (URL або шлях до файлу) |
| `--title` | Ні | Перевизначити заголовок |
| `--author` | Ні | Перевизначити автора |
| `--language` | Ні | Перевизначити мову |

### Підтримувані формати

| Формат | Бібліотека |
|--------|-----------|
| URL (http/https) | trafilatura |
| PDF | pymupdf4llm |
| DOCX | python-docx |
| EPUB | ebooklib + beautifulsoup4 |
| TXT | stdlib |
| HTML (файл) | trafilatura |
| MD | stdlib |

Завантажені оригінали зберігаються в `source/`, об'єднаний текст — в `<name>.md`.

### Обробка помилок

- Дублікат назви: помилка, папка не створюється
- Помилка конвертації: повний rollback (папка видаляється)
- Неіснуючий файл або непідтримуваний формат: чітке повідомлення

### Змінна середовища

`MINILOG_KB_DIR` — альтернативний шлях до папки баз знань (за замовчуванням `./knowledge_bases/`).

---

## Команда detect-domains

```bash
minilog extract detect-domains --name <name> [--min-relevance 0.5]
```

LLM читає `<name>.md` і визначає які предметні області присутні в тексті, з обґрунтуванням і прикладами. Результати фільтруються за `--min-relevance` (за замовчуванням 0.5).

**Вимоги:** `ANTHROPIC_API_KEY` в `.env` або як змінна середовища.

**Результат:** `kb/artifacts/detected_domains.json`, `kb/artifacts/domains.md`

---

## Команда propose-schema

```bash
minilog extract propose-schema --name <name> [--domains d1,d2] [--min-facts 5]
```

Два кроки:
1. **Step 2a:** Для кожного домену LLM пропонує 20-30 minilog предикатів
2. **Step 2b:** Для кожного предиката LLM шукає ВСІ приклади в тексті (grounding check). Предикати з менш ніж `--min-facts` прикладів відкидаються

**Результат:** `kb/artifacts/schema.ml`, `kb/artifacts/grounding.json`, `kb/artifacts/domains.md`

---

## Команда extract-facts

```bash
minilog extract extract-facts --name <name>
```

LLM витягує ground facts з тексту відповідно до схеми. Кожен факт має цитату. Великі тексти автоматично розбиваються на chunks. Валідація: арність, наявність предиката в схемі, цитата в тексті.

**Результат:** `kb/artifacts/facts.ml`

---

## Команда propose-rules

```bash
minilog extract propose-rules --name <name>
```

LLM аналізує факти та схему і пропонує кандидатів на правила.

---

## Команда generate-rules

```bash
minilog extract generate-rules --name <name> [--rules rule1,rule2]
```

Для кожного кандидата LLM генерує minilog rule body. Правила валідуються парсером.

**Результат:** `kb/artifacts/rules.ml`

---

## Команда finalize

```bash
minilog extract finalize --name <name>
```

Об'єднує `schema.ml`, `facts.ml`, `rules.ml` у фінальний `kb/<name>.ml`. Додає ontological profile до `domains.md`.

```bash
# Завантажити базу в REPL:
minilog repl knowledge_bases/prolog/kb/prolog.ml
```

---

## Команда run-all

```bash
minilog extract run-all --name <name> [--min-relevance 0.5] [--min-facts 5]
```

Виконує всі кроки 2-7 послідовно однією командою. Зупиняється при першій помилці.

---

## Команда clean

```bash
minilog extract clean --name <name>
```

Видаляє `kb/` та `.session.json`. Залишає тільки результати Step 1: `source/`, `<name>.md`, `metadata.txt`. Корисно для перезапуску extraction pipeline з нуля.

---

## Повний workflow (end-to-end)

```bash
# 1. Завантажити текст
minilog extract download --name prolog --sources https://en.wikipedia.org/wiki/Prolog

# 2-7. Запустити весь pipeline
minilog extract run-all --name prolog

# Або покроково:
minilog extract detect-domains --name prolog --min-relevance 0.6
minilog extract propose-schema --name prolog --min-facts 10
minilog extract extract-facts --name prolog
minilog extract propose-rules --name prolog
minilog extract generate-rules --name prolog
minilog extract finalize --name prolog

# 8. Запитати базу знань
minilog repl knowledge_bases/prolog/kb/prolog.ml

# Перезапустити з нуля (зберігаючи завантажене):
minilog extract clean --name prolog
minilog extract run-all --name prolog
```

---

*Цей документ є частиною проекту minilog.*
