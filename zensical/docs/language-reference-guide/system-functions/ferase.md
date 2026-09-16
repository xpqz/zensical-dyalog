---
search:
  boost: 2
---

# File Erase `{R}←X ⎕FERASE Y`

```apl
{R}←X ⎕FERASE Y
```
[Key to notation](../key-to-notation.md)

## Access code 4

`Y` must be a simple integer scalar or 1 or 2 element vector containing the file tie number followed by an optional passnumber.  If the passnumber is omitted it is assumed to be zero.  `X` must be a character scalar or vector containing the name of the file associated with the tie number `Y`.  This name must be identical with the name used to tie the file (except that the directory delimiters `/` and `\` are treated as being the same) and the file must be exclusively tied.  The file named in `X` is erased and untied.

The [shy](../../programming-reference-guide/introduction/results.md#shy-results) result of `⎕FERASE` is the tie number of the erased file.

## Examples
```apl

      'SALES'⎕FERASE 'SALES' ⎕FTIE 0

      './temp' ⎕FCREATE 1
      'temp' ⎕FERASE 1
FILE NAME ERROR
      'temp'⎕FERASE 1
      
      ⎕←'.\temp'⎕FERASE 1 ⍝ Works with / or \
1
```

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕FERASE FERASE
</div>
