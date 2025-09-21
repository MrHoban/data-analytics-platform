# Contributing to Data Analytics Platform

Thank you for your interest in contributing to the Data Analytics Platform! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- .NET 8.0 SDK
- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Git

### Development Environment Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/data-analytics-platform.git
   cd data-analytics-platform
   ```

2. **Backend Setup**
   ```bash
   cd backend
   dotnet restore
   dotnet build
   ```

3. **Python Analytics Engine**
   ```bash
   cd analytics-engine
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

5. **Database Setup**
   ```bash
   docker-compose up -d postgres redis
   cd backend/DataAnalytics.API
   dotnet ef database update
   ```

## 🔧 Development Guidelines

### Code Style

#### C# (.NET)
- Follow Microsoft's C# coding conventions
- Use meaningful variable and method names
- Add XML documentation for public APIs
- Use async/await for asynchronous operations

#### Python
- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Add docstrings for all functions and classes
- Use Black for code formatting

#### TypeScript/React
- Use functional components with hooks
- Follow React best practices
- Use TypeScript strict mode
- Use ESLint and Prettier for code formatting

### Testing

#### Backend Tests
```bash
cd backend
dotnet test
```

#### Python Tests
```bash
cd analytics-engine
pytest tests/
```

#### Frontend Tests
```bash
cd frontend
npm test
```

### Commit Messages
Use conventional commit format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring
- `test:` for adding tests
- `chore:` for maintenance tasks

Example: `feat: add real-time data processing endpoint`

## 🐛 Reporting Issues

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, versions)
- Screenshots if applicable

## 💡 Feature Requests

For feature requests:
- Check existing issues first
- Provide clear use case
- Explain the benefit
- Consider implementation complexity

## 📝 Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation if needed

3. **Test Your Changes**
   ```bash
   # Run all tests
   ./scripts/run-tests.sh
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: your descriptive commit message"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Use descriptive title
   - Explain what changes were made
   - Reference related issues
   - Add screenshots for UI changes

## 🏗️ Architecture Guidelines

### Adding New Features

#### Backend API Endpoints
1. Add controller in `DataAnalytics.API/Controllers/`
2. Add business logic in `DataAnalytics.Core/Services/`
3. Add data models in `DataAnalytics.Core/Models/`
4. Add tests in `DataAnalytics.Tests/`

#### Python Analytics Features
1. Add route in `analytics-engine/src/api/routes/`
2. Add service logic in `analytics-engine/src/services/`
3. Add models in `analytics-engine/src/models/`
4. Add tests in `analytics-engine/tests/`

#### Frontend Components
1. Add components in `frontend/src/components/`
2. Add pages in `frontend/src/pages/`
3. Add services in `frontend/src/services/`
4. Update routing if needed

### Database Changes
1. Create migration: `dotnet ef migrations add YourMigrationName`
2. Update database: `dotnet ef database update`
3. Update seed data if needed

## 🔒 Security Guidelines

- Never commit sensitive information (API keys, passwords)
- Use environment variables for configuration
- Follow OWASP security guidelines
- Validate all user inputs
- Use parameterized queries for database operations

## 📚 Documentation

- Update README.md for significant changes
- Add API documentation for new endpoints
- Update architecture diagrams if needed
- Add inline code comments for complex logic

## 🤝 Community

- Be respectful and inclusive
- Help others learn and grow
- Share knowledge and best practices
- Provide constructive feedback

## 📞 Getting Help

- Check existing documentation
- Search through issues
- Ask questions in discussions
- Contact maintainers if needed

Thank you for contributing to the Data Analytics Platform! 🎉
