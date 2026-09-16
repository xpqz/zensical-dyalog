---
search:
  boost: 2
---

# Greater Than

```apl
R←X>Y
```
[Key to notation](../key-to-notation.md)

`Y` must be numeric. `X` must be numeric. `R` is Boolean. `R` is 1 if `X` is greater than `Y` and `X=Y` is 0. Otherwise `R` is 0.

`⎕CT` and `⎕DCT` are  implicit arguments of _greater than_.

## Examples
```apl
      1 2 3 4 5 > 2
0 0 1 1 1
 
      ⎕CT←1E¯10
 
      1 1.00000000001 1.000000001 > 1
0 0 1
```

<!-- Hidden search keywords -->
<div style="display: none;">
  > greater
</div>
