---
search:
  boost: 2
---

# Native File Erase `{R}←X ⎕NERASE Y`

```apl
{R}←X ⎕NERASE Y
```
[Key to notation](../key-to-notation.md)

This function erases (deletes) a tied native file.  `Y` is a negative integer tie number associated with a tied native file.  `X` is a simple character vector or scalar containing the name of the same file and must be **identical** to the name used when it was opened by `⎕NCREATE` or `⎕NTIE`.

The [shy](../../programming-reference-guide/introduction/results.md#shy-results) result of `⎕NERASE` is the tie number that the erased file had.

## Example
```apl
      file ⎕NERASE file ⎕NTIE 0
```

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕NERASE NERASE
</div>
