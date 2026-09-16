

# List Workspace Library

```apl
)LIB {dir}
```

This command lists the names of Dyalog workspaces contained in the given directory.

## Example
```apl
      )LIB WS
MYWORK TEMP
```

If a directory is not given, the workspaces on the user's APL workspace path (**WSPATH**) are listed.  In this case, the listing is divided into sections identifying the directories concerned.  The current directory is identified as "`.`".

## Example
```apl
      )LIB
.
        PDTEMP  WORK   GRAPHICS
```
```apl
c:\Dyalog\ws
        display groups
```
