# CRUSH Development Guidelines

## Core Commands

### Package Management (use uv only)
- Add dependency: `uv add package_name`
- Add dev dependency: `uv add --dev package_name`
- Run tools: `uv run tool_name`
- Upgrade package: `uv add package_name --upgrade-package package_name`

### Code Quality Tools
- Format code: `uv run ruff format .`
- Check linting: `uv run ruff check .`
- Fix linting issues: `uv run ruff check . --fix`
- Type checking: `uv run pyright`
- Run all checks: `uv run ruff check . && uv run pyright`

### Testing
- Run all tests: `uv run pytest`
- Run specific test file: `uv run pytest tests/test_file.py`
- Run specific test: `uv run pytest tests/test_file.py::test_name`
- Run with coverage: `uv run pytest --cov=src`
- Run BDD tests: `uv run pytest tests_bdd/`

## Code Style Guidelines

### Naming Conventions
- Functions/variables: snake_case
- Classes: PascalCase
- Constants: UPPER_SNAKE_CASE

### Imports
- Follow isort ordering (stdlib, third-party, first-party)
- No unused imports
- Group imports at the top of the file

### Code Structure
- Type hints required for all functions
- Public APIs must have docstrings
- Functions should be small and focused
- Prefer early returns to avoid nested conditions
- Use constants instead of magic values
- Follow existing code patterns exactly

### Error Handling
- Handle expected errors gracefully
- Use specific exception types
- Log unexpected errors appropriately

## Project Structure Notes

### Frontend (dbr_mvp/frontend)
- Main entry: src/main.py
- UI components: src/frontend/components/
- Pages: src/frontend/pages/

### Backend (dbr_mvp/backend)
- Main entry: src/dbr/main.py
- API endpoints: src/dbr/api/
- Models: src/dbr/models/
- Core logic: src/dbr/core/
- Services: src/dbr/services/

## Development Philosophy
- Simplicity over cleverness
- Readability is paramount
- Test edge cases and error conditions
- Follow existing patterns
- Keep changes minimal and focused