---
search:
  boost: 2
---

# Response Time Limit `⎕RTL`

```apl
⎕RTL
```

A non-zero value in `⎕RTL` places a time limit, in seconds, for input requested via `⍞`, `⎕ARBIN`, and `⎕SR`.  `⎕RTL` may be assigned any integer in the range 0 to 32767.  The value in a clear workspace is 0. `⎕RTL` has Namespace scope.

## Example
```apl
      ⎕RTL←5 ⋄ ⍞←'FUEL QUANTITY?' ⋄ R←⍞
FUEL QUANTITY?
TIMEOUT
      ⎕RTL←5 ⋄ ⍞←'FUEL QUANTITY?' ⋄ R←⍞
```

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕RTL RTL
</div>
