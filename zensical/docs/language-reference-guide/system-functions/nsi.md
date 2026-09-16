---
search:
  boost: 2
---

# Namespace Indicator

```apl
R←⎕NSI
```
[Key to notation](../key-to-notation.md)

`R` is a nested vector of character vectors containing the names of the spaces from which functions in the state indicator were called (`⍴⎕NSI``←→⍴⎕RSI``←→⍴⎕SI`).

`⎕RSI` and `⎕NSI` are identical except that `⎕RSI` returns refs to the spaces whereas `⎕NSI` returns their names. Put another way:  `⎕NSI←→⍕¨⎕RSI``.`

`⎕NSI` contains the names of spaces from which functions were called not those in which they are currently running.

## Example
```apl
      )OBJECTS
xx      yy
 
      ⎕VR 'yy.foo'
     ∇ r←foo
[1]    r←⎕SE.goo
     ∇                          
      ⎕VR'⎕SE.goo'
     ∇ r←goo
[1]    r←⎕SI,[1.5]⎕NSI
     ∇
 
      )CS xx
#.xx
      calling←#.yy.foo
      ]Display calling
┌→─────────────┐
↓ ┌→──┐ ┌→───┐ │
│ │goo│ │#.yy│ │
│ └───┘ └────┘ │
│ ┌→──┐ ┌→───┐ │
│ │foo│ │#.xx│ │
│ └───┘ └────┘ │
└∊─────────────┘
```

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕NSI NSI
</div>
