---
search:
  boost: 2
---

# Intersection

```apl
R←X∩Y
```
[Key to notation](../key-to-notation.md)

`Y` must be  a scalar or vector.  `X` must be a scalar or vector.  A scalar `X` or `Y` is treated as a one-element vector.  `R` is a vector composed of items occurring in both `X` and `Y` in the order of occurrence in `X`.  If an item is repeated in `X` and also occurs in `Y`, the item is also repeated in `R`.

Items in `X` and `Y` are considered the same if `X≡Y` returns 1 for those items.

`⎕CT` and `⎕DCT` are  implicit arguments of _intersection_.

## Examples
```apl
      'ABRA'∩'CAR'
ARA
 
      1 'PLUS' 2 ∩ ⍳5
1 2
```

For performance information, see [Programmer's Guide: "Search Functions and Hash Tables"](../../programming-reference-guide/introduction/search-functions-and-hash.md).

<!-- Hidden search keywords -->
<div style="display: none;">
  ∩ intersection
</div>
