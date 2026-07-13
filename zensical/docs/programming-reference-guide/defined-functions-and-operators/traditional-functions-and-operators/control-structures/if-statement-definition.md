---
search:
  exclude: true
---

# <span class="name">:If Statement</span> {: .heading}

```
 
       |
       :If bexp
       |
       .-------.
       |       |
       |       andor
       |       |
       |<------'
       |
       code
       |
       |<------------------------------.
       |                               |
       .-------.-------.               |
       |       |       |               |
       |       :Else   :ElseIf bexp    |
       |       |       |               |
       |       |       .-------.       |
       |       |       |       |       |
       |       |       |       andor   |
       |       |       |       |       |
       |       |       |<------'       |
       |       |       |               |
       |       code    code            |
       |       |       |               |
       |<------'       `---------------'
       |
       :End[If]
       |
```
