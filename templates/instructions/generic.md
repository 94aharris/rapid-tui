# General Development Instructions

## Code Style Guidelines

- Use consistent indentation (2 or 4 spaces, no tabs)
- Maximum line length: 100 characters
- Use descriptive variable and function names
- Follow language-specific naming conventions
- Add comments for complex logic

## Best Practices

- Write self-documenting code
- Keep functions small and focused (single responsibility)
- Use version control effectively (atomic commits, descriptive messages)
- Handle errors gracefully
- Log important events and errors

## Common Patterns

### Error Handling
```
try {
    // Operation that might fail
    result = performOperation()
} catch (error) {
    // Handle error appropriately
    logError(error)
    throw error
}
```

### Logging
```
logger.info("Operation started")
logger.error("Operation failed: " + errorMessage)
logger.debug("Detailed debug information")
```

## Anti-Patterns to Avoid

- Hardcoded values (use configuration files)
- Copy-paste code duplication
- Overly complex nested logic
- Magic numbers without explanation
- Ignoring errors silently

## Testing Conventions

- Write unit tests for all business logic
- Use integration tests for component interactions
- Test edge cases and error conditions
- Aim for high code coverage
- Keep tests maintainable and readable

## Documentation Standards

- Document public APIs and interfaces
- Include usage examples
- Explain complex algorithms
- Keep documentation up-to-date with code changes
- Use inline comments sparingly

## Project-Specific Customizations

Add your team-specific guidelines below:
<!-- Customize this section for your project -->