---
search:
  boost: 2
---

# Delay

```apl
{R}←⎕DL Y
```
[Key to notation](../key-to-notation.md)

`Y` must be a simple non-negative single numeric value (of any rank).  A pause of approximately `Y` seconds is caused.

The [shy](../../programming-reference-guide/introduction/results.md#shy-results) result `R` is a scalar numeric value indicating the length of the pause in seconds.

The pause may be interrupted by a weak or strong interrupt.

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕DL DL
</div>
