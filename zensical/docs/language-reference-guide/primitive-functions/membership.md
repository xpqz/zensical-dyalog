---
search:
  boost: 2
---

# Membership `R←X∊Y`

```apl
R←X∊Y
```
[Key to notation](../key-to-notation.md)

`Y` may be any array.  `X` may be any array.  `R` is Boolean. An element of `R` is 1 if the corresponding element of `X` can be found in `Y`.

An element of `X` is considered identical to an element in `Y` if `X≡Y` returns 1 for those elements.

`⎕CT` and `⎕DCT` are  implicit arguments of _membership_.

## Examples
```apl
      'THIS NOUN' ∊ 'THAT WORD'
1 1 0 0 1 0 1 0 0
 
      'CAT' 'DOG' 'MOUSE' ∊ 'CAT' 'FOX' 'DOG' 'LLAMA'
1 1 0
```

For performance information, see [Programmer's Guide: "Search Functions and Hash Tables"](../../programming-reference-guide/introduction/search-functions-and-hash.md).

<!-- Hidden search keywords -->
<div style="display: none;">
  ∊ member membership
</div>
