# Контекст для нового чату: генерація книги "Formal Axiomatic Layers over LLM Prompts"

**Призначення:** цей файл містить увесь контекст для продовження генерації 50+ сторінкового ресерч-документа у новому чаті. Прочитайте його повністю перед початком роботи.

**ВАЖЛИВО:** у новому чаті перш за все створіть папку `~/development/minilog/docs/research/` (через bash: `mkdir -p /Users/Vitalii_Bondarenko2/development/minilog/docs/research`) і перемістіть туди цей файл. Далі всі файли книги зберігаються там.

---

## 1. Перше повідомлення для нового чату (скопіюйте у новий чат)

> Привіт. Ми продовжуємо роботу над великим ресерч-документом "Formal Axiomatic Layers as Interpreted Reasoners over LLM Prompts" (50+ сторінок українською).
>
> Повний контекст у файлі `/Users/Vitalii_Bondarenko2/development/minilog/docs/CONTEXT-for-new-chat.md`. Прочитай його повністю перш ніж починати — там усі прийняті рішення, повний зміст на 26 розділів, бібліографія на 55 джерел, стилістичні вимоги, заборони.
>
> Після того як прочитаєш:
> 1. Створи папку `~/development/minilog/docs/research/` і перемісти туди контекст-файл
> 2. Підтверди коротко, що зрозумів задачу
> 3. Напиши **Частину I** (розділи 1-4, ~8-10 сторінок) повним текстом
> 4. Збережи локально як `~/development/minilog/docs/research/part-01-foundations.md`
> 5. Опублікуй у Notion як дочірню сторінку [Formal Axiomatic Layers over LLM Prompts — TOC and Literature Review](https://www.notion.so/340d36341fb38181a3c1c5c59b24fe35)
> 6. Покажи короткий підсумок і зачекай на "продовжуй" перш ніж писати Частину II
>
> Мова: українська з англійськими технічними термінами. Без emoji. Без згадок про minilog, Codex, migVisor, Terra Tacita. Повний working code у Частині IV.

---

## 2. Тема і центральна теза

**Назва:** "Formal Axiomatic Layers as Interpreted Reasoners over LLM Prompts"

**Обсяг:** 50+ сторінок (орієнтовно 55-57 з бібліографією).

**Центральна теза:** LLM використовується НЕ як джерело логічних висновків, а як двомовний перекладач між природною мовою і формальною системою. Власне виведення виконується зовнішнім детермінованим движком (Prolog, Datalog, SMT-solver, ASP, theorem prover), який має аксіоми, дерево доведення, фальсифікованість і детермінізм. LLM заходить у pipeline двічі: (1) спереду — парсинг natural language у формальні факти і запити; (2) ззаду — переклад proof tree на природну мову. Ядро reasoning-у — символічне і перевірне.

**Чому це важливо:** прямий результат на фундаментальні обмеження чистих LLM (галюцинації, непрозорість, недетермінізм, вразливість до prompt injection). Патерн не новий концептуально (коріння у Logic-LM 2023, LINC 2023), але став жвавим напрямком саме у 2024-2025 з появою систем ATA, Aristotle, LoRP, SOLAR, CLOVER.

---

## 3. Прийняті рішення (ПІДТВЕРДЖЕНО користувачем)

| Питання | Рішення |
|---|---|
| **Мова документа** | Змішана: основний текст українською, технічні терміни/назви статей/цитати/код англійською. Стиль як у `docs/prolog-state-2025.md` |
| **Глибина коду у Частині IV** | Повноцінні working examples 60-100 рядків з output-ами |
| **Зв'язок з minilog roadmap** | **БЕЗ зв'язку.** Документ чисто академічний. Жодних згадок про minilog, Codex Seraphinianus, migVisor, Terra Tacita |
| **Emoji** | Заборонені скрізь (глобальне правило користувача) |
| **Робоча папка** | `/Users/Vitalii_Bondarenko2/development/minilog/docs/research/` |
| **Порядок написання** | Послідовно I → II → III → IV → V → VI → VII, з паузами після кожної частини |

---

## 4. Повний зміст документа (ЗАТВЕРДЖЕНО)

### Частина I. Основи (~8 сторінок)

**Розділ 1. Проблема: чому LLM самі не можуть reasoning**
- Фундаментальні обмеження Трансформерів для символічного reasoning
- Галюцинації логічних висновків — емпіричні докази з бенчмарків (FOLIO, ProverQA)
- Нестабільність між запусками, чутливість до формулювання промпту
- Вразливість до prompt injection атак
- Недетермінізм як проблема в regulated domains
- Позиція Гері Маркуса: "must have the machinery of symbol manipulation"
- Shojaee et al. 2025 про низько-, середньо- і високоскладні режими reasoning

**Розділ 2. Що таке формальна аксіоматична система**
- Аксіоми як правила першого класу
- Теореми як виведення з аксіом
- Proof tree як артефакт першого класу
- Різниця між дедукцією і індукцією
- Детермінізм, монотонність, фальсифікованість
- Коротка історія: Euclid → Hilbert → Robinson → Kowalski
- Чому формальні системи дають саме те, чого бракує LLM

**Розділ 3. Prolog як еталонна аксіоматична мова**
- Horn clauses як обмеження First-Order Logic
- Unification, backtracking, SLD resolution
- Факти + правила + запити — повна програма в Пролозі
- Proof trees через `trace/0` і tabling
- Обмеження чистого Прологу — cut, negation-as-failure, performance
- Сучасний Prolog 2025: SWI-Prolog 9.3.x, Scryer, Trealla (короткий огляд)

**Розділ 4. Datalog, ASP, SMT — родина формальних reasoner-ів**
- Datalog як підмножина Прологу з гарантованою термінацією. Soufflé, Datomic, LogicBlox
- Answer Set Programming (ASP) — стабільні моделі. Clingo, DLV
- SMT solvers — Z3, cvc5. Логічні теорії
- Theorem provers — Lean, Coq, Isabelle, Prover9
- Порівняльна таблиця: виразність, термінація, продуктивність

### Частина II. Архітектурні патерни (~8 сторінок)

**Розділ 5. Патерн 1: LLM-as-Parser → Symbolic Solver**
- Базова схема, приклади з Logic-LM, LINC
- Переваги: faithfulness, verifiability, детермінізм
- Обмеження: якість залежить від точності перекладу
- Ілюстративний код на Python

**Розділ 6. Патерн 2: Verifier-over-Generator**
- LLM генерує, solver перевіряє
- SATLM, CLOVER, R2-Guard
- Roll-back при провалі верифікації

**Розділ 7. Патерн 3: Iterative Refinement Loop**
- LLM пропонує → solver виявляє помилку → LLM виправляє
- Logic-LM++, Logic-of-Thought
- Збіжність і критерії термінації

**Розділ 8. Патерн 4: Multi-Agent System з Symbolic Oracle**
- Кілька LLM-агентів з рольовим поділом
- SOLAR (CIKM 2025), ATA (2025)
- Parser, reasoner, explainer, verifier

**Розділ 9. Патерн 5: Neural Predicates (DeepProbLog spirit)**
- Нейронна мережа ВСЕРЕДИНІ символічного движка
- DeepProbLog (Manhaeve et al. NeurIPS 2018)
- Neural predicates як ймовірнісні факти
- End-to-end gradient flow через solver

### Частина III. Огляд ключових систем 2023-2025 (~10 сторінок)

**Розділ 10. Пробудження (2023): Logic-LM, LINC, Faithful CoT, SATLM**
- Logic-LM (Pan et al., EMNLP 2023) — landmark
- LINC (Olausson et al., EMNLP 2023) — majority voting
- Faithful Chain-of-Thought (Lyu et al., IJCNLP-AACL 2023)
- SATLM (Ye et al., NeurIPS 2023)
- Результати на FOLIO, ProofWriter, bAbI

**Розділ 11. Розвиток (2024): Logic-LM++, Thought-Like-Pro, Chatlogic**
- Logic-LM++ (Kirtania et al., ACL 2024)
- Thought-Like-Pro (Tan et al., 2024)
- Chatlogic (Wang et al., 2024)
- LLM+P (Liu et al., 2023)

**Розділ 12. Зрілість (2025): Aristotle, CLOVER, LoRP, SOLAR, ATA**
- Aristotle (ACL 2025)
- CLOVER (ICLR 2025)
- ProverGen/ProverQA (ICLR 2025)
- LoRP (Di et al., Knowledge-Based Systems 327, 2025)
- SOLAR (CIKM 2025)
- ATA (arxiv 2510.16381, 2025)
- R2-Guard (ICLR 2025)

**Розділ 13. Суміжні гілки: ASP, FOL verifiers, theorem provers**
- Ishay et al. ASP generation (KR 2023)
- SymBa
- Lean Copilot (2024)
- DeepSeek-Prover-V2 (2025)
- Logic-infused KG QA (2025)

### Частина IV. Практична імплементація з кодом (~10 сторінок, НАЙВАЖЧА)

**Розділ 14. Приклад 1: Prolog + LLM pipeline на Python**
- Повний working example: user question → LLM-as-parser → Prolog query → LLM-as-explainer → response
- Використання pyswip (SWI-Prolog bridge)
- Обробка помилок, retry loop
- Domain: family tree або medical diagnosis

**Розділ 15. Приклад 2: SMT (Z3) + LLM для constraint planning**
- Реалізація підходу з Hao et al. 2024 (TravelPlanner)
- Повний Python скрипт з Z3
- LLM генерує SMT-LIB constraints
- Unsatisfiable core як пояснення
- Interactive plan repair

**Розділ 16. Приклад 3: ASP (Clingo) + LLM**
- Переваги ASP: stable model semantics, defaults, exceptions
- LLM генерує Clingo program
- Non-monotonic reasoning
- Приклад: автомобільна діагностика

**Розділ 17. Приклад 4: Custom Prolog engine як formal axiomatic layer**
- ВАЖЛИВО: говорити про "custom Prolog interpreter" або "educational Prolog engine" абстрактно. НЕ згадувати minilog
- Case study на загальній задачі класифікації
- Python pipeline

**Розділ 18. Патерни проектування на практиці**
- Коли Prolog/Datalog (deterministic rules)
- Коли Z3/SMT (arithmetic constraints)
- Коли ASP (defaults, non-monotonicity)
- Коли DeepProbLog (probabilistic facts)
- Антипатерни

### Частина V. Evaluation і бенчмарки (~5 сторінок)

**Розділ 19. Ключові бенчмарки**
- FOLIO (Han et al. 2024)
- ProverQA (ICLR 2025)
- ProofWriter
- TravelPlanner
- NeuBAROCO (ACL 2024)
- Порівняльна таблиця

**Розділ 20. Метрики для формальних layers**
- Accuracy vs Faithfulness
- Proof tree quality
- Детермінізм: pass@k vs pass∧k
- Robustness до paraphrasing
- Стійкість до prompt injection (ATA 2025)

### Частина VI. Застосування в регульованих доменах (~5 сторінок)

**Розділ 21. Юриспруденція**
- Stanford Law "Breakthroughs in LLM Reasoning..." (Dec 2024)
- SOLAR (CIKM 2025)
- Audit trail для court

**Розділ 22. Медицина і клінічні рішення**
- ArgMed-Agents (BIBM 2024)
- Інтеграція з SNOMED CT, UMLS
- Чому hallucinations неприйнятні

**Розділ 23. Enterprise і промислові застосування**
- Amazon Bedrock LLM Guardrails
- Amazon Vulcan warehouse robots (2025)
- Tool-use policies як SMT constraints
- ВАЖЛИВО: НЕ згадувати migVisor. Говорити про enterprise data integration абстрактно

### Частина VII. Відкриті проблеми і майбутнє (~5 сторінок)

**Розділ 24. Відкриті проблеми**
- Масштабованість KB
- Обмежена виразність Horn clauses vs повна FOL
- Якість LLM-as-parser
- Коли аксіоми неповні або суперечливі
- Автоматичне вивчення аксіом
- Meta-cognition

**Розділ 25. Напрямки 2026+**
- Гібриди SMT+Datalog+LLM
- Adaptive axiom selection
- Foundation models з native formal output
- Explainability standards
- Зв'язок з constitutional AI

**Розділ 26. Висновки**
- Підсумок що таке formal axiomatic layer
- Дорожня карта для практика
- Фінальна думка: це не повернення до символічного AI 1980-х, це третя хвиля
- ВАЖЛИВО: без згадок про minilog roadmap

---

## 5. Повна бібліографія (55 джерел)

### Survey papers (5)
1. **A Survey on LLM Symbolic Reasoning** (Li et al., 2025, under review). https://github.com/jindongli-Ai/LLM-Symbolic-Reasoning-Survey
2. **Advancing Symbolic Integration in Large Language Models: Beyond Conventional Neurosymbolic AI** (arxiv 2510.21425, Oct 2025)
3. **Neuro-Symbolic AI in 2024: A Systematic Review** (arxiv 2501.05435)
4. **A Comprehensive Review of Neuro-symbolic AI for Robustness, UQ, and Intervenability** (Arabian Journal Science Engineering, 2025)
5. **Neuro-Symbolic Artificial Intelligence: Towards Improving the Reasoning Abilities of LLMs** (IJCAI 2025 Survey)

### Foundational papers LLM + symbolic reasoning (10)
6. **Logic-LM: Empowering LLMs with Symbolic Solvers for Faithful Logical Reasoning** (Pan et al., EMNLP 2023)
7. **LINC: A Neurosymbolic Approach for Logical Reasoning by Combining LMs with First-Order Logic Provers** (Olausson et al., EMNLP 2023)
8. **LOGIC-LM++: Multi-Step Refinement for Symbolic Formulations** (Kirtania et al., ACL 2024)
9. **Faithful Chain-of-Thought Reasoning** (Lyu et al., IJCNLP-AACL 2023)
10. **SATLM: Satisfiability-Aided Language Models Using Declarative Prompting** (Ye et al., NeurIPS 2023)
11. **Leveraging LLMs to Generate Answer Set Programs** (Ishay et al., KR 2023)
12. **LLM+P: Empowering Large Language Models with Optimal Planning Proficiency** (Liu et al., 2023)
13. **LLM-DM: LLMs as World Models for Planning** (Guan et al., 2023)
14. **MRKL Systems** (Karpas et al., arxiv 2022)
15. **Program-Aided Language Models (PAL)** (Gao et al., ICML 2023)

### Системи 2024-2025 (15)
16. **Thought-Like-Pro: Self-Driven Prolog-based Chain-of-Thought** (Tan et al., arxiv 2407.14562, 2024)
17. **Chatlogic: Integrating logic programming with LLMs** (Wang et al., 2024)
18. **LoRP: LLM-based Logical Reasoning via Prolog** (Di et al., Knowledge-Based Systems 327, 2025)
19. **Logic-infused knowledge graph QA** (Bashir et al., Data & Knowledge Engineering 157, 2025)
20. **Aristotle: Mastering Logical Reasoning with A Logic-Complete Decompose-Search-Resolve Framework** (ACL 2025)
21. **CLOVER: Compositional FOL Translation and Verification** (ICLR 2025)
22. **ProverGen / ProverQA** (ICLR 2025)
23. **SOLAR: On Verifiable Legal Reasoning** (CIKM 2025)
24. **ATA: A Neuro-Symbolic Approach to Autonomous and Trustworthy Agents** (arxiv 2510.16381, Oct 2025)
25. **R2-Guard: Robust Reasoning Enhanced LLM Guardrail** (ICLR 2025)
26. **SymBa: Symbolic Backward Chaining** (2025)
27. **Neuro-Symbolic Integration Brings Causal and Reliable Reasoning Proofs** (2024)
28. **Improving Rule-based Reasoning in LLMs using Neurosymbolic** (EMNLP 2025)
29. **An Evaluation of Open Source LLMs for Neuro-Symbolic Integration** (CILC 2025)
30. **Symbolic ReAct: Enhancing Logical Reasoning via Symbolically-Guided MCTS** (Tan et al., EMNLP 2025)

### LLM + SMT/SAT planning (5)
31. **Large Language Models Can Solve Real-World Planning Rigorously with Formal Verification Tools** (Hao et al., arxiv 2404.11891, NAACL 2025). TravelPlanner 93.9% vs 10% baseline
32. **Planning Anything with Rigor: LLM-based Formalized Programming** (arxiv 2410.12112)
33. **Solver-Aided Verification of Policy Compliance in Tool-Augmented LLM Agents** (2026)
34. **Broken by Default: Formal Verification Study of Security Vulnerabilities in AI-Generated Code** (2026)
35. **AutoTAMP: Autoregressive Task and Motion Planning with LLMs as Translators and Checkers** (Chen et al., 2023)

### DeepProbLog і ймовірнісне LP (5)
36. **DeepProbLog: Neural Probabilistic Logic Programming** (Manhaeve et al., NeurIPS 2018)
37. **Neural Probabilistic Logic Programming in DeepProbLog** (Manhaeve et al., Artificial Intelligence, 2021)
38. **SLASH: Embracing the Power of Neural-Probabilistic Circuits** (Skryagin et al., 2022)
39. **From Statistical Relational to Neurosymbolic AI: A Survey** (Marra, Dumančić, Manhaeve, De Raedt, 2024)
40. **Adaptable Logical Control for Large Language Models** (Zhang et al., NeurIPS 2024)

### Бенчмарки (5)
41. **FOLIO: Natural Language Reasoning with First-Order Logic** (Han et al., 2024)
42. **ProofWriter** (Tafjord et al., 2020)
43. **ProverQA** (ICLR 2025)
44. **TravelPlanner** (Xie et al., 2024)
45. **NeuBAROCO: Dataset for Syllogism Reasoning Biases** (ACL 2024)

### Applied і domain-specific (5)
46. **Breakthroughs in LLM Reasoning for Neuro-symbolic Legal AI** (Stanford Law, Dec 2024)
47. **ArgMed-Agents: Explainable Clinical Decision Reasoning** (BIBM 2024)
48. **Logic-infused KG QA for specialized domains** (Data & Knowledge Engineering 2025)
49. **Integrating LLM and Logic Programming for Renewable Energy Supply Chain Tracing** (MDPI 2025)
50. **Amazon Bedrock Guardrails** — industrial deployment

### Foundational background (5)
51. **DeepMind AlphaGeometry** (Trinh et al., Nature 2024)
52. **MIT-IBM Neuro-Symbolic Concept Learner (NSCL)**
53. **Gary Marcus, "The Next Decade in AI"**
54. **Kautz's Taxonomy of Neuro-Symbolic AI** (IJCAI 2020)
55. **Monitor-Guided Decoding of Code LMs with Static Analysis** (NeurIPS 2023)

---

## 6. Оцінка обсягу

| Частина | Розділи | Обсяг |
|---|---|---|
| I. Основи | 1-4 | ~8 стор |
| II. Архітектурні патерни | 5-9 | ~8 стор |
| III. Ключові системи 2023-2025 | 10-13 | ~10 стор |
| IV. Практична імплементація | 14-18 | ~10 стор (з кодом) |
| V. Evaluation і бенчмарки | 19-20 | ~5 стор |
| VI. Застосування в доменах | 21-23 | ~5 стор |
| VII. Відкриті проблеми і висновки | 24-26 | ~5 стор |
| + бібліографія, index | | ~4-5 стор |
| **Повний обсяг** | 26 розділів | **~55-57 стор** |

---

## 7. Workflow для нового чату

**Важливо:** 50+ сторінок не пишеться за одне повідомлення. Підхід — частина за частиною.

**Процес на кожну частину:**

1. Написати повний текст частини (8-10 сторінок) у markdown
2. Зберегти локально як `~/development/minilog/docs/research/part-NN-name.md`
3. Опублікувати у Notion як дочірню сторінку TOC-документа
4. Показати короткий підсумок (не повторювати текст, лише структуру)
5. Зачекати на "продовжуй" перш ніж переходити до наступної частини

**Порядок:** послідовно I → II → III → IV → V → VI → VII.

**Локації файлів:**
- Локально: `/Users/Vitalii_Bondarenko2/development/minilog/docs/research/part-NN-name.md`
- Notion: дочірні сторінки під TOC-документом https://www.notion.so/340d36341fb38181a3c1c5c59b24fe35

**Імена файлів:**
- `part-01-foundations.md`
- `part-02-architectural-patterns.md`
- `part-03-systems-2023-2025.md`
- `part-04-practical-implementation.md`
- `part-05-evaluation.md`
- `part-06-regulated-domains.md`
- `part-07-open-problems.md`

---

## 8. Стилістичні вимоги

**Мова:**
- Основний текст — українська, природна, без калькувань
- Технічні терміни — англійською (unification, backtracking, proof tree, chain-of-thought, few-shot prompting, faithfulness)
- Назви статей і систем — завжди англійською, жирним при першій згадці
- Цитати з джерел — англійською, в blockquote, з атрибуцією
- Код — завжди англійською (Python, Prolog, SMT-LIB)
- Коментарі в коді — англійською

**Форматування:**
- H1 для частин, H2 для розділів, H3 для підрозділів
- Таблиці для порівняльних характеристик
- Code blocks з fence ``` та вказанням мови
- Жирний для назв систем, курсив для іншомовних термінів
- **БЕЗ emoji будь-де**

**Стиль викладу:**
- Академічний, але не сухий. Як у "The Art of Prolog" Shapiro або "AIMA" Russell-Norvig
- Приклади і метафори де допомагає зрозумінню
- Не боятися висловлювати точку зору ("Logic-LM була landmark саме тому, що...")
- Тверезий, збалансований тон — без хайпу

**Код:**
- Working examples, не pseudo-code
- Повні Python скрипти, які можна скопіювати і запустити
- Короткі коментарі для архітектурних рішень
- Мок-LLM де доречно (щоб код не вимагав реальних API calls)
- Включати очікуваний output

---

## 9. Приклад стилю

Ось два абзаци з `docs/prolog-state-2025.md`, які демонструють цільовий стиль:

> **SICStus Prolog** — комерційний, платний, індустріально найпотужніший. Має JIT-компіляцію, інтегровані constraint solvers, які здобували медалі на MiniZinc Challenge (2009, 2014, 2020–2022, і **2025**). Медалі на MiniZinc Challenge у 2025 — це прямий доказ, що constraint programming на Пролозі не застарілий напрямок, а активно конкурентний.

> Це найцікавіша частина. До ~2020 року здавалося, що глибоке навчання витіснить символічні методи назавжди. А потім виявилося дві речі: (1) LLM не вміють надійно дедукувати. Вони галюцинують логічні висновки. (2) Символічні методи дають verifiable, explainable reasoning, який LLM не дають. Тому з'явився тренд **neuro-symbolic AI**.

Зверніть увагу: технічні терміни англійською (constraint programming, verifiable, explainable reasoning, neuro-symbolic AI), основний текст природною українською, жирним виділені ключові назви, без emoji, тон поважний але не нудний.

---

## 10. Заборони (КРИТИЧНО)

1. **НЕ згадувати minilog** у жодних описах, прикладах, case study. Навіть у розділах про Prolog+LLM pipeline використовувати "custom Prolog engine" або "educational Prolog interpreter" абстрактно
2. **НЕ згадувати Codex Seraphinianus analyzer** і Phase 2 roadmap
3. **НЕ згадувати migVisor** і Phase 4 roadmap
4. **НЕ згадувати Terra Tacita** трилогію і Phase 5
5. **НЕ використовувати emoji** взагалі ніде: діаграми, заголовки, bullet lists, код, таблиці
6. **НЕ робити автопосилання на roadmap користувача** — документ повністю самостійний
7. **НЕ скорочувати обсяг** — якщо розділ виходить коротким, значить бракує деталей
8. **НЕ пропускати код-приклади у Частині IV** — це ключова частина

---

## 11. Ключові факти для Розділу 1 (щоб не шукати заново)

Коли писатимете Розділ 1, ось ключові цифри і цитати, які вже знайдені у попередньому чаті через web search:

- **TravelPlanner benchmark:** OpenAI o1-preview досягає лише 10% success rate на multi-constraint travel planning. GPT-4 — 0.6%. З SMT-based framework (Hao et al. 2024) — 93.9%.
- **Shojaee et al. 2025** розрізняє три complexity regimes: low-, medium-, high-complexity. Reasoning дає найбільший виграш у medium-complexity зоні.
- **ATA (2025)** демонструє perfect determinism і повний імунітет до prompt injection завдяки symbolic core.
- **Gary Marcus citation:** "must have the machinery of symbol manipulation" — з "The Next Decade in AI"
- **Amazon industrial deployment (2025):** Vulcan warehouse robots і Rufus shopping assistant використовують NeSy
- **LLM reasoning failures:** Boye & Moell 2025 "Large language models and mathematical reasoning failures" (arxiv 2502.11574); "scaling limits of LLMs for logical reasoning" arxiv 2502.01100

---

## 12. Пов'язані документи (для довідки, НЕ для цитування в тексті)

Claude у новому чаті може прочитати ці файли для довідки, але НЕ повинен на них посилатися у тексті книги:

- Локально: `/Users/Vitalii_Bondarenko2/development/minilog/docs/prolog-state-2025.md` — стаття про стан Прологу 2025, хороший приклад стилю
- Локально: `/Users/Vitalii_Bondarenko2/development/minilog/docs/language-reference.md` — мовний довідник з прикладами "Свідомі обмеження" (теж хороший приклад стилю)
- Notion TOC-сторінка з повним змістом і бібліографією: https://www.notion.so/340d36341fb38181a3c1c5c59b24fe35

---

## 13. Контрольний список перед написанням Частини I

Перш ніж Claude у новому чаті почне писати, він має:

- [ ] Прочитати цей файл повністю
- [ ] Прочитати `docs/prolog-state-2025.md` для розуміння стилю
- [ ] Підтвердити що розуміє: мова змішана, без emoji, без minilog/Codex/migVisor згадок
- [ ] Коротко (3-5 речень) резюмувати задачу у першій відповіді
- [ ] Почати писати Розділ 1 без додаткових питань (усі рішення вже прийнято)

Якщо виникають сумніви — перечитати відповідний розділ цього файла замість того, щоб питати користувача. Усі прийняті рішення тут зафіксовано.

---

**Кінець контексту. Успіху у новому чаті.**
