# План-график работ по разработке Virtuoso MES

## Общая информация
- **Проект:** Virtuoso MES — Интеллектуальная система управления производством
- **Дата начала:** 14 августа 2026 г.
- **Общая длительность:** 13–16 месяцев (базовый сценарий) / 18+ при полной реализации ТЗ
- **Стек (принятый для реализации):** Python 3.12 + FastAPI, React 18 + Next.js 14 + TypeScript, PostgreSQL 16 (+ TimescaleDB с Ф3), Redis 7, MinIO, Celery, Docker → K8s
- **Архитектурный принцип:** modular monolith (принято 15.08.2026, см. `docs/adr/001-modular-monolith.md`); микросервисы — только по доказанной необходимости
- **Стенд / проверки:** локально + Docker Compose (**без GitHub Actions**); см. `docs/local-verify.md`
- **Источник требований:** `DeepAnalitic.md` v1.0 (23.07.2026)
- **Актуализация плана:** 15.08.2026

### Легенда статусов
| Символ | Значение |
|--------|----------|
| ✅ | Готово (проверено на стенде) |
| 🟡 | Частично / скелет |
| ⏳ | В работе |
| ⬜ | Ожидает |
| ➕ | Добавлено в план по результатам сверки с ТЗ |

---

## Фаза 0: Выравнивание ТЗ и плана (W0, 15.08–20.08) ➕
**Цель:** убрать противоречия ТЗ ↔ план ↔ код до масштабирования разработки

| Задача | Статус | Критерий готовности |
|--------|--------|---------------------|
| 0.1 Зафиксировать архитектуру: modular monolith + event bus (Redis/Celery), не Database-per-Service на старте | ✅ | ADR-001 принят (`docs/adr/001-modular-monolith.md`) |
| 0.2 Приоритеты MVP: что обязательно для приёмки Ф1–Ф2 vs backlog «nice-to-have» | ✅ | MoSCoW B+C: `docs/moscow-phase1-2.md` |
| 0.3 Инвентаризация legacy Shop Floor (модели, API, UI, данные) для миграции | ✅ | Карта: `docs/legacy-entity-map.md` (source: `E:\Virtuoso\local-test`) |
| 0.4 Локальные проверки качества (typecheck/lint/pytest в Docker), без GitHub Actions | ✅ | `docs/local-verify.md` + `scripts/verify-local.ps1` |

---

## Фаза 1: Базовая платформа (Месяцы 1–3)
**Цель:** инфраструктура, ядро безопасности, перенос legacy Shop Floor, склад/ПЗ MVP и **простой Kanban** (MoSCoW B+C)
**Scope Must:** см. `docs/moscow-phase1-2.md`

