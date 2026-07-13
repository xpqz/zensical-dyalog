---
search:
  exclude: true
---





# <span class="name">Trace Controls</span> <span class="command">⎕TRACE</span> {: .heading}


## Dyadic `⎕TRACE` means


[Set Trace Controls](set-trace.md)
```apl
      +(0,⍳10) ⎕TRACE 'foo'
0 1 2 3 4 5
```

## Monadic `⎕TRACE` means


[Query Trace Controls](query-trace.md)
```apl
      ⎕TRACE 'foo'
0 1 2 3 4 5
```
