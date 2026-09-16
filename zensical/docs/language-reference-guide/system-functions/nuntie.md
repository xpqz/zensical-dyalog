---
search:
  boost: 2
---

# Native File Untie

```apl
{R}←⎕NUNTIE Y
```
[Key to notation](../key-to-notation.md)

This closes one or more native files.  `Y` is a scalar or vector of negative integer tie numbers.  The files associated with elements of `Y` are closed.  Native file untie with a zero length argument (`⎕NUNTIE ⍬`) flushes all file buffers to disk - see [File Untie](funtie.md) for more explanation.

The [shy](../../programming-reference-guide/introduction/results.md#shy-results) result of `⎕NUNTIE` is a vector of tie numbers of the files **actually untied**.

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕NUNTIE NUNTIE
</div>
