-- Database Setup Script
-- Run this script to set up the complete database

-- Create database (run this as superuser)
-- CREATE DATABASE data_analytics;
-- CREATE USER analytics_user WITH PASSWORD 'analytics_password';
-- GRANT ALL PRIVILEGES ON DATABASE data_analytics TO analytics_user;

-- Connect to the database and run the following:
-- \c data_analytics;

-- Grant schema permissions
GRANT USAGE ON SCHEMA public TO analytics_user;
GRANT CREATE ON SCHEMA public TO analytics_user;

-- Run migrations in order
\i migrations/001_initial_schema.sql
\i seed-data/002_initial_data.sql

-- Verify installation
SELECT 'Database setup completed successfully!' as status;

-- Show table counts
SELECT 
    schemaname,
    tablename,
    (SELECT COUNT(*) FROM (SELECT schemaname||'.'||tablename as full_name) t 
     WHERE full_name = schemaname||'.'||tablename) as row_count
FROM pg_tables 
WHERE schemaname IN ('auth', 'analytics', 'audit')
ORDER BY schemaname, tablename;
