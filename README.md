# 📊 Data Analytics Platform

[![.NET](https://img.shields.io/badge/.NET-8.0-512BD4?style=flat-square&logo=dotnet)](https://dotnet.microsoft.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

> A comprehensive, production-ready data analytics platform demonstrating expertise in data processing, visualization, and machine learning. Built with modern microservices architecture and designed for scalability and performance.

## ✨ Live Demo

🌐 **[View Live Demo](https://your-demo-url.com)** | 📖 **[API Documentation](https://your-api-docs.com)** | 🎥 **[Video Walkthrough](https://your-video-url.com)**

## 🎯 Key Highlights

- 🏗️ **Microservices Architecture** - Scalable C# API + Python Analytics Engine
- 🎨 **Modern UI/UX** - React TypeScript with Material-UI and Dark/Light themes
- 🤖 **Machine Learning** - Multiple algorithms with real-time training and prediction
- 📈 **Interactive Visualizations** - Dynamic charts and dashboards with Plotly.js
- 🔒 **Enterprise Security** - JWT authentication with role-based access control
- ⚡ **High Performance** - Redis caching, database optimization, async processing
- 🐳 **DevOps Ready** - Docker containerization with CI/CD pipeline support

## 🚀 Features

### Core Capabilities
- **Data Processing**: Advanced data cleaning, transformation, and preprocessing
- **Machine Learning**: Support for multiple algorithms including Random Forest, XGBoost, and Neural Networks
- **Data Visualization**: Interactive charts and dashboards using Plotly.js
- **Statistical Analysis**: Comprehensive statistical tools and correlation analysis
- **Real-time Processing**: Asynchronous job processing with Redis message queues
- **Caching**: Redis-based caching for improved performance
- **Authentication**: JWT-based authentication with role-based access control

### Technical Highlights
- **Microservices Architecture**: Separate C# API and Python analytics engine
- **Scalable Design**: Docker containerization with horizontal scaling support
- **Performance Optimized**: Database indexing, connection pooling, and caching strategies
- **Comprehensive Testing**: Unit tests, integration tests, and API documentation
- **Modern Frontend**: React TypeScript with Material-UI components
- **API Documentation**: OpenAPI/Swagger documentation for all endpoints

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │   C# ASP.NET    │    │  Python FastAPI │
│   (TypeScript)   │◄──►│   Core API      │◄──►│ Analytics Engine│
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │      Redis      │
                       │    Database     │    │  Cache & Queue  │
                       └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **C# ASP.NET Core 8.0**: Main API service with Entity Framework Core
- **Python FastAPI**: Analytics engine with async support
- **PostgreSQL**: Primary database with JSONB support
- **Redis**: Caching and message queue system

### Frontend
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe JavaScript
- **Material-UI**: Component library
- **Plotly.js**: Interactive data visualizations
- **React Router**: Client-side routing

### DevOps & Tools
- **Docker & Docker Compose**: Containerization
- **Nginx**: Reverse proxy and load balancing
- **Prometheus**: Metrics and monitoring
- **Serilog**: Structured logging (C#)
- **Loguru**: Advanced logging (Python)

### Machine Learning & Data Science
- **scikit-learn**: Core ML algorithms
- **XGBoost**: Gradient boosting
- **pandas**: Data manipulation
- **NumPy**: Numerical computing
- **Plotly**: Data visualization
- **statsmodels**: Statistical analysis

## 📸 Screenshots

### Dashboard Overview
![Dashboard](docs/images/dashboard-overview.png)
*Modern, responsive dashboard with dark/light theme support*

### Machine Learning Interface
![ML Interface](docs/images/ml-interface.png)
*Intuitive machine learning model training and evaluation*

### Data Visualization
![Visualizations](docs/images/data-visualization.png)
*Interactive charts and statistical analysis tools*

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- .NET 8.0 SDK (for local development)
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd data-analytics-platform
   ```

2. **Start the platform**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - C# API: http://localhost:5000
   - Python Analytics: http://localhost:8000
   - API Documentation: http://localhost:5000/swagger

### Local Development Setup

#### Backend (C# API)
```bash
cd backend/DataAnalytics.API
dotnet restore
dotnet run
```

#### Analytics Engine (Python)
```bash
cd analytics-engine
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Frontend (React)
```bash
cd frontend
npm install
npm start
```

#### Database Setup
```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Run database migrations
cd backend/DataAnalytics.API
dotnet ef database update
```

## 📊 Usage Examples

### Data Upload and Processing
```python
import requests

# Upload dataset
files = {'file': open('data.csv', 'rb')}
response = requests.post('http://localhost:5000/api/datasets/upload',
                        files=files,
                        headers={'Authorization': 'Bearer <token>'})

# Process data
processing_request = {
    "datasetId": response.json()['id'],
    "operations": ["clean", "normalize"],
    "configuration": {
        "remove_duplicates": True,
        "handle_missing": "drop"
    }
}
requests.post('http://localhost:5000/api/analytics/process-data',
              json=processing_request,
              headers={'Authorization': 'Bearer <token>'})
```

### Machine Learning Model Training
```python
training_request = {
    "datasetId": "dataset-id",
    "algorithm": "random_forest",
    "targetColumn": "target",
    "features": ["feature1", "feature2", "feature3"],
    "hyperparameters": {
        "n_estimators": 100,
        "max_depth": 10
    }
}
response = requests.post('http://localhost:5000/api/analytics/train-model',
                        json=training_request,
                        headers={'Authorization': 'Bearer <token>'})
```

### Data Visualization
```python
viz_request = {
    "datasetId": "dataset-id",
    "chartType": "scatter",
    "xColumn": "feature1",
    "yColumn": "feature2",
    "configuration": {
        "title": "Feature Correlation",
        "colorColumn": "target"
    }
}
response = requests.post('http://localhost:5000/api/analytics/visualize',
                        json=viz_request,
                        headers={'Authorization': 'Bearer <token>'})
```

## 🏆 Project Showcase

This project demonstrates proficiency in:

### **Full-Stack Development**
- ✅ Modern React TypeScript frontend with Material-UI
- ✅ RESTful API design with ASP.NET Core
- ✅ Microservices architecture with inter-service communication
- ✅ Database design and optimization with PostgreSQL

### **Data Science & Machine Learning**
- ✅ Data preprocessing and feature engineering
- ✅ Multiple ML algorithms (Random Forest, XGBoost, Neural Networks)
- ✅ Model evaluation and hyperparameter tuning
- ✅ Real-time prediction APIs

### **DevOps & Infrastructure**
- ✅ Docker containerization and orchestration
- ✅ Redis caching and message queues
- ✅ Performance optimization and monitoring
- ✅ Security best practices and authentication

### **Software Engineering Best Practices**
- ✅ Clean architecture and SOLID principles
- ✅ Comprehensive testing (unit, integration, API)
- ✅ API documentation with OpenAPI/Swagger
- ✅ Error handling and logging strategies

## 📁 Project Structure

```
data-analytics-platform/
├── 🎨 frontend/                 # React TypeScript UI
│   ├── src/components/          # Reusable UI components
│   ├── src/pages/              # Application pages
│   ├── src/contexts/           # React contexts (theme, auth)
│   └── src/services/           # API service layer
├── 🔧 backend/                 # C# ASP.NET Core API
│   ├── DataAnalytics.API/      # Web API controllers
│   ├── DataAnalytics.Core/     # Business logic
│   ├── DataAnalytics.Data/     # Data access layer
│   └── DataAnalytics.Tests/    # Unit tests
├── 🐍 analytics-engine/        # Python FastAPI service
│   ├── src/api/               # API routes
│   ├── src/services/          # ML and data services
│   ├── src/models/            # Data models
│   └── tests/                 # Python tests
├── 🗄️ database/               # Database scripts
│   ├── migrations/            # Schema migrations
│   └── seed-data/            # Sample data
├── 🐳 docker/                 # Docker configurations
├── 📚 docs/                   # Documentation
└── 🚀 scripts/               # Deployment scripts
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)
- Portfolio: [your-portfolio.com](https://your-portfolio.com)

## 🙏 Acknowledgments

- Built with modern technologies and best practices
- Inspired by real-world data analytics challenges
- Designed for scalability and maintainability

---

⭐ **If you found this project helpful, please give it a star!** ⭐
```