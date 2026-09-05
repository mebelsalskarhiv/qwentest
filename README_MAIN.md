# Virtuoso MES - Manufacturing Execution System

## Overview

Virtuoso MES is a comprehensive Manufacturing Execution System designed to manage and optimize production processes, inventory, quality control, and maintenance operations.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy (Async)
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt

### Frontend
- **Framework**: Next.js 14 (React 18)
- **UI Library**: Material-UI v5
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Charts**: Recharts

### DevOps
- **Containerization**: Docker & Docker Compose
- **Database Migrations**: Alembic

## Project Structure

```
virtuoso-mes/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # API route handlers
│   │   ├── core/                # Core configuration
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   └── main.py              # Application entry point
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router
│   │   ├── components/          # React components
│   │   ├── services/            # API services
│   │   ├── store/               # Zustand stores
│   │   └── types/               # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Using Docker Compose (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd virtuoso-mes
```

2. **Start all services**
```bash
docker-compose up -d
```

3. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Database: localhost:5432

4. **Default credentials**
- Username: `admin`
- Password: `admin123`

### Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Inventory
- `GET /api/v1/inventory/items` - List inventory items
- `POST /api/v1/inventory/items` - Create item
- `PUT /api/v1/inventory/items/{id}` - Update item
- `POST /api/v1/inventory/items/{id}/movements` - Record stock movement
- `GET /api/v1/inventory/categories` - List categories
- `GET /api/v1/inventory/suppliers` - List suppliers

### Production
- `GET /api/v1/production/orders` - List production orders
- `POST /api/v1/production/orders` - Create order
- `PUT /api/v1/production/orders/{id}` - Update order
- `POST /api/v1/production/orders/{id}/start` - Start order
- `POST /api/v1/production/orders/{id}/complete` - Complete order
- `GET /api/v1/production/products` - List products
- `GET /api/v1/production/work-centers` - List work centers

## Features (Phase 1 - Completed)

- ✅ User authentication & authorization (JWT)
- ✅ Role-based access control (9 roles)
- ✅ Inventory management MVP
- ✅ Production orders MVP
- ✅ Basic dashboard with stats
- ✅ Docker Compose infrastructure
- ✅ Responsive UI with Material-UI

## User Roles

1. **Admin** - Full system access
2. **Manager** - Production & resource management
3. **Supervisor** - Shop floor supervision
4. **Operator** - Production operations
5. **Quality Inspector** - Quality control
6. **Maintenance Technician** - Equipment maintenance
7. **Warehouse Keeper** - Inventory management
8. **Engineer** - Process engineering
9. **Guest** - Read-only access

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/virtuoso_mes
JWT_SECRET_KEY=your-secret-key-change-in-production
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000
```

## Next Steps (Per Plan)

### Phase 2 (Weeks 11-18)
- Advanced production planning
- ERP integration (1C)
- Work order management
- Material requirements planning

### Phase 3 (Weeks 19-26)
- Quality management (SPC, CAPA)
- OEE monitoring
- Real-time production monitoring
- Non-conformance tracking

### Phase 4 (Weeks 27-34)
- Maintenance management (TOиР)
- Document management
- PWA support
- Advanced analytics & reporting

### Phase 5 (Month 13+)
- Digital twins
- Machine learning predictions
- Industry 4.0 integrations
- IoT device integration

## License

Proprietary - All rights reserved

## Support

For issues and questions, please contact the development team.
