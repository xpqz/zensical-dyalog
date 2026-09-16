---
search:
  boost: 2
---


# Flush Session Caption

```apl
R←2022⌶Y
```
[Key to notation](../../key-to-notation.md)

!!! info "Dyalog on Microsoft Windows"
    This function is available only under Microsoft Windows.

Under Windows, the Session Caption displays information such as the name of the current workspace. The contents of the Caption can be modified: see *Window Captions* in the *Installation and Configuration Guide* for more details.

However, the Caption is updated only at the six-space prompt; calling `⎕LOAD` for example from within a function will not result in the Caption being updated at the end of the `⎕LOAD`.

This _I-beam_ causes the Session Caption to be updated (flushed) when called. It does not alter the contents of the Caption.

## Example
```apl

      2022⌶0    
```

<!-- Hidden search keywords -->
<div style="display: none;">
  2022⌶
</div>
