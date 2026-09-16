---
search:
  boost: 2
---


# Remove Data Binding `R←2014⌶Y`

```apl
R←2014⌶Y
```
[Key to notation](../../key-to-notation.md)

!!! Info "Information"
    This function is available only in the .NET Framework interface.

This function disassociates a data-bound variable from its data binding source.

`Y` is any array.

If `Y` or an element of `Y` is a character vector that contains the name of a data-bound variable, that variable is dissociated from its data binding source.

The result `R` is always 1.

## Example
```apl

      2014⌶'txtSource'
1    
```

<!-- Hidden search keywords -->
<div style="display: none;">
  2014⌶
</div>
