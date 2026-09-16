---
search:
  boost: 2
---

# Current Thread Identity

```apl
R←⎕TID
```
[Key to notation](../key-to-notation.md)

`R` is a simple integer scalar whose value is the number of the current thread.

## Examples
```apl
      ⎕TID     ⍝ Base thread number
0
 
      ⍎&'⎕TID' ⍝ Thread number of async ⍎.
1
```

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕TID TID
</div>