| Неделя | Задача | Ответственный | Статус | Критерий готовности |
|--------|--------|---------------|--------|---------------------|
| W1 (14.08) | 1.1 Инициализация monorepo backend/frontend, lint/typecheck | Both | ✅ | `npm run typecheck`, Python import OK |
| W1 (14.08) | 1.2 Docker Compose: PostgreSQL, Redis, MinIO, pgAdmin, backend, frontend | DevOps | ✅ | `docker compose up` healthy; pgAdmin на свободном порту |
| W2 (21.08) | 1.3 FastAPI ядро: роутинг, CORS, Alembic, `/docs` | Backend | ✅ | `/docs` открывается, миграция `0001_initial` |
| W2 (21.08) | 1.4 Auth: JWT access+refresh, User/Role/Permission, login/me/logout | Backend | ✅ | `/auth/login` → токены; bcrypt без passlib-багов |
| W3 (28.08) | 1.5 RBAC: 9 ролей, permissions seed, dependency `require_permission` | Backend | 🟡 | Seed есть; нужны тесты 403/200 на защищённых эндпоинтах |
| W3 (28.08) | 1.6 Audit: AuditLog + запись критичных действий | Backend | 🟡 | Модель+API есть; middleware на все mutating-запросы — довести |
| W4 (04.09) | 1.7 Configuration: SystemSettings CRUD, версии | Backend | 🟡 | API есть; UI настроек и hot-reload cache — довести |
| W4 (04.09) | 1.8 Notifications: WS + Redis pub/sub | Backend | 🟡 | Сервис есть; e2e push в UI — проверить |
| W5 (11.09) | 1.9 Frontend ядро: App Router, MUI v6, layout, sidebar | Frontend | ✅ | `/` и навигация по ключам страниц |
| W5 (11.09) | 1.10 Frontend auth: Login, AuthProvider, JWT interceptor | Frontend | ✅ | Вход `admin / Admin123!`, токен в localStorage |
| W6 (18.09) | 1.11 UI пользователи: таблица, CRUD, роли | Frontend | ✅ | CRUD пользователя end-to-end |
| W6 (18.09) | 1.12 UI роли/права: матрица разрешений | Frontend | ✅ | Чекбоксы разрешений сохраняются |
| W6 (18.09) | 1.12a ➕ Employee ↔ User, Department UI, Customer CRUD | Both | ✅ | Справочники API+UI |
| W7 (25.09) | 1.13 Станции (Station): модели, CRUD, режимы доставки (mounted/smb/nfs) | Backend | ✅ | CRUD станций + статусы active/inactive |
| W7 (25.09) | 1.14 Inventory MVP: материалы, остатки, резервы, поступления, обрезки | Backend | ✅ | Stock + FIFO-резерв + заказ/поступление; обрезки → позже |
| W7–W8 | 1.14a ➕ Inventory UI (материалы/поступления/обрезки) | Frontend | ✅ | Вкладки: остатки / резервы / жадные / поступления; обрезки → позже |
| W8 (02.10) | 1.15 Production MVP: ProductionOrder, Stage, StageType, WorkOrder, Timeline, Comment | Backend | ✅ | ПЗ→этапы→наряды; PATCH status + timeline/comments |
| W8 (02.10) | 1.15a ➕ Production UI: списки/карточки ПЗ и нарядов | Frontend | ✅ | CRUD ПЗ/этапы/наряды + карточка со сменой статуса |
| W9 (09.10) | 1.15b ➕ Kanban MVP нарядов (Must B+C): 4–6 колонок, dnd → смена статуса | Frontend | ✅ | 5 колонок + dnd-kit; фильтр по участку |
| W8 (02.10) | 1.16 API Gateway (nginx/Traefik): TLS-ready, rate limit, единый вход | DevOps | ✅ | nginx :80 → FE/API; auth rate-limit; TLS example |
| W8 | 1.16a ➕ Celery worker в Compose (фон: доставка файлов позже, отчёты) | DevOps | ✅ | worker+beat; ops ping/inspect |
| W9 (09.10) | 1.17 Unit-тесты ядра: auth, RBAC, audit (coverage ≥80% core) | Backend | ✅ | pytest + greenlet cov ≥80% (core/auth/audit) |
| W9–W10 | 1.18 Smoke e2e: login → users → PO → Kanban status change | QA | ✅ | pytest + `scripts/smoke-e2e.ps1`; browser: `smoke-browser.ps1` |
| W9 | 1.18a ➕ Нагрузочный smoke (не 500 сессий): k6 baseline 50 VU | QA | ✅ | `run-k6.ps1` (2 workers); p95 < 3с, 0% fail |
| W10 (16.10) | 1.19 Bugfix + демо-данные (seed заказов/склада/нарядов на доске) | Команда | ✅ | `DEMO-BOARD-001` + 5 нарядов по колонкам Kanban |
| W10 (16.10) | 1.20 Демонстрация Фазы 1 заказчику | PM | ✅ | Протокол: `docs/demo-protocol-phase1.md` |

**Результат Фазы 1:** Паритет legacy (users/roles/refs/склад/ПЗ) + рабочий Kanban MVP; тесты ядра; демо 15 мин.

**Перенесено из Ф1:** полный набор колонок/фильтров Kanban, Gantt, 500 VU → Ф2.

---

## Фаза 2: Управление производством и ERP (Месяцы 4–6)
**Цель:** полный производственный контур цеха + первая ERP-интеграция (1С)

