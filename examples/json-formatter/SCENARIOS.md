# JSON Formatter Scenarios

> Goal: JSON formatter output matches `jq` behavior exactly
> Verification: format same input with both, compare output byte-for-byte
> Oracle: `jq .` command

Status: [ ] pending, [x] passing, [~] partial (needs upstream change)

---

## Phase 1: Basic Formatting

### 1.1 Primitive Values

- [ ] null literal
- [ ] true literal
- [ ] false literal
- [ ] integer zero
- [ ] positive integer
- [ ] negative integer
- [ ] float with decimal
- [ ] float with exponent notation
- [ ] empty string
- [ ] simple string
- [ ] string with unicode escapes
- [ ] string with special characters (\n, \t, \\, \")

### 1.2 Simple Structures

- [ ] empty object `{}`
- [ ] object with one key
- [ ] object with multiple keys — key ordering
- [ ] empty array `[]`
- [ ] array with one element
- [ ] array with multiple elements
- [ ] array with mixed types

### 1.3 Indentation

- [ ] nested object — 2-space indent
- [ ] nested array — 2-space indent
- [ ] 3 levels deep
- [ ] 5 levels deep
- [ ] array inside object
- [ ] object inside array

## Phase 2: Edge Cases

### 2.1 Numeric Precision

- [ ] large integer (64-bit boundary)
- [ ] very small float
- [ ] negative zero
- [ ] scientific notation normalization

### 2.2 String Edge Cases

- [ ] empty key name
- [ ] key with spaces
- [ ] key with dots
- [ ] value with raw newlines
- [ ] value with null bytes
- [ ] very long string (10KB)

### 2.3 Structural Edge Cases

- [ ] deeply nested (50 levels)
- [ ] object with 1000 keys
- [ ] array with 10000 elements
- [ ] duplicate keys — last wins
- [ ] trailing comma handling (invalid JSON)
