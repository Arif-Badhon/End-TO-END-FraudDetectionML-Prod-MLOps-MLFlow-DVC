-- This runs automatically when PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas for organizing tables
CREATE SCHEMA IF NOT EXISTS raw_data;
CREATE SCHEMA IF NOT EXISTS features;
CREATE SCHEMA IF NOT EXISTS models;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Set default search path
ALTER DATABASE fraud_detection SET search_path TO public, raw_data, features, models, monitoring;

-- Create a test table to verify connection
CREATE TABLE IF NOT EXISTS public.connection_test (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message TEXT
);

INSERT INTO public.connection_test (message) VALUES ('Database initialized successfully!');

-- Grant permissions to frauduser (the user is created by POSTGRES_USER env var)
GRANT ALL PRIVILEGES ON SCHEMA public TO frauduser;
GRANT ALL PRIVILEGES ON SCHEMA raw_data TO frauduser;
GRANT ALL PRIVILEGES ON SCHEMA features TO frauduser;
GRANT ALL PRIVILEGES ON SCHEMA models TO frauduser;
GRANT ALL PRIVILEGES ON SCHEMA monitoring TO frauduser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO frauduser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO frauduser;

-- Log success
DO $$
BEGIN
    RAISE NOTICE 'Fraud Detection Database initialized successfully!';
    RAISE NOTICE 'Schemas created: raw_data, features, models, monitoring';
    RAISE NOTICE 'User: frauduser';
END $$;