| Неделя | Задача | Ответственный | Статус | Критерий готовности |
|--------|--------|---------------|--------|---------------------|
| W11–W12 | 2.1 Kanban advanced: расширенные колонки/фильтры, UX мастера (база уже в Ф1 1.15b) | Frontend | ✅ | 6 колонок; поиск/ПЗ/приоритет/участок; клик→карточка; drag за ручку |
| W11–W12 | 2.2 Scheduling: календарь смен, Gantt, детект конфликтов станков | Both | ⬜ | Конфликт подсвечивается, ручной dnd сроков |
| W13 | 2.3 Авто-назначение: эвристика станок+исполнитель (rule-based) | Backend | ⬜ | Предложение исполнителя/станка с объяснением |
| W13 | 2.4 QR: генерация на наряд/материал, сканер в UI | Both | ⬜ | Scan → карточка наряда |
| W14 | 2.5 File Delivery: SMB/NFS/FTP + Celery retry + журнал | Backend | ⬜ | Файл на станции, audit trail доставки |
| W14–W15 | 2.6 Интеграция 1С: заказы, номенклатура, остатки, выпуск (HTTP API) | Integration | ⬜ | Тестовая база 1С ↔ MES, 3 объекта sync |
| W14 | 2.6a ➕ Integration Hub: outbox/inbox, webhooks, идемпотентность | Backend | ⬜ | Повторная доставка не дублирует документы |
| W15–W16 | 2.7 UI производства: полный workflow мастер/технолог/оператор (web) | Frontend | ⬜ | Сценарий «заказ → выпуск» без SQL |
| W16 | 2.7a ➕ Печатные формы MVP: наряд, маршрутный лист (PDF) | Backend | ⬜ | PDF генерируется из шаблона |
| W16 | 2.7b ➕ Партионность материалов + резерв под ПЗ (углубление склада) | Backend | ⬜ | Партия прослеживается до наряда |
| W17–W18 | 2.8 Интеграционные + e2e тесты, UAT | QA | ⬜ | UAT-замечания закрыты |
| W18 | 2.8a ➕ Нагрузка 500 сессий на прод-подобный стенд | QA | ⬜ | p95 < 3с, отчёт |
| W18 | 2.9 Демонстрация Фазы 2 | PM | ⬜ | Протокол приёмки |

**Результат Фазы 2:** Kanban advanced + Gantt, доставка УП, 1С sync, печатные формы MVP.

**Backlog Ф2 (не блокирует приёмку):** Supply Chain / заявки поставщикам (ТЗ §3.1.5) — вынести в Ф2.5 или Ф4 по приоритету заказчика.

---

## Фаза 3: Качество и мониторинг оборудования (Месяцы 7–9)
**Цель:** QC/SPC/CAPA + OEE со станков (эмулятор → стенд)

| Неделя | Задача | Ответственный | Статус | Критерий готовности |
|--------|--------|---------------|--------|---------------------|
| W19–W20 | 3.1 Monitoring adapters: MTConnect + OPC-UA + эмулятор ЧПУ | Backend IoT | ⬜ | Метрики пишутся в TimescaleDB |
| W19–W20 | 3.2 OEE engine: A×P×Q по станку/участку | Backend | ⬜ | График OEE за период |
| W21 | 3.3 Простои: причины, Pareto, тренды | Both | ⬜ | Отчёт «Структура простоев» |
| W21–W22 | 3.4 QC: входной → операционный → приёмочный ОТК | Backend | ⬜ | Наряд проходит 3 вида контроля |
| W22 | 3.5 SPC: X/R карты, алерты | Backend | ⬜ | Выход за пределы → notification |
| W22 | 3.6 Nonconformance: RCA (5 почему / Исикава), CAPA | Backend | ⬜ | CAPA с закрытием и оценкой |
| W23–W24 | 3.7 UI мониторинга + цеховое табло (read-only dashboard) ➕ | Frontend | ⬜ | Live-обновление OEE/статусов |
| W23–W24 | 3.8 UI качества: протоколы, SPC, CAPA | Frontend | ⬜ | Полный QC workflow |
| W24 | 3.8a ➕ Трассируемость: партия материала → ПЗ → наряд → ОТК | Both | ⬜ | Отчёт traceability по QR/номеру |
| W25–W26 | 3.9 Нагрузка IoT + UAT | QA | ⬜ | UAT пройден |
| W26 | 3.10 Демонстрация Фазы 3 | PM | ⬜ | Протокол |

