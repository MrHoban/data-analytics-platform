-- Data Analytics Platform - Initial Seed Data
-- This script populates the database with initial roles and sample data

-- =============================================
-- ROLES AND PERMISSIONS
-- =============================================

-- Insert default roles
INSERT INTO auth.roles (id, name, description, permissions) VALUES
(
    uuid_generate_v4(),
    'Administrator',
    'Full system access with all permissions',
    '{
        "users": ["create", "read", "update", "delete"],
        "datasets": ["create", "read", "update", "delete"],
        "models": ["create", "read", "update", "delete"],
        "reports": ["create", "read", "update", "delete"],
        "system": ["configure", "monitor", "backup"]
    }'::jsonb
),
(
    uuid_generate_v4(),
    'Data Scientist',
    'Access to data analysis and machine learning features',
    '{
        "datasets": ["create", "read", "update"],
        "models": ["create", "read", "update", "delete"],
        "reports": ["create", "read", "update", "delete"],
        "analytics": ["run", "schedule"]
    }'::jsonb
),
(
    uuid_generate_v4(),
    'Analyst',
    'Access to data visualization and basic analytics',
    '{
        "datasets": ["read"],
        "reports": ["create", "read", "update"],
        "analytics": ["run"]
    }'::jsonb
),
(
    uuid_generate_v4(),
    'Viewer',
    'Read-only access to reports and dashboards',
    '{
        "reports": ["read"],
        "dashboards": ["read"]
    }'::jsonb
);

-- =============================================
-- DEFAULT ADMIN USER
-- =============================================

-- Insert default admin user (password: Admin123!)
-- Note: In production, this should be changed immediately
INSERT INTO auth.users (id, email, password_hash, first_name, last_name, is_active, is_email_verified)
VALUES (
    uuid_generate_v4(),
    'admin@dataanalytics.com',
    '$2a$11$8gE7mKKW8yF5vF5vF5vF5uF5vF5vF5vF5vF5vF5vF5vF5vF5vF5vF5', -- Admin123!
    'System',
    'Administrator',
    true,
    true
);

-- Assign admin role to default user
INSERT INTO auth.user_roles (user_id, role_id)
SELECT u.id, r.id
FROM auth.users u, auth.roles r
WHERE u.email = 'admin@dataanalytics.com' AND r.name = 'Administrator';

-- =============================================
-- SAMPLE DATA SOURCES
-- =============================================

INSERT INTO analytics.data_sources (id, name, description, source_type, connection_config, schema_definition, created_by)
SELECT 
    uuid_generate_v4(),
    'CSV File Upload',
    'Direct CSV file upload through web interface',
    'file',
    '{
        "supported_formats": ["csv", "tsv"],
        "max_file_size": "100MB",
        "encoding": "utf-8"
    }'::jsonb,
    '{
        "auto_detect": true,
        "delimiter": ",",
        "header_row": true
    }'::jsonb,
    u.id
FROM auth.users u WHERE u.email = 'admin@dataanalytics.com';

INSERT INTO analytics.data_sources (id, name, description, source_type, connection_config, schema_definition, created_by)
SELECT 
    uuid_generate_v4(),
    'Excel File Upload',
    'Excel file upload with sheet selection',
    'file',
    '{
        "supported_formats": ["xlsx", "xls"],
        "max_file_size": "50MB",
        "sheet_selection": true
    }'::jsonb,
    '{
        "auto_detect": true,
        "header_row": true,
        "sheet_index": 0
    }'::jsonb,
    u.id
FROM auth.users u WHERE u.email = 'admin@dataanalytics.com';

INSERT INTO analytics.data_sources (id, name, description, source_type, connection_config, schema_definition, created_by)
SELECT 
    uuid_generate_v4(),
    'JSON API',
    'REST API data source with JSON response',
    'api',
    '{
        "method": "GET",
        "authentication": "bearer",
        "rate_limit": 1000,
        "timeout": 30
    }'::jsonb,
    '{
        "response_format": "json",
        "data_path": "$.data",
        "pagination": true
    }'::jsonb,
    u.id
FROM auth.users u WHERE u.email = 'admin@dataanalytics.com';

-- =============================================
-- SAMPLE DATASETS (for demonstration)
-- =============================================

