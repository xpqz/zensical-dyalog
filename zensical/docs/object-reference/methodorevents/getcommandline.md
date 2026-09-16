# GetCommandLine

Method 145

The GetCommandLine method returns the command line that was used to start the current Dyalog APL session or application.

The GetCommandLine method is niladic.

The result is a character vector.

## Examples
```apl
      GetCommandLine
"C:\Program Files\Dyalog\Dyalog APL-64 13.2 Unicode\dyalog.exe"
```
```apl
      ⎕←2 ⎕NQ '.' 'GetCommandLine'
"C:\Program Files\Dyalog\Dyalog APL-64 13.2 Unicode\dyalog.exe"
```

!!! note "Legacy"
    GetCommandLine only works on Microsoft Windows; its use is deprecated in favour of [GetCommandLineArgs](getcommandlineargs.md), which works on all supported platforms.

## Application

Objects: [Root](../objects/root.md)
