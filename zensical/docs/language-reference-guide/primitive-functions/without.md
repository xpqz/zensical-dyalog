---
search:
  boost: 2
---

# Without

```apl
R←X~Y
```
[Key to notation](../key-to-notation.md)

`X` must be a scalar or vector.  `R` is a vector of the elements of `X` excluding those elements which occur in `Y` taken in the order in which they occur in `X`.

Elements of `X` and `Y` are considered the same if `X≡Y` returns 1 for those elements.

`⎕CT` and `⎕DCT` are  implicit arguments of _without_. _Without_ is also known as _excluding_.

## Examples
```apl
      'HELLO'~'GOODBYE'
HLL
      'MONDAY' 'TUESDAY' 'WEDNESDAY'~'TUESDAY' 'FRIDAY'
 MONDAY  WEDNESDAY
 
      5 10 15~⍳10
15
```

For performance information, see [Programmer's Guide: "Search Functions and Hash Tables"](../../programming-reference-guide/introduction/search-functions-and-hash.md).

<!-- Hidden search keywords -->
<div style="display: none;">
  ~ without
</div>
