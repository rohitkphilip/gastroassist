# Contributing to GastroAssist

Thank you for your interest in contributing to GastroAssist! This guide will help you understand our development process and how you can participate in improving the system.

## Code of Conduct

Please read and follow our [Code of Conduct](https://github.com/your-organization/gastroassist/blob/main/CODE_OF_CONDUCT.md) to create a positive environment for everyone.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** to your local machine
3. **Set up the development environment** following our [Setup Guide](./setup-guide.md)
4. **Create a new branch** for your feature or bugfix
5. **Make your changes** and commit them
6. **Push your branch** to your fork
7. **Submit a pull request** to the main repository

## Development Process

### Branching Strategy

- `main` - Stable, production-ready code
- `develop` - Integration branch for features
- `feature/name` - Individual feature branches
- `bugfix/name` - Bug fix branches
- `docs/name` - Documentation updates

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) standard:

```
feat: add new search filtering option
docs: update installation instructions
fix: resolve issue with query parsing
chore: update dependencies
```

### Pull Request Process

1. Create a pull request from your feature branch to our `develop` branch
2. Fill in the PR template with details about your changes
3. Link any relevant issues
4. Wait for code review and address any feedback
5. After approval, your PR will be merged

## Testing Guidelines

All contributions should include appropriate tests:

- **Unit tests** for individual components
- **Integration tests** for component interactions
- **End-to-end tests** for critical user workflows

See our [Testing Guide](./testing-guide.md) for detailed information.

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/backend/test_knowledge_router.py

# Run with coverage report
pytest --cov=app tests/
```

## Documentation

Code should be well-documented with clear comments and docstrings. Additionally, update any relevant documentation:

- README updates for user-facing changes
- API documentation for endpoint changes
- Architecture documentation for structural changes

## Code Style

We follow these style guidelines:

- **Python**: [PEP 8](https://pep8.org/) style guide
- **TypeScript/JavaScript**: Standard ESLint configuration
- **React**: Functional components with hooks

### Formatting

We use:
- **Black** for Python code formatting
- **Prettier** for TypeScript/JavaScript formatting

## Submitting Issues

### Bug Reports

When submitting a bug report, please include:

1. Clear description of the issue
2. Steps to reproduce
3. Expected vs actual behavior
4. Environment details (OS, browser, etc.)
5. Screenshots if applicable

### Feature Requests

When submitting a feature request, please include:

1. Clear description of the proposed feature
2. Rationale and use cases
3. Any implementation ideas you have
4. Mock-ups if applicable

## Review Process

Each pull request requires:

1. Passing CI checks
2. Code review by at least one maintainer
3. All feedback addressed
4. Documentation updates if needed

## Getting Help

If you need assistance:

- Check existing documentation
- Look for similar issues in the issue tracker
- Join our Discord community for real-time help
- Contact a maintainer directly for complex questions

## Medical Accuracy

Since GastroAssist provides medical information, we have additional requirements:

1. All medical content must be evidence-based
2. Include references to authoritative sources
3. Be clear about limitations and uncertainties
4. Avoid diagnostic or prescriptive language

Medical content may undergo additional review by healthcare professionals.

## License

By contributing to GastroAssist, you agree that your contributions will be licensed under the project's [MIT License](https://github.com/your-organization/gastroassist/blob/main/LICENSE).

Thank you for contributing to better healthcare technology!
