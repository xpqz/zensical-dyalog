---
search:
  boost: 2
---

# File Read Access

```apl
R←⎕FRDAC Y
```
[Key to notation](../key-to-notation.md)

## Access code 4096

`Y` must be a simple integer scalar or 1 or 2 element vector containing the file tie number followed by an optional passnumber. If the passnumber is omitted it is assumed to be zero. The result is the access matrix for the designated file.

For details see [File Access Control](../../programming-reference-guide/component-files/component-files.md#file-access-control).

## Examples
```apl
      ⎕FRDAC 1
28 2105 16385
 0 2073 16385
31   ¯1     0
```

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕FRDAC FRDAC
</div>
