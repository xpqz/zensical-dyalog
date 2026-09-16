

# VALUE ERROR

```apl
6
```

This report is given when either:

- There is no active definition for a name encountered in an expression.
- A function does not return a result (see [Results](../introduction/results.md#no-result)) in a context where a result is required.

## Examples
```apl
     X
VALUE ERROR
     X
     ^
 
     ∇ HELLO
[1]    'HI THERE'
[2]  ∇
 
     2+HELLO
HI THERE
VALUE ERROR
     2+HELLO
      ^
```
