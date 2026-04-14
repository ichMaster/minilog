# Text Extraction — minilog extract

Перетворення текстів у бази знань minilog.

---

## Огляд

`minilog extract` — набір CLI-команд для перетворення текстів (URL, PDF, DOCX, EPUB тощо) у бази знань minilog.

Повний workflow:

| Step | Команда | Опис |
|------|---------|------|
| 1 | `download` | Завантажити і конвертувати джерела в Markdown |
| 2 | `detect-domains` | Виявити предметні області через LLM |
| 3 | `propose-schema` | Запропонувати предикати через LLM з grounding check |
| 4 | `extract-facts` | Витягти факти з тексту через LLM |
| 5 | `propose-rules` | Запропонувати кандидатів на правила через LLM |
| 6 | `generate-rules` | Згенерувати rule bodies через LLM |
| 7 | `finalize` | Зібрати фінальний `<name>.ml` |
| — | `run-all` | Виконати Steps 2-7 однією командою |
| — | `clean` | Видалити результати Steps 2-7, залишити джерела |

---

## Структура папки книги

```
knowledge_bases/<name>/
  ├── <name>.md              # Об'єднаний Markdown усіх джерел (Step 1)
  ├── metadata.txt           # Метадані (Step 1)
  ├── .session.json          # Стан workflow (автоматично)
  ├── source/                # Завантажені оригінали (Step 1)
  │   ├── slug.html
  │   ├── slug.md
  │   └── ...
  └── kb/                    # Результати extraction
      ├── <name>.ml           # Фінальна база знань (Step 7)
      └── artifacts/          # Проміжні файли (Steps 2-6)
          ├── detected_domains.json  (Step 2)
          ├── domains.md             (Step 2, 3, 7)
          ├── schema.ml              (Step 3)
          ├── grounding.json         (Step 3)
          ├── facts.ml               (Step 4)
          └── rules.ml               (Step 6)
```

---

## Step 1: download

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

## Step 2: detect-domains

```bash
minilog extract detect-domains --name <name> [--min-relevance 0.5]
```

LLM читає `<name>.md` і визначає які предметні області присутні в тексті, з обґрунтуванням і прикладами. Результати фільтруються за `--min-relevance` (за замовчуванням 0.5).

**Вимоги:** `ANTHROPIC_API_KEY` в `.env` або як змінна середовища.

**Результат:** `kb/artifacts/detected_domains.json`, `kb/artifacts/domains.md`

---

## Step 3: propose-schema

```bash
minilog extract propose-schema --name <name> [--domains d1,d2] [--min-facts 5]
```

Два підкроки:
- **Step 3a:** Для кожного домену LLM пропонує 20-30 minilog предикатів
- **Step 3b:** Для кожного предиката LLM шукає ВСІ приклади в тексті (grounding check). Предикати з менш ніж `--min-facts` прикладів відкидаються

**Результат:** `kb/artifacts/schema.ml`, `kb/artifacts/grounding.json`, `kb/artifacts/domains.md`

---

## Step 4: extract-facts

```bash
minilog extract extract-facts --name <name>
```

LLM витягує ground facts з тексту відповідно до схеми. Кожен факт має цитату. Великі тексти автоматично розбиваються на chunks. Валідація: арність, наявність предиката в схемі, цитата в тексті.

**Результат:** `kb/artifacts/facts.ml`

---

## Step 5: propose-rules

```bash
minilog extract propose-rules --name <name>
```

LLM аналізує факти та схему і пропонує кандидатів на правила.

---

## Step 6: generate-rules

```bash
minilog extract generate-rules --name <name> [--rules rule1,rule2]
```

Для кожного кандидата LLM генерує minilog rule body. Правила валідуються парсером.

**Результат:** `kb/artifacts/rules.ml`

---

## Step 7: finalize

```bash
minilog extract finalize --name <name>
```

Об'єднує `schema.ml`, `facts.ml`, `rules.ml` у фінальний `kb/<name>.ml`. Додає ontological profile до `domains.md`.

```bash
# Завантажити базу в REPL:
minilog repl knowledge_bases/prolog/kb/prolog.ml
```

---

## run-all (Steps 2-7)

```bash
minilog extract run-all --name <name> [--min-relevance 0.5] [--min-facts 5]
```

Виконує Steps 2-7 послідовно однією командою. Зупиняється при першій помилці.

---

## clean

```bash
minilog extract clean --name <name>
```

Видаляє `kb/` та `.session.json`. Залишає тільки результати Step 1: `source/`, `<name>.md`, `metadata.txt`. Корисно для перезапуску extraction pipeline з нуля.

---

## Повний workflow (end-to-end)

```bash
# Step 1: Завантажити текст
minilog extract download --name prolog --sources https://en.wikipedia.org/wiki/Prolog

# Steps 2-7: Запустити весь pipeline
minilog extract run-all --name prolog

# Або покроково:
minilog extract detect-domains --name prolog --min-relevance 0.6   # Step 2
minilog extract propose-schema --name prolog --min-facts 10        # Step 3
minilog extract extract-facts --name prolog                        # Step 4
minilog extract propose-rules --name prolog                        # Step 5
minilog extract generate-rules --name prolog                       # Step 6
minilog extract finalize --name prolog                             # Step 7

# Запитати базу знань
minilog repl knowledge_bases/prolog/kb/prolog.ml

# Перезапустити з нуля (зберігаючи завантажене):
minilog extract clean --name prolog
minilog extract run-all --name prolog
```

---

*Цей документ є частиною проекту minilog.*
