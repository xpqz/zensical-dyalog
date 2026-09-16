---
search:
  boost: 2
---

# Timestamp `R←⎕TS`

```apl
R←⎕TS
```
[Key to notation](../key-to-notation.md)

This is a seven element vector which identifies the clock time set on the particular installation as follows:

|--------|-----------|
|`⎕TS[1]`|Year       |
|`⎕TS[2]`|Month      |
|`⎕TS[3]`|Day        |
|`⎕TS[4]`|Hour       |
|`⎕TS[5]`|Minute     |
|`⎕TS[6]`|Second     |
|`⎕TS[7]`|Millisecond|

## Example
```apl
      ⎕TS
1989 7 11 10 42 59 123
```

On some systems, where time is maintained only to the nearest second, a zero is returned for the seventh (millisecond) field.

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕TS TS
</div>
