from alembic import op

revision = '002_add_users_table'
down_revision = '001_init'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            full_name VARCHAR(200),
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE INDEX idx_users_username ON users(username);
        CREATE INDEX idx_users_email ON users(email);

        ALTER TABLE users ADD CONSTRAINT chk_username_length CHECK (length(username) >= 3);
    """)

def downgrade():
    op.execute("DROP TABLE IF EXISTS users;")
