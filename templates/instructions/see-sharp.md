# C# (.NET) Development Instructions

## Code Style Guidelines

- Follow Microsoft C# coding conventions
- Use PascalCase for class names and public members
- Use camelCase for private fields and local variables
- Prefix private fields with underscore: `_fieldName`
- Use implicit typing (`var`) when type is obvious

## Best Practices

- Use nullable reference types (C# 8.0+)
- Leverage LINQ for collection operations
- Implement IDisposable pattern for resource cleanup
- Use async/await for asynchronous operations
- Follow SOLID principles

## Common Patterns

### Async/Await Pattern
```csharp
public async Task<Result> GetDataAsync()
{
    try
    {
        var data = await _httpClient.GetAsync(url);
        return await data.Content.ReadAsAsync<Result>();
    }
    catch (HttpRequestException ex)
    {
        _logger.LogError(ex, "Failed to retrieve data");
        throw;
    }
}
```

### Dependency Injection
```csharp
public class MyService : IMyService
{
    private readonly ILogger<MyService> _logger;
    private readonly IDataRepository _repository;

    public MyService(ILogger<MyService> logger, IDataRepository repository)
    {
        _logger = logger;
        _repository = repository;
    }
}
```

### IDisposable Pattern
```csharp
public class ResourceManager : IDisposable
{
    private bool _disposed = false;

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    protected virtual void Dispose(bool disposing)
    {
        if (_disposed) return;

        if (disposing)
        {
            // Dispose managed resources
        }

        _disposed = true;
    }
}
```

## Anti-Patterns to Avoid

- Using `async void` (except for event handlers)
- Catching exceptions without handling them
- Not disposing IDisposable objects
- Mixing synchronous and asynchronous code incorrectly
- Using reflection excessively

## Testing Conventions

- Use xUnit, NUnit, or MSTest for unit testing
- Use Moq or NSubstitute for mocking
- Test file naming: `ClassNameTests.cs`
- Use [Fact] and [Theory] attributes (xUnit)
- Follow AAA pattern: Arrange, Act, Assert

## Documentation Standards

- Use XML documentation comments (///)
- Document public APIs, classes, and methods
- Use `<summary>`, `<param>`, `<returns>` tags
- Include `<exception>` tags for thrown exceptions
- Provide code examples in `<example>` tags

## Project-Specific Customizations

Add your team-specific guidelines below:
<!-- Customize this section for your project -->
