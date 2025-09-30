# Python Development Instructions

## Code Style Guidelines

- Follow PEP 8 style guidelines for Python code
- Use type hints for function parameters and return values
- Maximum line length: 88 characters (Black formatter standard)
- Use docstrings for all public modules, functions, classes, and methods

## Best Practices

- Prefer explicit over implicit code
- Use context managers (`with` statements) for resource management
- Leverage list/dict comprehensions for simple transformations
- Use `pathlib.Path` for file system operations instead of `os.path`
- Prefer `f-strings` for string formatting

## Common Patterns

### Error Handling
```python
try:
    # Operation that might fail
    result = risky_operation()
except SpecificException as e:
    # Handle specific exception
    logger.error(f"Operation failed: {e}")
    raise
finally:
    # Cleanup if needed
    cleanup()
```

### Logging
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Operation completed successfully")
```

## Anti-Patterns to Avoid

- Bare `except:` clauses without exception type
- Mutable default arguments in function definitions
- Using `*` imports (`from module import *`)
- Mixing tabs and spaces for indentation

## Testing Conventions

- Use `pytest` for testing framework
- Test file naming: `test_*.py` or `*_test.py`
- Use fixtures for test setup and teardown
- Aim for >80% code coverage

## Documentation Standards

- Use Google-style or NumPy-style docstrings
- Include type information in docstrings
- Document exceptions raised
- Provide usage examples for complex functions

## Project-Specific Customizations

Add your team-specific guidelines below:
<!-- Customize this section for your project -->