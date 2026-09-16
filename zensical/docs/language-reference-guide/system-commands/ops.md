

# List Global Defined Operators

```apl
)OPS {nm}
```

This command displays the names of global defined operators in the active workspace or current namespace.  Names are displayed in [`⎕AV`](../system-functions/av.md) collation order.  If a name is included after the command, only those names starting at or after the given name in collation order are displayed.

## Examples
```apl
      )OPS
AND DOIF DUAL ELSE POWER
 
      )OPS E
ELSE POWER
```
