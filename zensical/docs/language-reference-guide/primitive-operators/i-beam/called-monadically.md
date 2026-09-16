---
search:
  boost: 2
---


# Called Monadically? `R←900⌶Y`

```apl
R←900⌶Y
```
[Key to notation](../../key-to-notation.md)

Identifies how the current function was called. It reports whether the nearest tradfn on the stack was called without a left argument or not.

`Y` may be any array.

The result `R` is Boolean. 1 means that the nearest tradfn was called monadically; 0 means that it wasn't. If there is no function on the stack, the result is 0.

## Example
```apl
     ∇ r←{left}foo right
[1]    r←900⌶⍬
     ∇
      foo 10
1
      0 foo 10
0

```

<!-- Hidden search keywords -->
<div style="display: none;">
  900⌶
</div>
