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

*Цей документ є частиною проекту minilog. Phases 12-14 додадуть LLM-powered команди для виявлення доменів, витягування фактів і індукції правил.*
