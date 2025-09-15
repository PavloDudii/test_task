# Book Management System

A FastAPI-based REST API for managing books and authors with JWT authentication, filtering, and bulk import capabilities.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.12+ (for local development)

### Installation

1. Clone the repository
2. Copy `.env.example` to `.env` and configure your environment variables
3. Run the application:

```bash
    docker-compose up
```

The API will be available at: http://localhost:8000/

API Documentation
Interactive Swagger UI: http://localhost:8000/docs

### Testing
Run the tests locally with pytest:
```bash
  pytest
```

### Database Schema
The system uses three main tables:

#### users - User authentication and profiles

#### authors - Author information

#### books - Book catalog with author relationships

### Database Migrations
Apply database migrations manually using Alembic and raw SQL:
```bash
  alembic upgrade head
```
They will be applied automatically when using Docker.

### Authentication
JWT (JSON Web Token) authentication is used for securing endpoints. Register a user first, then use the login endpoint to obtain a token for authenticated requests.

### API Endpoints

- **User Management**
  - `POST /auth/register` - Register new user
  - `POST /auth/login` - Authenticate user and get JWT token 
  - `GET /auth/me` - Get current user information 
  - `POST /auth/logout` - Logout user

- **Author Management**
  - `POST /authors` - Create new author (authenticated)
  - `GET /authors` - Get all authors with pagination 
  - `GET /authors/search` - Search authors by name 
  - `GET /authors/{author_id}` - Get specific author by ID 
  - `PUT /authors/{author_id}` - Update author (authenticated)
  - `DELETE /authors/{author_id}` - Delete author (authenticated)

- **Book Management**
  - `POST /books` - Create new book (authenticated)
  - `GET /books` - Get books with filtering, pagination, and sorting 
  - `GET /books/{book_id}` - Get specific book by ID 
  - `PUT /books/{book_id}` - Update book (authenticated)
  - `DELETE /books/{book_id}` - Delete book (authenticated)
  - `POST /books/import` - Import books from CSV/JSON file (authenticated)

- **System**
  - `GET /health` - Health check endpoint 
  - `GET /` - Root endpoint with API information

### Importing Books
The system supports bulk import from CSV and JSON files. Example import files are provided in the repository.

Recommendation: First add authors separately before importing books to ensure proper relationships.

### Environment Configuration
Copy .env.example to .env and configure your variables.