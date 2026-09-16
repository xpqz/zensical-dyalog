---
search:
  boost: 2
---

# NOR `R←X⍱Y`

```apl
R←X⍱Y
```
[Key to notation](../key-to-notation.md)

`Y` must be a Boolean array. `X` must be a Boolean array. `R` is Boolean. The value of `R` is the truth value of the proposition "neither `X` nor `Y`", and is determined as follows:
```apl
             X   Y     R
      
             0   0     1
             0   1     0
             1   0     0
             1   1     0
```

## Example
```apl
      0 0 1 1 ⍱ 0 1 0 1
1 0 0 0
```

<!-- Hidden search keywords -->
<div style="display: none;">
  ⍱ nor
</div>
