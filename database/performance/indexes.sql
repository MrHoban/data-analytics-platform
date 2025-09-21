-- Performance optimization indexes for Data Analytics Platform
-- Run these after the initial schema creation

-- Users table indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON auth.users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON auth.users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_last_login ON auth.users(last_login_at);

-- Datasets table indexes
CREATE INDEX IF NOT EXISTS idx_datasets_user_id ON analytics.datasets(user_id);
CREATE INDEX IF NOT EXISTS idx_datasets_created_at ON analytics.datasets(created_at);
CREATE INDEX IF NOT EXISTS idx_datasets_status ON analytics.datasets(status);
CREATE INDEX IF NOT EXISTS idx_datasets_name ON analytics.datasets(name);
CREATE INDEX IF NOT EXISTS idx_datasets_user_created ON analytics.datasets(user_id, created_at DESC);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_datasets_user_status_created ON analytics.datasets(user_id, status, created_at DESC);

-- ML Models table indexes
CREATE INDEX IF NOT EXISTS idx_ml_models_user_id ON analytics.ml_models(user_id);
CREATE INDEX IF NOT EXISTS idx_ml_models_dataset_id ON analytics.ml_models(dataset_id);
CREATE INDEX IF NOT EXISTS idx_ml_models_created_at ON analytics.ml_models(created_at);
CREATE INDEX IF NOT EXISTS idx_ml_models_status ON analytics.ml_models(status);
CREATE INDEX IF NOT EXISTS idx_ml_models_algorithm ON analytics.ml_models(algorithm);

-- Composite index for model queries
CREATE INDEX IF NOT EXISTS idx_ml_models_user_status_created ON analytics.ml_models(user_id, status, created_at DESC);

-- Reports table indexes
CREATE INDEX IF NOT EXISTS idx_reports_user_id ON analytics.reports(user_id);
CREATE INDEX IF NOT EXISTS idx_reports_dataset_id ON analytics.reports(dataset_id);
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON analytics.reports(created_at);
CREATE INDEX IF NOT EXISTS idx_reports_report_type ON analytics.reports(report_type);

-- Composite index for report queries
CREATE INDEX IF NOT EXISTS idx_reports_user_type_created ON analytics.reports(user_id, report_type, created_at DESC);

-- Audit logs indexes
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit.audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit.audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_type ON audit.audit_logs(entity_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_id ON audit.audit_logs(entity_id);

-- Composite index for audit queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_timestamp ON audit.audit_logs(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_timestamp ON audit.audit_logs(entity_type, entity_id, timestamp DESC);

-- JSONB indexes for metadata columns
CREATE INDEX IF NOT EXISTS idx_datasets_metadata_gin ON analytics.datasets USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_ml_models_hyperparameters_gin ON analytics.ml_models USING GIN (hyperparameters);
CREATE INDEX IF NOT EXISTS idx_ml_models_metrics_gin ON analytics.ml_models USING GIN (metrics);
CREATE INDEX IF NOT EXISTS idx_reports_configuration_gin ON analytics.reports USING GIN (configuration);

-- Partial indexes for active records
CREATE INDEX IF NOT EXISTS idx_datasets_active ON analytics.datasets(user_id, created_at DESC) 
WHERE status = 'processed';

CREATE INDEX IF NOT EXISTS idx_ml_models_active ON analytics.ml_models(user_id, created_at DESC) 
WHERE status = 'trained';

-- Text search indexes
CREATE INDEX IF NOT EXISTS idx_datasets_name_trgm ON analytics.datasets USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_datasets_description_trgm ON analytics.datasets USING GIN (description gin_trgm_ops);

-- Enable trigram extension for text search (run as superuser)
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Statistics for query planner
ANALYZE auth.users;
ANALYZE analytics.datasets;
ANALYZE analytics.ml_models;
ANALYZE analytics.reports;
ANALYZE audit.audit_logs;
