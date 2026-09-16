---
search:
  exclude: true
---

# Unix Shell `⎕SH`

```apl
⎕SH
```

## Monadic `⎕SH` means

[Execute Unix Command](execute-unix-command.md)
```apl
       ⎕SH'ls'
FILES WS temp
```

## Dyadic `⎕SH` means

[Start Unix Auxiliary Processor](start-unix-auxiliary-processor.md)
```apl
      )CLEAR
clear ws
      'xutils' ⎕SH 'xutils'
      )FNS
avx     box     dbr     getenv  hex     ltom    ltov    mtol    ss      vtol

```
