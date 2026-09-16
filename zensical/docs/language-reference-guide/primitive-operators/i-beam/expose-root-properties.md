---
search:
  boost: 2
---


# Expose Root Properties `R←2401⌶Y`

```apl
R←2401⌶Y
```
[Key to notation](../../key-to-notation.md)

This function is used to expose or hide Root Properties, Event and Methods.

If `Y` is 1, Root Properties, Events and Methods are exposed.

If `Y` is 0, no further Root Properties, Events or Methods are exposed; however any that have already been exposed will remain so.

This functionality is available in Microsoft Windows versions by selecting or unselecting *Expose Root Properties* in the *Options* menu in the Session. Deselecting this menu item only affects future references to Root Properties, Events, or Methods.

This function is the only mechanism available under non-Windows versions of Dyalog APL; the state of this setting is saved in the workspace, and therefore cannot be controlled by an environment variable.

## Example
```apl

      #.GetEnvironment'MAXWS'
VALUE ERROR
      #.GetEnvironment'MAXWS'
     ∧
      
      2401⌶1
0
      #.GetEnvironment'MAXWS'
64M
      
      2401⌶0
1
      #.GetEnvironment'MAXWS'
64M
      #.GetCommandLine
VALUE ERROR
      #.GetCommandLine
     ∧

```

<!-- Hidden search keywords -->
<div style="display: none;">
  2401⌶
</div>
