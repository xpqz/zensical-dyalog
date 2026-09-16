---
search:
  boost: 2
---

# Type

```apl
(⎕ML<1) R←∊Y
```
[Key to notation](../key-to-notation.md)

Migration level must be such that `⎕ML<1` (otherwise `∊` means _enlist_. See [Enlist](enlist.md)).

`Y` may be any array.  `R` is an array with the same shape and structure as `Y` in which a numeric value is replaced by 0 and a character value is replaced by `' '`.

## Examples
```apl
      ∊(2 3⍴⍳6)(1 4⍴'TEXT')
 0 0 0
 0 0 0
 
      ' '=∊'X'
1
```

<!-- Hidden search keywords -->
<div style="display: none;">
  ∊ type
</div>
