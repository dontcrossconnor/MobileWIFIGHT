# Contributing to WiFi Penetration Testing Platform

Thank you for your interest in contributing to the MobileWIFIGHT project! This document provides guidelines for contributing to this project.

## ⚠️ Legal Notice

This project is designed exclusively for **authorized penetration testing and security research**. All contributors must:

1. Agree that contributions will only be used for lawful purposes
2. Not contribute features designed for illegal activities
3. Ensure all contributions comply with applicable laws
4. Include appropriate warnings for potentially dangerous features

## Code of Conduct

### Be Responsible
- Only contribute features for authorized security testing
- Include appropriate warnings and safety checks
- Never encourage or enable illegal activity
- Respect applicable laws and regulations

### Be Professional
- Treat all contributors with respect
- Provide constructive feedback
- Follow project standards and conventions
- Document your code thoroughly

## Development Principles

### 1. Test-Driven Development (TDD)

This project follows **strict TDD**:

1. **Write tests first** - Tests define expected behavior
2. **Watch them fail** (Red) - Ensure test actually tests something
3. **Write minimal code** to pass (Green)
4. **Refactor** while keeping tests passing

**No exceptions**: Every feature must have tests written first.

### 2. Immutable Contracts

The following files are **FROZEN** and cannot be modified without explicit approval:

- `backend/app/models/*.py` - Data models
- `backend/app/services/interfaces.py` - Service interfaces
- `frontend/src/types/models.ts` - TypeScript types
- `CONTRACTS.md` - Contract documentation

**To modify contracts:**
1. Open an issue explaining the need
2. Get explicit approval from maintainers
3. Update ALL affected tests
4. Increment version number
5. Document migration path

### 3. Code Quality Standards

**Required:**
- 90%+ test coverage for unit tests
- 80%+ test coverage for integration tests
- 100% coverage for critical paths
- Pass all linting (Black, Ruff)
- Pass type checking (MyPy strict mode)
- All tests passing

**Code Style:**
- Backend: Follow PEP 8, use Black formatter
- Frontend: Follow TypeScript best practices
- Use meaningful variable names
- Add docstrings to all public methods
- Comment complex logic

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork:
git clone https://github.com/YOUR_USERNAME/MobileWIFIGHT.git
cd MobileWIFIGHT

# Add upstream remote
git remote add upstream https://github.com/dontcrossconnor/MobileWIFIGHT.git
```

### 2. Set Up Development Environment

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Install system dependencies (Linux)
sudo apt-get install -y aircrack-ng hcxtools hashcat
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

## Making Changes

### For New Features

1. **Write tests first**:
   ```bash
   # Add tests to appropriate test file
   # Example: backend/app/tests/test_adapter_service.py
   
   def test_adapter_service_new_feature_works():
       """Test new feature does X"""
       # Arrange
       service = AdapterService()
       
       # Act
       result = await service.new_feature()
       
       # Assert
       assert result.something == expected
   ```

2. **Run tests (watch them fail)**:
   ```bash
   cd backend
   pytest app/tests/test_adapter_service.py::test_adapter_service_new_feature_works -v
   ```

3. **Implement feature**:
   ```python
   # backend/app/services/adapter.py
   
   async def new_feature(self):
       """Implementation that makes test pass"""
       # Your code here
       pass
   ```

4. **Run tests (watch them pass)**:
   ```bash
   pytest app/tests/test_adapter_service.py::test_adapter_service_new_feature_works -v
   ```

5. **Refactor if needed** (keep tests passing)

6. **Check coverage**:
   ```bash
   pytest --cov=app --cov-report=term-missing --cov-fail-under=90
   ```

### For Bug Fixes

1. **Write test that reproduces bug**:
   ```python
   def test_bug_description():
       """Test that demonstrates the bug"""
       # This test should fail initially
       pass
   ```

2. **Fix the bug** (make test pass)

3. **Ensure no regressions** (all tests pass)

## Pull Request Process

### 1. Before Submitting

**Checklist:**
- [ ] All tests passing
- [ ] Coverage requirements met (90% unit, 80% integration)
- [ ] Code formatted (Black for Python, Prettier for TypeScript)
- [ ] Linting passed (Ruff, ESLint)
- [ ] Type checking passed (MyPy)
- [ ] No contract violations
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

**Run pre-commit checks:**
```bash
# Backend
cd backend
black .
ruff check .
mypy app/
pytest --cov=app --cov-fail-under=90

