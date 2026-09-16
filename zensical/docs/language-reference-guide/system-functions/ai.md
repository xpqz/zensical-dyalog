---
search:
  boost: 2
---

# Account Information

```apl
R←⎕AI
```
[Key to notation](../key-to-notation.md)

This is a simple integer vector, whose four elements are:

|--------|-------------------------------------------------|
|`⎕AI[1]`|user identification.                             |
|`⎕AI[2]`|compute time for the APL session in milliseconds.|
|`⎕AI[3]`|connect time for the APL session in milliseconds.|
|`⎕AI[4]`|keying time for the APL session in milliseconds. |

Elements beyond 4 are not defined but reserved.

## Example
```apl
     ⎕AI
52 7396 2924216 2814831
```

!!! info "Dyalog on Unix"
    Under UNIX, `⎕AI[1]` is the effective UID of the account whereas [`⎕AN`](./an.md) returns the real name.

!!! info "Dyalog on Microsoft Windows"
    Under Microsoft Windows, `⎕AI[1]` is the aplnid (network ID from configuration dialog box).

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕AI AI
</div>
