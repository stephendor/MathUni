```markdown
# MathUni Development Patterns

> Auto-generated skill from repository analysis

## Overview
MathUni is a TypeScript-based repository focused on organizing and delivering mathematics lessons, problem sets, and solutions. The codebase is framework-free, emphasizing modular content organization and clear coding standards. This skill outlines the project's conventions, workflows, and best practices for contributing new educational materials and maintaining code quality.

## Coding Conventions

### File Naming
- All files use **kebab-case**.
  - Example: `math-utils.ts`, `lesson-one.html`, `problem-set-one.md`

### Import Style
- Use **relative imports** for modules.
  ```typescript
  import { add } from './math-utils';
  ```

### Export Style
- Prefer **named exports**.
  ```typescript
  // math-utils.ts
  export function add(a: number, b: number): number {
    return a + b;
  }
  ```

### Commit Messages
- Prefixes: `feat`, `fix`, `style`
- Example:  
  ```
  feat: add quadratic equations lesson and problem set
  fix: correct typo in lesson-one.html
  style: format problem-set-two.md for consistency
  ```

## Workflows

### Add New Lesson with Problems and Solutions
**Trigger:** When someone wants to introduce a new lesson topic with associated practice and solutions.  
**Command:** `/new-lesson`

1. **Create or add the lesson HTML file**  
   Place it in:  
   ```
   lessons/{module}/{unit}.html
   ```
   Example:  
   ```
   lessons/algebra/quadratic-equations.html
   ```

2. **Create or add the problem set markdown**  
   Place it in:  
   ```
   problems/sets/{unit}.md
   ```
   Example:  
   ```
   problems/sets/quadratic-equations.md
   ```

3. **Create or add the solutions markdown**  
   Place it in:  
   ```
   problems/solutions/{unit}.md
   ```
   Example:  
   ```
   problems/solutions/quadratic-equations.md
   ```

**Example Directory Structure:**
```
lessons/
  algebra/
    quadratic-equations.html
problems/
  sets/
    quadratic-equations.md
  solutions/
    quadratic-equations.md
```

## Testing Patterns

- **Test files** use the pattern: `*.test.*`
  - Example: `math-utils.test.ts`
- **Testing framework** is not explicitly defined; check for test files following the above pattern.
- Place test files alongside the modules they test or in a dedicated `tests/` directory.

**Example Test File:**
```typescript
// math-utils.test.ts
import { add } from './math-utils';

describe('add', () => {
  it('adds two numbers', () => {
    expect(add(2, 3)).toBe(5);
  });
});
```

## Commands

| Command      | Purpose                                                        |
|--------------|----------------------------------------------------------------|
| /new-lesson  | Add a new lesson with its problem set and solutions            |
```
