---
search:
  boost: 2
---

# Account Name

```apl
R←⎕AN
```
[Key to notation](../key-to-notation.md)

This is a simple character vector containing the user (login) name. Under UNIX and Linux this is the real user name, whereas `⎕AI` returns the effective user id.

## Example
```apl
      ⎕AN
Pete
 
      ⍴⎕AN
4
```

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕AN AN
</div>
