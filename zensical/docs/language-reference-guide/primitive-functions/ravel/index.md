---
search:
  boost: 2
---

# Ravel

```apl
R←,Y
```
[Key to notation](../../key-to-notation.md)

`Y` may be any array.  `R` is a vector of the elements of `Y` taken in row-major order.

## Examples
```apl
      M
1 2 3
4 5 6
 
      ,M
1 2 3 4 5 6
 
      A
ABC
DEF
GHI
JKL
      ,A
ABCDEFGHIJKL
 
      ⍴,10
1
```

See also: [Ravel with Axes](ravel-with-axes.md).

<!-- Hidden search keywords -->
<div style="display: none;">
  , ravel
</div>