# Frontend
cd frontend
npm run lint
npm run type-check
npm test
```

### 2. Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): brief description

Longer description if needed.

BREAKING CHANGE: Description of breaking changes if any.
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples:**
```bash
git commit -m "feat(adapter): add support for RTL8814AU chipset"
git commit -m "fix(scanner): resolve handshake capture race condition"
git commit -m "test(cracker): add GPU provider integration tests"
git commit -m "docs(api): update WebSocket event documentation"
```

### 3. Submit Pull Request

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR on GitHub**:
   - Use descriptive title following commit convention
   - Fill out PR template completely
   - Reference related issues
   - Explain motivation and implementation approach

3. **PR Template**:
   ```markdown
   ## Description
   Brief description of changes.

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Tests written and passing
   - [ ] Coverage requirements met
   - [ ] Integration tests added (if applicable)

   ## Checklist
   - [ ] Code follows project style
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No contract violations
   ```

### 4. Code Review

- Respond to feedback promptly
- Make requested changes in new commits
- Don't force-push after review starts
- Engage in constructive discussion

### 5. Merging

Maintainers will merge once:
- All tests passing
- Coverage requirements met
- Code review approved
- CI/CD pipeline green
- No conflicts with main branch

## Testing Guidelines

### Unit Tests

**Location**: `backend/app/tests/test_*.py`

**Requirements**:
- 90%+ coverage
- Fast execution (< 1s per test)
- No external dependencies (use mocks)
- Test one thing at a time

**Example**:
```python
@pytest.mark.asyncio
async def test_adapter_service_detect_adapters_returns_list():
    """Test that detect_adapters returns a list of adapters"""
    # Arrange
    service = AdapterService()
    mock_network_manager.get_interfaces.return_value = [...]
    
    # Act
    result = await service.detect_adapters()
    
    # Assert
    assert isinstance(result, list)
    assert all(isinstance(a, Adapter) for a in result)
```

### Integration Tests

**Location**: Same test files, marked with `@pytest.mark.integration`

**Requirements**:
- 80%+ coverage
- Test actual tool integrations
- May require real hardware
- Can be slower

**Example**:
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_adapter_monitor_mode_toggle():
    """Test toggling monitor mode with real adapter"""
    pytest.skip("Requires Alfa adapter")
    # Test with real hardware
```

**Run integration tests**:
```bash
pytest -m integration
```

**Skip integration tests**:
```bash
pytest -m "not integration"
```

## Project Structure

```
MobileWIFIGHT/
├── backend/              # Python backend
│   ├── app/
│   │   ├── api/         # FastAPI routes (to be implemented)
│   │   ├── core/        # Core config (to be implemented)
│   │   ├── models/      # Data models (FROZEN)
│   │   ├── services/    # Service implementations
│   │   ├── tools/       # Tool wrappers (to be implemented)
│   │   └── tests/       # Test suites
│   └── requirements.txt
│
├── frontend/            # Electron + React frontend
│   ├── src/
│   │   ├── components/ # React components (to be implemented)
│   │   ├── views/      # Main views (to be implemented)
│   │   ├── types/      # TypeScript types (FROZEN)
│   │   └── api/        # API client (to be implemented)
│   └── package.json
│
├── docs/               # Documentation
├── LICENSE             # MIT License
└── README.md           # Project overview
```

## Documentation

### Documenting Code

**Python**:
```python
async def method_name(self, param: str) -> Result:
    """Brief one-line description.
    
    Longer description if needed. Explain what the method does,
    not how it does it.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When parameter is invalid
    """
    pass
```

**TypeScript**:
```typescript
/**
 * Brief one-line description.
 * 
 * Longer description if needed.
 * 
 * @param param - Description of parameter
 * @returns Description of return value
 * @throws {Error} When something goes wrong
 */
function methodName(param: string): Result {
    // Implementation
}
```

### Updating Documentation

When making changes, update:
- Docstrings/JSDoc comments
- README.md (if public API changes)
- ARCHITECTURE.md (if architecture changes)
- IMPLEMENTATION_GUIDE.md (if process changes)
- API documentation (if endpoints change)

## Need Help?

- **Questions**: Open a [Discussion](https://github.com/dontcrossconnor/MobileWIFIGHT/discussions)
- **Bugs**: Open an [Issue](https://github.com/dontcrossconnor/MobileWIFIGHT/issues)
- **Security**: See SECURITY.md (to be created)

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Git commit history
- Release notes

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to MobileWIFIGHT!**

Remember: With great power comes great responsibility. Use and contribute to this project ethically and legally.
