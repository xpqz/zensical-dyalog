---
search:
  boost: 2
---

# Current Thread Name

```apl
⎕TNAME
```

The system variable `⎕TNAME` reports and sets the name of the current APL thread. This name is used to identify the thread in the Tracer.

The default value of `⎕TNAME` is an empty character vector. `⎕TNAME` has workspace scope.

You may set `⎕TNAME` to any valid character vector, but it is recommended that control characters (such as `⎕AV[⎕IO]` ) be avoided.

## Example
```apl
      ⎕TNAME←'Dylan'
      ⎕TNAME
Dylan
```

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕TNAME TNAME
</div>
