

# WS FULL `1`

```apl
1
```

This report is given when there is insufficient workspace in which to perform an operation.  Workspace available is identified by the system constant `⎕WA`.

The maximum workspace size allowed is defined by the environment variable `MAXWS`. See **maxws parameter** for details.

## Example
```apl

      ⎕WA⍴1.2
WS FULL
      ⎕WA⍴1.2
      ^
```
