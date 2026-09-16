---
search:
  boost: 2
---

# Native File Names `R←⎕NNAMES`

```apl
R←⎕NNAMES
```
[Key to notation](../key-to-notation.md)

This niladic function reports the names of all currently open native files.  `R` is a character matrix.  Each row contains the name of a tied native file padded if necessary with blanks.  The names are **identical** to those that were given when opening the files with `⎕NCREATE` or `⎕NTIE`. The rows of the result are in the order in which the files were tied.

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕NNAMES NNAMES
</div>
