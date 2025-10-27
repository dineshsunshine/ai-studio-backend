# AI Studio Backend

A professional FastAPI backend with PostgreSQL database, designed to integrate with Google AI Studio frontend.

## 🚀 Features

- **FastAPI** - Modern, fast Python web framework
- **PostgreSQL** - Robust relational database
- **SQLAlchemy ORM** - Database abstraction layer
- **Alembic** - Database migrations
- **JWT Authentication** - Secure token-based auth
- **Pydantic** - Data validation
- **Auto-generated API Documentation** - Swagger UI & ReDoc
- **Docker Support** - Easy deployment with docker-compose
- **Ngrok Integration** - Public URL for local development

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or use Docker)
- ngrok account (free) - [Sign up here](https://ngrok.com)

## 🛠️ Installation & Setup

### Option 1: Using Docker (Recommended)

1. **Clone and navigate to backend directory:**
   ```bash
   cd AI_Studio/backend
   ```

2. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` and add your configuration:**
   ```bash
   # Update these values
   SECRET_KEY=your-super-secret-key-here
   NGROK_AUTH_TOKEN=your-ngrok-token-here
   CORS_ORIGINS=http://localhost:3000,https://aistudio.google.com
   ```

4. **Start services with Docker:**
   ```bash
   docker-compose up -d
   ```

5. **Create database tables:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

6. **Create a test user:**
   ```bash
   docker-compose exec backend python scripts/create_test_user.py
   ```

### Option 2: Manual Setup (Without Docker)

1. **Install PostgreSQL** (if not already installed):
   ```bash
   # macOS
   brew install postgresql@15
   brew services start postgresql@15
   
   # Ubuntu/Debian
   sudo apt-get install postgresql-15
   ```

2. **Create database:**
   ```bash
   psql postgres
   CREATE DATABASE ai_studio_db;
   CREATE USER ai_studio_user WITH PASSWORD 'ai_studio_pass';
   GRANT ALL PRIVILEGES ON DATABASE ai_studio_db TO ai_studio_user;
   \q
   ```

3. **Create virtual environment:**
   ```bash
   cd AI_Studio/backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create `.env` file:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

7. **Create test user:**
   ```bash
   python scripts/create_test_user.py
   ```

## 🌐 Running the Backend

### With Public URL (for Google AI Studio integration)

```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # Skip if using Docker

# Start server with ngrok tunnel
python scripts/start_with_ngrok.py
```

This will:
- Start the FastAPI server on `http://localhost:8000`
- Create a public ngrok URL (e.g., `https://abc123.ngrok.io`)
- Display the URLs in the terminal

**Copy the public URL** and use it in your Google AI Studio frontend!

### Without Public URL (local only)

```bash
# With Docker
docker-compose up

# Without Docker
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI**: `http://localhost:8000/api/v1/docs`
- **ReDoc**: `http://localhost:8000/api/v1/redoc`
- **OpenAPI JSON**: `http://localhost:8000/api/v1/openapi.json`

## 🔐 Authentication

The API uses JWT tokens for authentication.

### Login to get token:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword123"
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Use token in requests:

```bash
curl -X GET "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer eyJhbGc..."
```

## 🧪 API Endpoints

### Health Check
- `GET /api/v1/health` - Check API and database status

### Authentication
- `POST /api/v1/auth/login` - Login and get access token

### Users
- `POST /api/v1/users` - Create new user
- `GET /api/v1/users` - List all users
- `GET /api/v1/users/{id}` - Get user by ID
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

## 🗄️ Database Migrations

### Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

### Apply migrations:
```bash
alembic upgrade head
```

### Rollback migration:
```bash
alembic downgrade -1
```

## 🔧 Configuration

All configuration is in `.env` file:

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key (generate with `openssl rand -hex 32`)
- `CORS_ORIGINS` - Allowed origins for CORS
- `NGROK_AUTH_TOKEN` - Your ngrok auth token
- `NGROK_DOMAIN` - (Optional) Custom ngrok domain

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/      # API route handlers
│   │       └── api.py          # API router aggregation
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # Database setup
│   │   └── security.py        # Auth utilities
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   └── main.py                # FastAPI app
├── alembic/                   # Database migrations
├── scripts/                   # Utility scripts
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Docker configuration
└── README.md                  # This file
```

## 🚀 Deployment Tips

### For Production:

1. **Use strong SECRET_KEY:**
   ```bash
   openssl rand -hex 32
   ```

2. **Use environment-specific configs:**
   - Separate `.env` files for dev/staging/prod
   - Use proper secrets management

3. **Enable HTTPS:**
   - Use reverse proxy (nginx/Caddy)
   - Get SSL certificate (Let's Encrypt)

4. **Database:**
   - Use managed PostgreSQL (AWS RDS, DigitalOcean, etc.)
   - Regular backups
   - Connection pooling

5. **Monitoring:**
   - Add logging
   - Use APM tools (Sentry, New Relic)
   - Health check endpoints

## 🆘 Troubleshooting

### Database connection errors:
```bash
# Check if PostgreSQL is running
docker-compose ps  # Docker
# OR
brew services list  # macOS
sudo systemctl status postgresql  # Linux
```

### Port already in use:
```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 <PID>
```

### Ngrok tunnel issues:
- Verify your auth token is correct in `.env`
- Check ngrok dashboard for active tunnels
- Free ngrok accounts have connection limits

## 📝 Next Steps

Now that your backend is set up, you can:

1. ✅ Test the API endpoints using Swagger UI
2. ✅ Create custom endpoints for your AI Studio features
3. ✅ Add more models and relationships
4. ✅ Integrate with your Google AI Studio frontend
5. ✅ Deploy to production (AWS, DigitalOcean, Railway, etc.)

## 🤝 Contributing

Feel free to add more features as your AI Studio project grows!

## 📄 License

This project is created for AI Studio use.


