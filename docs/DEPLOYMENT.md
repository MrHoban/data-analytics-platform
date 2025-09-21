# 🚀 Deployment Guide

This guide covers different deployment strategies for the Data Analytics Platform.

## 📋 Prerequisites

- Docker and Docker Compose
- Domain name (for production)
- SSL certificates (for HTTPS)
- Cloud provider account (AWS, Azure, GCP)

## 🐳 Docker Deployment (Recommended)

### Local Development
```bash
# Clone repository
git clone https://github.com/yourusername/data-analytics-platform.git
cd data-analytics-platform

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### Production Deployment
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Or with environment variables
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
export REDIS_URL="redis://host:6379"
export JWT_SECRET="your-secret-key"
docker-compose up -d
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using ECS (Elastic Container Service)
1. **Build and Push Images**
   ```bash
   # Build images
   docker build -t your-registry/data-analytics-frontend ./frontend
   docker build -t your-registry/data-analytics-api ./backend
   docker build -t your-registry/data-analytics-python ./analytics-engine
   
   # Push to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
   docker push your-registry/data-analytics-frontend
   docker push your-registry/data-analytics-api
   docker push your-registry/data-analytics-python
   ```

2. **Create ECS Task Definition**
   ```json
   {
     "family": "data-analytics-platform",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "containerDefinitions": [
       {
         "name": "frontend",
         "image": "your-registry/data-analytics-frontend",
         "portMappings": [{"containerPort": 80}]
       },
       {
         "name": "api",
         "image": "your-registry/data-analytics-api",
         "portMappings": [{"containerPort": 5000}]
       },
       {
         "name": "analytics",
         "image": "your-registry/data-analytics-python",
         "portMappings": [{"containerPort": 8000}]
       }
     ]
   }
   ```

#### Using Kubernetes (EKS)
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-analytics-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: data-analytics
  template:
    metadata:
      labels:
        app: data-analytics
    spec:
      containers:
      - name: frontend
        image: your-registry/data-analytics-frontend
        ports:
        - containerPort: 80
      - name: api
        image: your-registry/data-analytics-api
        ports:
        - containerPort: 5000
      - name: analytics
        image: your-registry/data-analytics-python
        ports:
        - containerPort: 8000
```

### Azure Deployment

#### Using Azure Container Instances
```bash
# Create resource group
az group create --name data-analytics-rg --location eastus

# Deploy container group
az container create \
  --resource-group data-analytics-rg \
  --file azure-container-group.yaml
```

#### Using Azure Kubernetes Service (AKS)
```bash
# Create AKS cluster
az aks create \
  --resource-group data-analytics-rg \
  --name data-analytics-cluster \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Deploy application
kubectl apply -f k8s/
```

### Google Cloud Platform

#### Using Cloud Run
```bash
# Deploy each service
gcloud run deploy data-analytics-frontend \
  --image gcr.io/your-project/data-analytics-frontend \
  --platform managed \
  --region us-central1

gcloud run deploy data-analytics-api \
  --image gcr.io/your-project/data-analytics-api \
  --platform managed \
  --region us-central1

gcloud run deploy data-analytics-python \
  --image gcr.io/your-project/data-analytics-python \
  --platform managed \
  --region us-central1
```

## 🔧 Configuration

### Environment Variables

#### Backend (.NET API)
```bash
ASPNETCORE_ENVIRONMENT=Production
ConnectionStrings__DefaultConnection=postgresql://...
Redis__ConnectionString=redis://...
JWT__Secret=your-jwt-secret
JWT__Issuer=your-issuer
JWT__Audience=your-audience
PythonService__BaseUrl=http://analytics-service:8000
```

#### Python Analytics Engine
```bash
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
LOG_LEVEL=INFO
MODEL_STORAGE_PATH=/app/models
CORS_ORIGINS=https://your-frontend-domain.com
```

#### Frontend (React)
```bash
REACT_APP_API_URL=https://your-api-domain.com
REACT_APP_ANALYTICS_URL=https://your-analytics-domain.com
REACT_APP_ENVIRONMENT=production
```

### Database Setup

#### PostgreSQL
```sql
-- Create database
CREATE DATABASE data_analytics;

-- Create user
CREATE USER analytics_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE data_analytics TO analytics_user;

-- Run migrations
dotnet ef database update --project DataAnalytics.API
```

#### Redis Configuration
```redis
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## 🔒 Security Considerations

### SSL/TLS Configuration
```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://api:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Firewall Rules
```bash
# Allow only necessary ports
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw deny 5000   # Block direct API access
ufw deny 8000   # Block direct analytics access
```

## 📊 Monitoring and Logging

### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'data-analytics-api'
    static_configs:
      - targets: ['api:5000']
  
  - job_name: 'data-analytics-python'
    static_configs:
      - targets: ['analytics:8000']
```

### Log Aggregation
```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  api:
    logging:
      driver: "fluentd"
      options:
        fluentd-address: localhost:24224
        tag: api.logs
  
  analytics:
    logging:
      driver: "fluentd"
      options:
        fluentd-address: localhost:24224
        tag: analytics.logs
```

## 🔄 CI/CD Pipeline

### GitHub Actions Deployment
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to production
        run: |
          # Build and deploy steps
          docker-compose -f docker-compose.prod.yml up -d
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check database connectivity
   docker exec -it postgres psql -U postgres -d data_analytics
   ```

2. **Redis Connection Issues**
   ```bash
   # Check Redis connectivity
   docker exec -it redis redis-cli ping
   ```

3. **Service Discovery Issues**
   ```bash
   # Check container networking
   docker network ls
   docker network inspect data-analytics-platform_default
   ```

### Health Checks
```bash
# API health check
curl http://localhost:5000/health

# Analytics health check
curl http://localhost:8000/health

# Frontend availability
curl http://localhost:3000
```

## 📈 Scaling

### Horizontal Scaling
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  api:
    deploy:
      replicas: 3
  
  analytics:
    deploy:
      replicas: 2
```

### Load Balancing
```nginx
# nginx load balancer
upstream api_backend {
    server api1:5000;
    server api2:5000;
    server api3:5000;
}

upstream analytics_backend {
    server analytics1:8000;
    server analytics2:8000;
}
```

For more detailed deployment instructions, see the specific cloud provider documentation.
