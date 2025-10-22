#!/bin/bash
# Generate Django migrations without database connection

export DJANGO_ENVIRONMENT=development
export POSTGRES_HOST=localhost
export POSTGRES_DB=dummy
export POSTGRES_USER=dummy
export POSTGRES_PASSWORD=dummy
export POSTGRES_PORT=5432
export REDIS_URL=redis://localhost:6379/1
export SECRET_KEY=dummy-key-for-migration-generation
export DEBUG=True

# Generate migrations
python manage.py makemigrations rbac users --verbosity 2

echo "Migrations generated successfully!"