INSERT INTO analytics.datasets (id, name, description, file_path, file_size, file_type, row_count, column_count, schema_info, metadata, status, created_by)
SELECT 
    uuid_generate_v4(),
    'Sample Sales Data',
    'Demonstration dataset with sales transactions',
    '/sample-data/sales_data.csv',
    1024000,
    'csv',
    10000,
    8,
    '{
        "columns": [
            {"name": "transaction_id", "type": "string", "nullable": false},
            {"name": "date", "type": "date", "nullable": false},
            {"name": "customer_id", "type": "string", "nullable": false},
            {"name": "product_id", "type": "string", "nullable": false},
            {"name": "quantity", "type": "integer", "nullable": false},
            {"name": "unit_price", "type": "decimal", "nullable": false},
            {"name": "total_amount", "type": "decimal", "nullable": false},
            {"name": "region", "type": "string", "nullable": true}
        ]
    }'::jsonb,
    '{
        "source": "sample",
        "generated": true,
        "date_range": "2023-01-01 to 2023-12-31",
        "categories": ["electronics", "clothing", "books", "home"]
    }'::jsonb,
    'processed',
    u.id
FROM auth.users u WHERE u.email = 'admin@dataanalytics.com';

INSERT INTO analytics.datasets (id, name, description, file_path, file_size, file_type, row_count, column_count, schema_info, metadata, status, created_by)
SELECT 
    uuid_generate_v4(),
    'Customer Demographics',
    'Sample customer demographic information',
    '/sample-data/customers.csv',
    512000,
    'csv',
    5000,
    6,
    '{
        "columns": [
            {"name": "customer_id", "type": "string", "nullable": false},
            {"name": "age", "type": "integer", "nullable": false},
            {"name": "gender", "type": "string", "nullable": false},
            {"name": "income", "type": "decimal", "nullable": true},
            {"name": "location", "type": "string", "nullable": false},
            {"name": "signup_date", "type": "date", "nullable": false}
        ]
    }'::jsonb,
    '{
        "source": "sample",
        "generated": true,
        "privacy": "anonymized",
        "regions": ["North", "South", "East", "West"]
    }'::jsonb,
    'processed',
    u.id
FROM auth.users u WHERE u.email = 'admin@dataanalytics.com';

-- =============================================
-- SAMPLE REPORTS
-- =============================================

INSERT INTO analytics.reports (id, name, description, report_type, dataset_id, configuration, chart_data, is_public, created_by)
SELECT 
    uuid_generate_v4(),
    'Sales Performance Dashboard',
    'Overview of sales metrics and trends',
    'dashboard',
    d.id,
    '{
        "charts": [
            {
                "type": "line",
                "title": "Sales Trend",
                "x_axis": "date",
                "y_axis": "total_amount",
                "aggregation": "sum"
            },
            {
                "type": "bar",
                "title": "Sales by Region",
                "x_axis": "region",
                "y_axis": "total_amount",
                "aggregation": "sum"
            },
            {
                "type": "pie",
                "title": "Product Distribution",
                "category": "product_id",
                "value": "quantity",
                "aggregation": "sum"
            }
        ],
        "filters": ["date_range", "region"],
        "refresh_interval": 300
    }'::jsonb,
    '{
        "last_updated": "2024-01-01T00:00:00Z",
        "data_points": 12,
        "chart_count": 3
    }'::jsonb,
    true,
    u.id
FROM analytics.datasets d, auth.users u 
WHERE d.name = 'Sample Sales Data' AND u.email = 'admin@dataanalytics.com';

INSERT INTO analytics.reports (id, name, description, report_type, dataset_id, configuration, chart_data, is_public, created_by)
SELECT 
    uuid_generate_v4(),
    'Customer Analysis Report',
    'Demographic analysis and customer insights',
    'dashboard',
    d.id,
    '{
        "charts": [
            {
                "type": "histogram",
                "title": "Age Distribution",
                "x_axis": "age",
                "bins": 10
            },
            {
                "type": "bar",
                "title": "Customers by Location",
                "x_axis": "location",
                "y_axis": "customer_id",
                "aggregation": "count"
            },
            {
                "type": "scatter",
                "title": "Age vs Income",
                "x_axis": "age",
                "y_axis": "income"
            }
        ],
        "filters": ["gender", "location"],
        "refresh_interval": 600
    }'::jsonb,
    '{
        "last_updated": "2024-01-01T00:00:00Z",
        "data_points": 5000,
        "chart_count": 3
    }'::jsonb,
    true,
    u.id
FROM analytics.datasets d, auth.users u 
WHERE d.name = 'Customer Demographics' AND u.email = 'admin@dataanalytics.com';

-- =============================================
-- SYSTEM CONFIGURATION
-- =============================================

-- Log the initialization
INSERT INTO audit.system_logs (level, message, source, details)
VALUES (
    'INFO',
    'Database initialized with seed data',
    'migration',
    '{
        "version": "1.0.0",
        "tables_created": 15,
        "roles_created": 4,
        "sample_datasets": 2,
        "sample_reports": 2
    }'::jsonb
);
