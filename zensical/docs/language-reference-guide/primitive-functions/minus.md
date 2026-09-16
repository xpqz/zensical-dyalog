---
search:
  boost: 2
---

# Minus `R←X-Y`

```apl
R←X-Y
```
[Key to notation](../key-to-notation.md)

`Y` may be any numeric array. `X` may be any numeric array. `R` is numeric. The value of `R` is the difference between `X` and `Y`.

This function is also known as Subtract.

## Example
```apl
      3 ¯2 4 0 - 2 1 ¯2 4
1 ¯3 6 ¯4
 
      2j3-.3j5  ⍝ (a+bi)-(c+di) = (a-c)+(b-d)i
1.7J¯2
```

<!-- Hidden search keywords -->
<div style="display: none;">
  - minus subtract
</div>
