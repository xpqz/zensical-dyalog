---
search:
  boost: 2
---


# Set Dyalog Pixel Type

```apl
R←2035⌶Y
```
[Key to notation](../../key-to-notation.md)

!!! info "Dyalog on Microsoft Windows"
    This function is available only under Microsoft Windows.

Determines how Coord `'Pixel'` is interpreted. This is determined initially by the value of the DYALOG_PIXEL_TYPE parameter and, when altered by this function,  applies to all subsequent GUI operations.

`Y` is a character vector that is either `'ScaledPixel'` or `'RealPixel'`. Any other value will cause a `DOMAIN ERROR`.

The result `R` is the previous value.

## Example
```apl
      2035⌶'ScaledPixel'
RealPixel
      2035⌶'RealPixel'
ScaledPixel

      2035⌶'realpixel'
DOMAIN ERROR
      2035⌶'realpixel'
     ∧

```

<!-- Hidden search keywords -->
<div style="display: none;">
  2035⌶
</div>
