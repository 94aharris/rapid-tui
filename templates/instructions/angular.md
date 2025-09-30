# Angular/TypeScript Development Instructions

## Code Style Guidelines

- Follow Angular style guide conventions
- Use TypeScript strict mode
- Maximum line length: 120 characters
- Use single quotes for strings
- Add semicolons at end of statements

## Best Practices

- Use Angular CLI for generating components, services, and modules
- Implement OnDestroy interface and unsubscribe from observables
- Use async pipe in templates to handle observables
- Leverage dependency injection for services
- Use lazy loading for feature modules

## Common Patterns

### Component Structure
```typescript
import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'app-example',
  templateUrl: './example.component.html',
  styleUrls: ['./example.component.scss']
})
export class ExampleComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();

  ngOnInit(): void {
    // Initialization logic
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

### Service with HTTP
```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  constructor(private http: HttpClient) {}

  getData(): Observable<Data[]> {
    return this.http.get<Data[]>('/api/data');
  }
}
```

## Anti-Patterns to Avoid

- Subscribing to observables in components without unsubscribing
- Direct DOM manipulation (use Renderer2 or Angular directives)
- Logic in constructors (use ngOnInit instead)
- Mutating input properties directly

## Testing Conventions

- Use Jasmine and Karma for unit testing
- Use Protractor or Cypress for E2E testing
- Test file naming: `*.spec.ts`
- Use TestBed for component testing
- Mock services and dependencies

## Documentation Standards

- Use TSDoc comments for public APIs
- Document component inputs and outputs
- Include usage examples in component documentation
- Document service methods and return types

## Project-Specific Customizations

Add your team-specific guidelines below:
<!-- Customize this section for your project -->
