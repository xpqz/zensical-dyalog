---
search:
  boost: 2
---


# Identify .NET Type

```apl
R←2017⌶Y
```
[Key to notation](../../key-to-notation.md)

!!! Info "Information"
    This function is available only in the .NET Framework interface.

Returns the .NET Type of a named .NET class that is loaded in the current AppDomain. System.Type.GetType requires the fully qualified name, that is, prefixed by the assembly name, whereas (`2017⌶`) does not.

`Y` is a character string containing the name of a .NET object. Unless the fully qualified name is given, the namespaces in the current AppDomain are searched in the order they are specified by  `⎕USING` or `:Using`.

If the object is identified in the current AppDomain, the result `R` is its Type. If not, the function generates `DOMAIN ERROR`.

## Example
```apl
      ⎕USING←'System'
      2017⌶'DateTime'
System.DateTime
```

<!-- Hidden search keywords -->
<div style="display: none;">
  2017⌶
</div>
