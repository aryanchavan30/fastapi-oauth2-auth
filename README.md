# FastAPI OAuth2 Authentication System

A production-ready FastAPI authentication system with OAuth2, JWT tokens, email verification, password reset, and user management. Built with modern Python practices and security best practices.

## 🚀 Features

- **OAuth2 Authentication** with JWT tokens (Access & Refresh)
- **Email Verification** with secure tokens
- **Password Reset** functionality
- **User Management** with role-based access control
- **PostgreSQL Database** with SQLAlchemy ORM
- **Alembic Migrations** for database schema management
- **Email Integration** with SMTP support
- **Input Validation** with Pydantic
- **API Documentation** with Swagger UI & ReDoc
- **CORS Support** for frontend integration
- **Security Best Practices** (password hashing, token validation)

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Email Configuration](#email-configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Production Deployment](#production-deployment)
- [Contributing](#contributing)

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- `uv` package manager (recommended) or `pip`

### Installation with uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/fastapi-oauth2-auth.git
cd fastapi-oauth2-auth

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### Installation with pip

```bash
# Clone the repository
git clone https://github.com/yourusername/fastapi-oauth2-auth.git
cd fastapi-oauth2-auth

# Create virtual environment
python -m venv fastapi_auth
source fastapi_auth/bin/activate  # On Windows: fastapi_auth\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/fastapi_auth

# Security Settings
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Configuration (Optional but recommended)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# Environment
ENVIRONMENT=development
```

### Generate Secret Key

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🗄️ Database Setup

### PostgreSQL Installation

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download from [PostgreSQL Official Website](https://www.postgresql.org/download/windows/)

### Database Creation

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE fastapi_auth;
CREATE USER fastapi_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fastapi_auth TO fastapi_user;
\q
```

### Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Generate migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

## 📧 Email Configuration

### Gmail Setup

1. **Enable 2-Factor Authentication** in your Google Account
2. **Generate App Password**:
   - Go to Google Account Settings
   - Security → 2-Step Verification
   - App passwords → Generate password
   - Use the generated password in `SMTP_PASSWORD`

### Other Email Providers

**Outlook/Hotmail:**
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-password
```

**Yahoo:**
```env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USER=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
```

**Custom SMTP:**
```env
SMTP_HOST=your-smtp-server.com
SMTP_PORT=587
SMTP_USER=your-username
SMTP_PASSWORD=your-password
```

## 🏃‍♂️ Running the Application

### Development Server

```bash
# Using uv
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Using pip
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server

```bash
# Using Gunicorn with Uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Access the Application

- **API Base URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📚 API Documentation

### Authentication Headers

For protected endpoints, include the access token in the Authorization header:

```bash
Authorization: Bearer <your_access_token>
```

### Base URL

```
http://localhost:8000/api/v1
```

## 🛠️ API Endpoints

### Authentication Endpoints

#### 1. Register User
**POST** `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "password": "SecurePassword123",
  "confirm_password": "SecurePassword123"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false,
  "is_superuser": false,
  "last_login": null,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": null
}
```

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit

#### 2. Login
**POST** `/auth/login`

Login with email and password to get access tokens.

**Content-Type:** `application/x-www-form-urlencoded`

**Request Body:**
```
username=user@example.com&password=SecurePassword123
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 3. Refresh Token
**POST** `/auth/refresh`

Get a new access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 4. Verify Email
**GET** `/auth/verify/{token}`

Verify user email using the verification token sent via email.

**Parameters:**
- `token` (path): Email verification token

**Response (200):**
```json
{
  "message": "Email verified successfully"
}
```

#### 5. Forgot Password
**POST** `/auth/forgot-password`

Request a password reset email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "message": "Password reset email sent if email exists"
}
```

#### 6. Reset Password
**POST** `/auth/reset-password`

Reset password using the reset token from email.

**Request Body:**
```json
{
  "token": "reset_token_from_email",
  "new_password": "NewSecurePassword123",
  "confirm_password": "NewSecurePassword123"
}
```

**Response (200):**
```json
{
  "message": "Password reset successfully"
}
```

#### 7. Get Current User
**GET** `/auth/me`

Get current authenticated user details.

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": true,
  "is_superuser": false,
  "last_login": "2024-01-01T12:00:00",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T11:00:00"
}
```

#### 8. Logout
**POST** `/auth/logout`

Logout user (client should delete stored tokens).

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

#### 9. Resend Verification Email
**POST** `/auth/resend-verification`

Resend email verification for the current user.

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
  "message": "Verification email sent"
}
```

### User Management Endpoints

#### 10. Get All Users (Admin Only)
**GET** `/users/`

Get list of all users (superuser only).

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records (default: 100)

**Response (200):**
```json
[
  {
    "id": 1,
    "email": "user1@example.com",
    "username": "user1",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "is_verified": true,
    "is_superuser": false,
    "last_login": "2024-01-01T12:00:00",
    "created_at": "2024-01-01T10:00:00",
    "updated_at": null
  }
]
```

#### 11. Get User by ID
**GET** `/users/{user_id}`

Get specific user by ID (own profile or admin only).

**Headers:** `Authorization: Bearer <access_token>`

**Parameters:**
- `user_id` (path): User ID

**Response (200):** Same as Get Current User

#### 12. Update Current User
**PUT** `/users/me`

Update current user profile.

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "username": "newusername"
}
```

**Response (200):** Updated user object

#### 13. Delete Current User
**DELETE** `/users/me`

Delete current user account.

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
  "message": "User account deleted successfully"
}
```

### Health Check Endpoints

#### 14. Root Endpoint
**GET** `/`

API information and version.

**Response (200):**
```json
{
  "message": "FastAPI Auth System API",
  "version": "1.0.0"
}
```

#### 15. Health Check
**GET** `/health`

API health status.

**Response (200):**
```json
{
  "status": "healthy"
}
```

## 💡 Usage Examples

### Using cURL

#### Register a new user:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePassword123",
    "confirm_password": "SecurePassword123"
  }'
