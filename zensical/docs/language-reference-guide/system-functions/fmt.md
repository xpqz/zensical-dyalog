---
search:
  exclude: true
---

# Format `⎕FMT`

```apl
⎕FMT
```

## Monadic `⎕FMT` means

[Display Form](format-monadic.md)
```apl
      ⎕FMT 2 4⍴⍳8
1 2 3 4
5 6 7 8

```

## Dyadic `⎕FMT` means

[Format](format-dyadic.md)
```apl
     'I3,F5.2' ⎕FMT 2 4⍴⍳8
  1 2.00  3 4.00
  5 6.00  7 8.00
```
