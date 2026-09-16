

# FORMAT ERROR

```apl
7
```

This report is given when the format specification in the left argument of system function `⎕FMT` is ill-formed.

## Example
```apl
      'A1,1X,I5'⎕FMT CODE NUMBER
FORMAT ERROR
      'A1,1X,I5'⎕FMT CODE NUMBER
       ^
```

(The correct specification should be `'A1,X1,I5'` .)
