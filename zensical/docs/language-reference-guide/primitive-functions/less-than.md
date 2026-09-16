---
search:
  boost: 2
---

# Less Than `R←X<Y`

```apl
R←X<Y
```
[Key to notation](../key-to-notation.md)

`Y` may be any numeric array. `X` may be any numeric array. `R` is Boolean. `R` is 1 if `X` is less than `Y` and `X=Y` is 0. Otherwise `R` is 0.

`⎕CT` and `⎕DCT` are  implicit arguments of _less than_.

## Examples
```apl
      (2 4) (6 8 10) < 6
 1 1  0 0 0
 
      ⎕CT←1E¯10
 
      1 0.99999999999 0.9999999999<1
0 0 1
```

<!-- Hidden search keywords -->
<div style="display: none;">
  < less
</div>
