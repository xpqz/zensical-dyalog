---
search:
  boost: 2
---

# Greater Than Or Equal To

```apl
R←X≥Y
```
[Key to notation](../key-to-notation.md)

`Y` must be numeric. `X` must be numeric. `R` is Boolean. `R` is 1 if `X` is greater than `Y` or `X=Y`. Otherwise `R` is 0.

`⎕CT` and `⎕DCT` are  implicit arguments of _greater than or equal to_.

## Examples
```apl
      1 2 3 4 5 ≥ 3
0 0 1 1 1
 
      ⎕CT←1E¯10
 
      1≥1
1
 
      1≥1.00000000001
1
 
      1≥1.00000001
0
```

<!-- Hidden search keywords -->
<div style="display: none;">
  ≥ greater
</div>