**Результат Фазы 3:** OEE, QC/SPC/CAPA, трассируемость.

---

## Фаза 4: ТОиР, документы, мобильность, аналитика (Месяцы 10–12)
**Цель:** закрыть модули ТЗ §3.5–3.8 без «фантазийного» AI до накопления данных

| Неделя | Задача | Ответственный | Статус | Критерий готовности |
|--------|--------|---------------|--------|---------------------|
| W27–W28 | 4.1 Maintenance: паспорта, график ТО, заявки на ремонт, инструмент | Backend | ⬜ | График ТО + закрытие ремонта |
| W27–W28 | 4.2 Document Service: версии, workflow согласования (ЭЦП — опционально) | Backend | ⬜ | Документ проходит маршрут |
| W29 | 4.3 Dashboard/Reporting: KPI роли (директор/мастер/технолог), Excel/PDF | Both | ⬜ | 3 ролевых дашборда |
| W29 | 4.3a ➕ BI API / read-replicas views для Power BI | Backend | ⬜ | Документированный read API |
| W30–W32 | 4.4 PWA оператора: офлайн-очередь, QR, приёмка/сдача | Frontend Mobile | ⬜ | PWA ставится, sync после offline |
| W30–W32 | 4.4a ➕ Rule-based predictive hints (не ML): пороги вибрации/простоев | Backend | ⬜ | Алерт «рекомендуется ТО» по правилам |
| W33 | 4.5 ML prep: сбор датасетов, MLflow sandbox (без prod-SLA) | ML | ⬜ | Датасет + baseline модель offline |
| W33–W34 | 4.6 UAT + демо Фазы 4 | PM/QA | ⬜ | Протокол |

**Результат Фазы 4:** ТОиР, документы, PWA, BI; ML — в песочнице.

**Явно отложено в Ф5:** React Native (дубль PWA), RFID, голосовой ввод, GraphQL, полный SSO.

---

## Фаза 5: Industry 4.0 и масштабирование (Месяцы 13+)
**Цель:** то, что требует зрелых данных, железа и бюджета интеграций

| Период | Задача | Статус | Критерий готовности |
|--------|--------|--------|---------------------|
| M13 | 5.1 Цифровые двойники (2D сначала, 3D опционально) | ⬜ | Симуляция цикла УП на 1 типе станка |
| M13–M14 | 5.2 ML в prod: прогноз отказа / брака (AUC≥0.85 при наличии данных) | ⬜ | Модель за shadow-mode → prod |
| M14–M15 | 5.3 Оптимизация scheduling (metaheuristics), +10–15% загрузки | ⬜ | A/B на исторических планах |
| M15 | 5.4 SSO (AD/LDAP/OIDC), MFA для админов ➕ | ⬜ | Корп. логин работает |
| M16 | 5.5 Интеграции: SAP/Dynamics/CAD-CAM/PLM по запросу | ⬜ | Коннектор + контрактные тесты |
| Постоянно | 5.6 Observability: Prometheus+Grafana, Loki/ELK, Jaeger; SLA 99.5% | ⬜ | Алерты и runbooks |
| Постоянно | 5.7 i18n (ru/en), WCAG 2.1 AA критичных экранов ➕ | ⬜ | Чеклист a11y пройден |

---

## Матрица покрытия ТЗ ↔ план

