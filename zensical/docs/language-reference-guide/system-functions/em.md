---
search:
  boost: 2
---

# Event Message

```apl
R←⎕EM Y
```
[Key to notation](../key-to-notation.md)

`Y` must be a simple non-negative integer scalar or vector of event codes.  If `Y` is a scalar, `R` is a simple character vector containing the associated event message.  If `Y` is a vector, `R` is a vector of character vectors containing the corresponding event messages.

If `Y` refers to an undefined error code "`n`", the event message returned is "`ERROR NUMBER n`".

See [APL Error Messages](../../programming-reference-guide/error-messages/apl-errors.md).

## Example
```apl
      ⎕EM 11
DOMAIN ERROR
```

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕EM EM
</div>
