---
search:
  boost: 2
---

# Constant `R←{X}(A⍨)Y`

```apl
R←{X}(A⍨)Y
```
[Key to notation](../key-to-notation.md)

`A`,  `X` and `Y` are arrays. The _constant_ operator returns array `A`.

## Examples
```apl

      'mu'⍨ 'any' ⎕NULL   ⍝ Always returns its operand
mu
      1E100 ('mu'⍨) 1j1
mu
      ¯1⍨¨ ⍳2 3
¯1 ¯1 ¯1
¯1 ¯1 ¯1

```

<!-- Hidden search keywords -->
<div style="display: none;">
  ⍨
  constant
</div>
