# Contributing to ChartPredictor

We welcome contributions to ChartPredictor! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- A GitHub account

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/xplizet/ChartPredictor.git
   cd ChartPredictor
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

5. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🎯 Types of Contributions

We welcome several types of contributions:

### 🐛 Bug Reports
- Use the bug report template
- Include steps to reproduce
- Provide system information
- Include relevant logs or screenshots

### ✨ Feature Requests
- Use the feature request template
- Describe the problem you're solving
- Provide detailed specifications
- Consider backwards compatibility

### 💻 Code Contributions
- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test coverage improvements

### 📚 Documentation
- README improvements
- Code documentation
- User guides
- API documentation

## 🔧 Development Guidelines

### Code Style
- Follow **PEP 8** style guidelines
- Use **type hints** for all functions and methods
- Write **descriptive variable and function names**
- Include **docstrings** for all public methods and classes

### Code Quality Tools
We use several tools to maintain code quality:

```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/

# Run all quality checks
python -m pytest tests/ --cov=src/
```

### Testing
- Write tests for all new features
- Maintain or improve test coverage
- Run the full test suite before submitting
- Include both unit tests and integration tests

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/ --cov-report=html
```

### Commit Guidelines
Follow the **Conventional Commits** specification:

- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `style:` formatting changes
- `refactor:` code refactoring
- `test:` adding or modifying tests
- `chore:` maintenance tasks

**Examples:**
```
feat: add Fibonacci retracement analysis
fix: resolve division by zero in RSI calculation
docs: update installation instructions
test: add unit tests for pattern detection
```

### Branch Naming
Use descriptive branch names:
- `feature/add-fibonacci-analysis`
- `fix/rsi-calculation-error`
- `docs/update-readme`
- `test/pattern-detection-coverage`

## 📋 Pull Request Process

### Before Submitting
1. **Ensure all tests pass**:
   ```bash
   pytest tests/
   ```

2. **Check code quality**:
   ```bash
   black --check src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

3. **Update documentation** if needed
4. **Add or update tests** for your changes
5. **Update CHANGELOG.md** if appropriate

### Pull Request Guidelines
1. **Use the PR template**
2. **Write a clear title and description**
3. **Reference related issues** using `#issue-number`
4. **Include screenshots** for UI changes
5. **Request review** from maintainers
6. **Respond to feedback** promptly

### PR Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Code is properly commented
- [ ] Tests added/updated and passing
- [ ] Documentation updated if needed
- [ ] No breaking changes (or clearly documented)
- [ ] CHANGELOG.md updated if appropriate

## 🧪 Testing Guidelines

### Test Structure
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── fixtures/       # Test data and fixtures
└── conftest.py     # Pytest configuration
```

### Writing Tests
- Use **descriptive test names**
- Follow **AAA pattern** (Arrange, Act, Assert)
- **Mock external dependencies** (APIs, file system)
- Test **both success and error cases**
- Include **edge cases** and **boundary conditions**

### Example Test
```python
def test_calculate_rsi_with_valid_data():
    # Arrange
    prices = [10, 11, 12, 11, 10, 9, 10, 11]
    extractor = ChartExtractor(default_settings)
    
    # Act
    rsi = extractor._calculate_rsi_manual(prices, period=14)
    
    # Assert
    assert 0 <= rsi <= 100
    assert isinstance(rsi, float)
```

## 🐛 Bug Report Guidelines

When reporting bugs, please include:

1. **Clear description** of the problem
2. **Steps to reproduce** the issue
3. **Expected behavior**
4. **Actual behavior**
5. **System information**:
   - OS version
   - Python version
   - ChartPredictor version
   - Relevant dependencies
6. **Log files** or error messages
7. **Screenshots** if applicable

## ✨ Feature Request Guidelines

When requesting features:

1. **Describe the problem** you're trying to solve
2. **Explain your proposed solution**
3. **Consider alternatives** you've thought about
4. **Provide use cases** and examples
5. **Consider impact** on existing functionality
6. **Think about implementation** complexity

## 📱 Technical Considerations

### Architecture
- **Modular design**: Keep components loosely coupled
- **Error handling**: Implement comprehensive error handling
- **Logging**: Use structured logging with appropriate levels
- **Configuration**: Make features configurable when appropriate
- **Performance**: Consider performance implications of changes

### Dependencies
- **Minimize new dependencies** where possible
- **Use well-maintained packages** with good community support
- **Consider optional dependencies** for non-core features
- **Update requirements.txt** and setup.py appropriately

### Financial Software Considerations
- **Accuracy is critical**: Test thoroughly with real market data
- **Performance matters**: Financial analysis needs to be fast
- **Risk disclaimers**: Include appropriate warnings and disclaimers
- **Data validation**: Validate all input data rigorously

## 🏷️ Issue Labels

We use labels to categorize issues:

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `priority-high`: High priority issue
- `priority-low`: Low priority issue
- `wontfix`: This will not be worked on

## 🎉 Recognition

Contributors are recognized in:
- README.md contributors section
- CHANGELOG.md for significant contributions
- GitHub releases for major features

## ❓ Getting Help

If you need help:

1. **Check existing issues** and documentation
2. **Join discussions** in GitHub Discussions
3. **Ask questions** in issues with the `question` label
4. **Contact maintainers** for complex questions

## 📄 Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

### Our Standards

- **Be respectful** and inclusive
- **Provide constructive feedback**
- **Focus on the technical merits**
- **Help others learn and grow**
- **Assume good intentions**

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks or trolling
- Publishing private information
- Other conduct inappropriate for a professional setting

## 🙏 Thank You

Thank you for contributing to ChartPredictor! Your efforts help make financial analysis tools more accessible to everyone.

---

For questions about this guide, please open an issue or contact the maintainers.