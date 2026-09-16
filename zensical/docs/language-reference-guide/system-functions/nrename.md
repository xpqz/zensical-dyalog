---
search:
  boost: 2
---

# Native File Rename `{R}←X ⎕NRENAME Y`

```apl
{R}←X ⎕NRENAME Y
```
[Key to notation](../key-to-notation.md)

`⎕NRENAME` is used to rename a native file.

`Y` is a negative integer tie number associated with a tied native file.  `X` is a simple character vector or scalar containing a valid (and unused) file name.

The [shy](../../programming-reference-guide/introduction/results.md#shy-results) result of `⎕NRENAME` is the tie number of the renamed file.

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕NRENAME NRENAME
</div>
