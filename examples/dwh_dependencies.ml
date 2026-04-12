% dwh_dependencies.ml — залежності сховища даних
% Демонструє: багатотипові відношення, транзитивне замикання,
% виявлення циклів та конфліктів запису

% Таблиці
таблиця(stg_customers).
таблиця(stg_orders).
таблиця(dim_customer).
таблиця(dim_product).
таблиця(fact_sales).
таблиця(rpt_revenue).

% Процедури
процедура(sp_load_customers).
процедура(sp_load_orders).
процедура(sp_build_dim_customer).
процедура(sp_build_fact_sales).
процедура(sp_build_rpt_revenue).
процедура(sp_refresh_dim_customer).

% Читає — процедура читає з таблиці
читає(sp_load_customers, stg_customers).
читає(sp_build_dim_customer, stg_customers).
читає(sp_load_orders, stg_orders).
читає(sp_build_fact_sales, dim_customer).
читає(sp_build_fact_sales, stg_orders).
читає(sp_build_fact_sales, dim_product).
читає(sp_build_rpt_revenue, fact_sales).
читає(sp_refresh_dim_customer, dim_customer).

% Модифікує — процедура записує в таблицю
модифікує(sp_load_customers, dim_customer).
модифікує(sp_build_dim_customer, dim_customer).
модифікує(sp_load_orders, fact_sales).
модифікує(sp_build_fact_sales, fact_sales).
модифікує(sp_build_rpt_revenue, rpt_revenue).
модифікує(sp_refresh_dim_customer, dim_customer).

% Викликає — процедура викликає іншу
викликає(sp_build_fact_sales, sp_build_dim_customer).
викликає(sp_build_rpt_revenue, sp_build_fact_sales).

% Цикл: A -> B -> C -> A
викликає(sp_build_dim_customer, sp_refresh_dim_customer).
викликає(sp_refresh_dim_customer, sp_load_customers).
викликає(sp_load_customers, sp_build_dim_customer).

% --- Правила ---

% Залежність: процедура залежить від таблиці, яку читає
правило залежить(?p, ?t) якщо читає(?p, ?t).

% Вплив: таблиця впливає на іншу через ланцюг читання/запису
правило впливає_на(?t1, ?t2) якщо модифікує(?p, ?t2) і читає(?p, ?t1).

% Виявлення циклу виклику (обмежена глибина)
правило має_цикл(?p) якщо викликає(?p, ?q) і викликає(?q, ?p).
правило має_цикл(?p) якщо викликає(?p, ?q) і викликає(?q, ?r) і викликає(?r, ?p).

% Конфлікт запису: дві різні процедури пишуть в одну таблицю
правило конфлікт_запису(?t, ?p1, ?p2) якщо модифікує(?p1, ?t) і модифікує(?p2, ?t) і не однакові(?p1, ?p2).
правило однакові(?x, ?x) якщо процедура(?x).

% --- Запити ---
?- впливає_на(stg_customers, ?x).
?- має_цикл(?x).
?- конфлікт_запису(?t, ?p1, ?p2).
