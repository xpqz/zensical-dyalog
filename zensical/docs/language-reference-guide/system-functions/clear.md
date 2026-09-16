---
search:
  boost: 2
---

# Clear Workspace `⎕CLEAR`

```apl
⎕CLEAR
```

A clear workspace is activated, having the name `CLEAR WS`.  The active workspace is lost.  All system variables assume their default values.  The maximum size of workspace is available.

Apart from .NET objects, the contents of the session namespace `⎕SE` are not affected. .NET objects in `⎕SE` are disconnected from .NET because `⎕CLEAR` closes the current .NET AppDomain.

## Example
```apl

      ⎕CLEAR
      ⎕WSID
CLEAR WS
```

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕CLEAR CLEAR
</div>
