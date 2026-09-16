---
search:
  boost: 2
---

# Thread Numbers `R←⎕TNUMS`

```apl
R←⎕TNUMS
```
[Key to notation](../key-to-notation.md)

`⎕TNUMS` reports the numbers of all current threads.

`R` is a simple integer vector of the base thread and all its living descendants.

## Example
```apl
      ⎕TNUMS
0 2 4 5 6 3 7 8 9
```

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕TNUMS TNUMS
</div>
