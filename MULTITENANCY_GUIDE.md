# Virtuoso MES Multitenancy Guide

## Обзор архитектуры

Virtuoso MES теперь поддерживает полноценную мультитенантную архитектуру с:
- **Единым входом** через Caddy reverse proxy (порт 80/443)
- **Автоматической SSL** генерацией через Let's Encrypt
- **Изоляцией тенантов** на уровне базы данных
- **Суперадмин панелью** для управления тенантами
- **Биллинг системой** с тарифными планами

## Архитектура

```
                    ┌─────────────────┐
                    │     Caddy       │
                    │  (Reverse Proxy)│
                    │  Port 80/443    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ virtuoso-mes  │   │superadmin.    │   │ tenant1.      │
│ .local        │   │virtuoso-mes   │   │virtuoso-mes   │
│ (Demo/Public) │   │.local         │   │.local         │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────▼───────┐
                    │   Backend     │
                    │  (FastAPI)    │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │  PostgreSQL   │
                    │ (Multitenant) │
                    └───────────────┘
```

## Быстрый старт

### 1. Локальная разработка (без SSL)

```bash
# Запуск без Caddy (только backend + frontend + DB)
docker-compose up -d

# Доступ:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### 2. Production с SSL

```bash
# 1. Скопируйте и настройте .env
cp .env.example .env
nano .env  # Отредактируйте домен и пароли

# 2. Запустите production стек
docker-compose -f docker-compose.prod.yml up -d

# 3. Проверьте логи
docker-compose -f docker-compose.prod.yml logs -f caddy
```

## Структура доменов

| Домен | Описание | Доступ |
|-------|----------|--------|
| `virtuoso-mes.local` | Главная страница, демо, регистрация | Публично |
| `www.virtuoso-mes.local` | Редирект на главный | Публично |
| `superadmin.virtuoso-mes.local` | Панель суперадмина | SuperAdmin |
| `demo.virtuoso-mes.local` | Демо тенант | Все пользователи |
| `tenant1.virtuoso-mes.local` | Тенант 1 | Пользователи тенанта |
| `api.virtuoso-mes.local` | API для интеграций | По токену |

## Суперадмин панель

### Создание тенанта через API

```bash
# Логин как суперадмин
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@virtuoso-mes.local", "password": "admin123"}'

# Создание нового тенанта
curl -X POST "http://localhost:8000/api/v1/superadmin/tenants/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Manufacturing",
    "subdomain": "acme",
    "billing_plan": "professional",
    "ssl_enabled": true,
    "letsencrypt_email": "admin@acme.com",
    "admin_email": "admin@acme.com",
    "admin_password": "SecurePass123!",
    "auto_activate": true,
    "trial_days": 14
  }'
```

### Статистика по тенантам

```bash
curl -X GET "http://localhost:8000/api/v1/superadmin/tenants/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Включение SSL для тенанта

```bash
curl -X PUT "http://localhost:8000/api/v1/superadmin/tenants/{tenant_id}/ssl" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "letsencrypt_email": "admin@tenant.com"
  }'
```

## Тарифные планы

| План | Цена | Возможности |
|------|------|-------------|
| **Free** | $0 | 1 пользователь, базовый функционал |
| **Startup** | $29/мес | 10 пользователей, производство + склад |
| **Professional** | $99/мес | 50 пользователей, полное MES + качество |
| **Enterprise** | $299/мес | Безлимит, TOиР, аналитика, API приоритет |

## Управление тенантами

### Список всех тенантов

```bash
GET /api/v1/superadmin/tenants/?skip=0&limit=100
```

### Обновление биллинга

```bash
PUT /api/v1/superadmin/tenants/{tenant_id}/billing
{
  "billing_plan": "enterprise",
  "subscription_expires_at": "2025-12-31T23:59:59Z"
}
```

### Приостановка тенанта

```bash
POST /api/v1/superadmin/tenants/{tenant_id}/suspend
```

### Активация тенанта

```bash
POST /api/v1/superadmin/tenants/{tenant_id}/activate
```

### Удаление тенанта

```bash
DELETE /api/v1/superadmin/tenants/{tenant_id}?soft_delete=true
```

## Изоляция данных

Каждый тенант имеет свои данные:
- Пользователи (`users.tenant_id`)
- Заказы на производство (`production_orders.tenant_id`)
- Материалы (`inventory_items.tenant_id`)
- Сотрудники (`employees.tenant_id`)

Запросы автоматически фильтруются по `tenant_id` текущего пользователя.

## Caddy конфигурация

Файл `infrastructure/caddy/Caddyfile` управляет:
- Маршрутизацией по поддоменам
- Автоматической SSL через Let's Encrypt
- On-demand TLS для кастомных доменов
- Rate limiting (опционально)

### Валидация домена для SSL

Caddy запрашивает у backend `/api/v1/superadmin/tenants/validate-domain` перед выдачей сертификата.

## Безопасность

1. **JWT токены** содержат `tenant_id` для изоляции
2. **HTTPS обязателен** в production
3. **Пароли** хешируются через bcrypt
4. **CORS** настроен на домен тенанта
5. **Rate limiting** на уровне Caddy

## Мониторинг

```bash
# Логи Caddy
docker-compose -f docker-compose.prod.yml logs -f caddy

# Статистика тенантов
curl http://localhost:8000/api/v1/superadmin/tenants/stats

# Проверка SSL
curl -vI https://tenant1.virtuoso-mes.local
```

## Миграции

При обновлении схемы БД:

```bash
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

## Резервное копирование

```bash
# Backup PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U virtuoso virtuoso_mes > backup.sql

# Backup Caddy SSL сертификатов
docker-compose -f docker-compose.prod.yml run --rm caddy \
  tar czf /backup/caddy_data.tar.gz /data
```

## Troubleshooting

### SSL не выдается

1. Проверьте DNS записи (A record на сервер)
2. Проверьте логи Caddy: `docker logs virtuoso-caddy`
3. Убедитесь что порт 80 открыт для ACME challenge

### Тенант не доступен

1. Проверьте статус: `GET /api/v1/superadmin/tenants/{id}`
2. Убедитесь что `status = active`
3. Проверьте логи backend

### Ошибки базы данных

1. Проверьте подключение: `docker-compose exec postgres psql -U virtuoso`
2. Проверьте миграции: `alembic current`
3. Восстановите из backup при необходимости

## Следующие шаги

- [ ] Настроить Stripe для автоматического биллинга
- [ ] Добавить email уведомления о статусе тенанта
- [ ] Реализовать self-service регистрацию тенантов
- [ ] Добавить метрики использования (usage tracking)
- [ ] Интеграция с платежными системами РФ
