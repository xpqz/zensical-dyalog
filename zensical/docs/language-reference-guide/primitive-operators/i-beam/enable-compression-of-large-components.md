---
search:
  boost: 2
---


# Enable Compression of Large Components

```apl
{R}←3012⌶Y
```
[Key to notation](../../key-to-notation.md)

Specifies whether large components (>2GB) may be compressed.

`Y` is an integer defined as follows:

| Value | Description |
|-------|---------------|
| 0     | Large components will not be compressed. |
| 1     | Large components will be compressed if Z property is 1 (see [File Properties](../../system-functions/fprops.md)), but versions of Dyalog prior to v19.0 will not be able to read them.|

The [shy](../../../programming-reference-guide/introduction/results.md#shy-results) result `R` is the previous value of this setting.

<!-- Hidden search keywords -->
<div style="display: none;">
  3012⌶
</div>
