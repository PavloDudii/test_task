from alembic import op

revision = "001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

        CREATE TABLE authors (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            biography TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE UNIQUE INDEX authors_unique_name_idx ON authors (first_name, last_name);

        CREATE TABLE books (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            title VARCHAR(200) NOT NULL,
            content VARCHAR(2000) NOT NULL,
            description TEXT,
            published_year INTEGER,
            genre VARCHAR(50) NOT NULL,
            author_id UUID REFERENCES authors(id) ON DELETE SET NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX books_title_idx ON books (title);
        CREATE INDEX books_year_idx ON books (published_year);
    """)

def downgrade():
    op.execute("""
        DROP TABLE IF EXISTS books;
        DROP TABLE IF EXISTS authors;
        DROP EXTENSION IF EXISTS "uuid-ossp";
    """)