```

#### Login:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=SecurePassword123"
```

#### Get current user:
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using Python Requests

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Register user
register_data = {
    "email": "john@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePassword123",
    "confirm_password": "SecurePassword123"
}

response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print("Register:", response.json())

# Login
login_data = {
    "username": "john@example.com",
    "password": "SecurePassword123"
}

response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
tokens = response.json()
print("Login:", tokens)

# Use access token for protected routes
headers = {"Authorization": f"Bearer {tokens['access_token']}"}
response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
print("Current user:", response.json())
```

### Using JavaScript/Fetch

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';

// Register user
const registerUser = async () => {
  const response = await fetch(`${BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: 'john@example.com',
      username: 'johndoe',
      first_name: 'John',
      last_name: 'Doe',
      password: 'SecurePassword123',
      confirm_password: 'SecurePassword123'
    })
  });
  
  const data = await response.json();
  console.log('Register:', data);
};

// Login
const loginUser = async () => {
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'username=john@example.com&password=SecurePassword123'
  });
  
  const tokens = await response.json();
  console.log('Login:', tokens);
  
  // Store tokens
  localStorage.setItem('access_token', tokens.access_token);
  localStorage.setItem('refresh_token', tokens.refresh_token);
  
  return tokens;
};

// Get current user
const getCurrentUser = async () => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`${BASE_URL}/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const user = await response.json();
  console.log('Current user:', user);
};
```

## 🧪 Testing

### Run Tests with Pytest

```bash
# Install test dependencies
uv pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Manual Testing

1. **Access API Documentation**: http://localhost:8000/docs
2. **Interactive Testing**: Use Swagger UI to test endpoints
3. **Test Email Flow**: Register → Check email → Verify → Login

### Create Test Superuser

```bash
# Connect to PostgreSQL
psql -U fastapi_user -d fastapi_auth

# Create superuser
INSERT INTO users (email, username, first_name, last_name, hashed_password, is_active, is_verified, is_superuser, created_at)
VALUES ('admin@example.com', 'admin', 'Admin', 'User', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', TRUE, TRUE, TRUE, NOW());
```

## 🚀 Production Deployment

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://fastapi_user:password@db:5432/fastapi_auth
    env_file:
      - .env

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=fastapi_auth
      - POSTGRES_USER=fastapi_user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Environment Variables for Production

```env
# Production settings
DATABASE_URL=postgresql://user:password@localhost:5432/fastapi_auth
SECRET_KEY=your-production-secret-key-min-32-characters
ENVIRONMENT=production

# Email settings (use proper SMTP service)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
FROM_EMAIL=noreply@yourdomain.com
```

### Security Checklist

- [ ] Use HTTPS in production
- [ ] Set strong SECRET_KEY
- [ ] Use environment variables for sensitive data
- [ ] Enable CORS only for trusted domains
- [ ] Implement rate limiting
- [ ] Use secure database connection
- [ ] Regular security updates
- [ ] Monitor logs and errors

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔧 Troubleshooting

### Common Issues

**Database Connection Error:**
```bash
# Check PostgreSQL service
sudo systemctl status postgresql

# Check database exists
psql -U postgres -c "\l"
```

**Email Not Sending:**
```bash
# Check SMTP settings in .env
# Verify email credentials
# Check firewall/port settings
```

**Token Validation Error:**
```bash
# Check SECRET_KEY consistency
# Verify token expiration
# Check system clock synchronization
```

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support

For support, email aryanchavanapc@gmail.com or create an issue on GitHub.

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for details.

---

**Made with ❤️ using FastAPI, SQLAlchemy, and PostgreSQL**