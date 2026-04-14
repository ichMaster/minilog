# Text Extraction — minilog extract

Перетворення текстів у бази знань minilog.

---

## Огляд

`minilog extract` — набір CLI-команд для перетворення текстів (URL, PDF, DOCX, EPUB тощо) у бази знань minilog. Phase 11 реалізує першу команду — `download`.

Повний workflow (Phases 11-14):
1. **download** — завантажити і конвертувати джерела в Markdown (Phase 11)
2. **detect-domains** — виявити предметні області через LLM (Phase 12)
3. **propose-schema** — запропонувати предикати через LLM (Phase 12)
4. **extract-facts** — витягти факти з тексту через LLM (Phase 13)
5. **propose-rules** / **generate-rules** — індукція правил (Phase 14)
6. **finalize** — зібрати knowledge_base.ml (Phase 14)

---

## Команда download

### Синтаксис

```bash
minilog extract download --name <name> --sources <source1,source2,...> [--title T] [--author A] [--language L]
```

### Параметри

| Параметр | Обов'язковий | Опис |
|----------|-------------|------|
| `--name` | Так | Назва папки книги |
| `--sources` | Так | Джерела через кому (URL або шлях до файлу) |
| `--title` | Ні | Перевизначити заголовок |
| `--author` | Ні | Перевизначити автора |
| `--language` | Ні | Перевизначити мову |

### Підтримувані формати

| Формат | Бібліотека | Як працює |
|--------|-----------|-----------|
| URL (http/https) | trafilatura | Витягує основний контент, видаляє навігацію/рекламу |
| PDF | pymupdf4llm | Конвертує з збереженням заголовків і таблиць |
| DOCX | python-docx | Зберігає заголовки Word як Markdown headings |
| EPUB | ebooklib + beautifulsoup4 | Об'єднує розділи з метаданими |
| TXT | stdlib | Копіює як є |
| HTML (файл) | trafilatura | Як URL, але з локального файлу |
| MD | stdlib | Копіює як є |

### Структура папки книги

Після `download` папка `knowledge_bases/<name>/` містить:

```
knowledge_bases/my_book/
  ├── source.md          # Об'єднаний Markdown усіх джерел
  ├── metadata.txt       # Метадані (назва, автор, мова, дата)
  ├── slug1.html         # Оригінал першого джерела
  ├── slug1.md           # Конвертований Markdown
  ├── slug2.pdf          # Оригінал другого джерела
  └── slug2.md           # Конвертований Markdown
```

### Об'єднання джерел

Якщо передано кілька джерел, всі конвертуються окремо, а потім об'єднуються в `source.md` з роздільниками `---`:

```markdown
% Source: https://example.com/article

[вміст першого джерела]

---

% Source: notes.pdf

[вміст другого джерела]
```

### Обробка помилок

- Дублікат назви: помилка, папка не створюється
- Помилка конвертації: повний rollback (папка видаляється)
- Неіснуючий файл: чітке повідомлення із шляхом
- Непідтримуваний формат: повідомлення з розширенням файлу

### Змінна середовища

`MINILOG_KB_DIR` — альтернативний шлях до папки баз знань (за замовчуванням `./knowledge_bases/`).

### Приклад

```bash
# Завантажити статтю з Wikipedia
minilog extract download --name prolog_article --sources https://en.wikipedia.org/wiki/Prolog

# Завантажити PDF + нотатки
minilog extract download --name my_notes --sources ./paper.pdf,./notes.txt --title "My Research"

# Перевірити результат
cat knowledge_bases/prolog_article/metadata.txt
cat knowledge_bases/prolog_article/source.md | head -20
```

---

## Команда detect-domains (Phase 12)

### Синтаксис

```bash
minilog extract detect-domains --name <name>
```

Читає `source.md` з папки книги, відправляє до LLM (Anthropic API) разом з каталогом ~25 вбудованих доменів. LLM визначає які домени присутні в тексті, з обґрунтуванням і прикладами.

**Вимоги:** змінна `ANTHROPIC_API_KEY` має бути встановлена.

**Результат:**
- `detected_domains.json` — JSON з виявленими доменами
- `domains.md` — звіт у Markdown
- `.session.json` — стан workflow

### Приклад

```bash
export ANTHROPIC_API_KEY=sk-ant-...
minilog extract detect-domains --name prolog_article
```

---

## Команда propose-schema (Phase 12)

### Синтаксис

```bash
minilog extract propose-schema --name <name> [--domains domain1,domain2]
```

Два кроки:
1. **Step 2a:** Для кожного обраного домену LLM пропонує minilog предикати (функтор, арність, ролі аргументів)
2. **Step 2b:** Для кожного предиката LLM шукає 2-3 конкретних приклади в тексті (grounding check)

**Результат:**
- `schema.ml` — запропоновані предикати як коментарі (grounded/theoretical)
- `grounding.json` — результати перевірки з цитатами
- `domains.md` — оновлений звіт зі статистикою grounding

---

---

## Команда extract-facts (Phase 13)

```bash
minilog extract extract-facts --name <name>
```

LLM читає `source.md` і витягує конкретні ground facts відповідно до схеми. Кожен факт має цитату з тексту. Великі тексти автоматично розбиваються на chunks. Результат валідується: перевіряється арність, наявність предиката в схемі, і чи цитата дійсно є в тексті.

**Результат:** `facts.ml` — файл з фактами та цитатами-коментарями.

---

## Команда propose-rules (Phase 14)

```bash
minilog extract propose-rules --name <name>
```

LLM аналізує витягнуті факти та схему і пропонує кандидатів на правила — закономірності, які можна виразити як minilog rules.

---

## Команда generate-rules (Phase 14)

```bash
minilog extract generate-rules --name <name> [--rules rule1,rule2]
```

Для кожного обраного кандидата LLM генерує конкретний minilog rule body. Правила валідуються парсером minilog.

**Результат:** `rules.ml` — файл зі згенерованими правилами.

---

## Команда finalize (Phase 14)

```bash
minilog extract finalize --name <name>
```

Об'єднує `schema.ml`, `facts.ml`, `rules.ml` у єдиний `knowledge_base.ml` з provenance header. Додає ontological profile до `domains.md`.

```bash
# Після finalize можна завантажити базу в REPL:
minilog repl knowledge_bases/my_book/knowledge_base.ml
```

---

## Повний workflow (end-to-end)

```bash
# 1. Завантажити текст
minilog extract download --name prolog --sources https://en.wikipedia.org/wiki/Prolog

# 2. Виявити домени
minilog extract detect-domains --name prolog

# 3. Запропонувати схему
minilog extract propose-schema --name prolog

# 4. Витягти факти
minilog extract extract-facts --name prolog

# 5. Запропонувати правила
minilog extract propose-rules --name prolog

# 6. Згенерувати правила
minilog extract generate-rules --name prolog

# 7. Фіналізувати
minilog extract finalize --name prolog

# 8. Запитати базу знань
minilog repl knowledge_bases/prolog/knowledge_base.ml
```

---

*Цей документ є частиною проекту minilog.*