| Модуль ТЗ | Раздел ТЗ | Фаза плана | Примечание |
|-----------|-----------|------------|------------|
| Auth / RBAC / Audit / Settings / Notifications | §3.10, §7.1 | Ф1 | Скелет ✅, довести тесты/middleware |
| Users / Roles UI | §3.10.1 | Ф1 W6 | Следующий приоритет |
| Production Orders / Stages / WorkOrders | §3.1.1–3.1.3 | Ф1→Ф2 | MVP в Ф1, Kanban/auto в Ф2 |
| Scheduling / Gantt | §3.1.4 | Ф2 | |
| Supply Chain / поставки | §3.1.5 | Backlog / Ф2.5 | В исходном plan отсутствовал |
| Inventory / scraps / inventory count | §3.2 | Ф1 MVP → Ф2 углубление | FIFO/LIFO, multi-warehouse — Ф2+ |
| Quality / SPC / CAPA | §3.3 | Ф3 | |
| Equipment monitoring / OEE | §3.4.1–3.4.2 | Ф3 | |
| Predictive maintenance (ML) | §3.4.3 | Ф4 prep → Ф5 prod | |
| Digital twin | §3.4.4 | Ф5 | |
| Maintenance / tool crib | §3.5 | Ф4 | Ранее было слишком поздно относительно ценности |
| Documents / workflow / print | §3.6 | Ф2 print MVP, Ф4 workflow | |
| Analytics / BI | §3.7 | Ф4 | |
| Mobile / PWA / QR | §3.8 | Ф2 QR, Ф4 PWA | RN/RFID/voice → Ф5 backlog |
| ERP 1С | §3.9.1 | Ф2 | |
| CAD/CAM, SAP, PLM | §3.9.2–3.9.4 | Ф5 | |
| NFR: perf, HA, security, a11y, i18n | §4 | Ф1 smoke → Ф2 500 VU → Ф5 HA/SSO/a11y | |

---

## Ключевые риски и зависимости

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| ТЗ описывает микросервисы «сразу», команда строит монолит | Высокая | Средняя | ADR: monolith-first; границы модулей = будущие сервисы |
| Интеграция 1С не готова / нет тестовой базы | Средняя | Высокая | Контракт API + mock с W12; интегратор до W14 |
| MTConnect/OPC-UA на реальных ЧПУ | Средняя | Высокая | Эмулятор с W19; стендовый станок |
| Недостаток данных для ML | Высокая | Средняя | Rule-based в Ф4; ML только после 3–6 мес телеметрии |
| Перенос legacy без карты данных | Средняя | Высокая | Фаза 0 инвентаризация + dual-write/migration scripts |
| Scope creep (RFID, GraphQL, RN, голос, ЦД) | Высокая | Высокая | MoSCoW; «Won't» до Ф5 явно в плане |
| Нагрузка 500 сессий до появления домена | Средняя | Низкая | Перенесено на конец Ф2 |

---

## Ресурсы (ориентир, чел.-мес.)

| Роль | Было | Уточнено | Комментарий |
|------|------|----------|-------------|
| Backend | 18 | 20 | +Integration Hub, print, inventory depth |
| Frontend | 15 | 16 | +трассируемость UI, цеховое табло |
| DevOps/QA | 8 | 10 | CI с Ф0, нагрузка, observability раньше |
| PM/Analyst | 6 | 7 | Фаза 0 MoSCoW + legacy map |
| ML Engineer | 3 | 2+2 | 2 в Ф4 prep, 2 в Ф5 prod |
| **Итого** | ~50 | **~55–57** | |

---

## Метрики готовности (приёмка)

| Фаза | KPI приёмки |
|------|-------------|
| Ф0 | ADR-001 + MoSCoW B+C + legacy map; локальный `verify-local.ps1` |
| Ф1 | Legacy MVP + **Kanban MVP**; coverage core ≥80% (pytest в Docker); демо 15 мин |
| Ф2 | Kanban advanced + Gantt; 1С — 3 объекта; File Delivery; 500 VU p95<3с (локально/стенд) |
| Ф3 | OEE vs ручной ≥95%; SPC на 3 процессах; CAPA; traceability |
| Ф4 | ТОиР+docs+PWA offline; 3 ролевых дашборда; BI API; ML sandbox |
| Ф5 | ЦД/оптимизация/SSO по утверждённому backlog; SLA 99.5% |

---

## Ближайшие 2 недели (исполнение после утверждения)

1. **W6:** UI Users + Roles (1.11–1.12)  
2. **W6–W7:** Customer, Department, Station, Employee linkage (1.12a–1.13)  
3. **W7–W8:** Inventory MVP + Production MVP API/UI (1.14–1.15a)  
4. **W9:** Kanban MVP (1.15b) — Must для приёмки Ф1  
5. Параллельно: RBAC-тесты, audit middleware, Celery в Compose; перед демо — `.\scripts\verify-local.ps1`  

---

*Документ заменяет статусы предыдущей версии plan.md от 14.08.2026 и синхронизирован с фактическим состоянием репозитория на 15.08.2026. MoSCoW: B+C (15.08.2026).*
