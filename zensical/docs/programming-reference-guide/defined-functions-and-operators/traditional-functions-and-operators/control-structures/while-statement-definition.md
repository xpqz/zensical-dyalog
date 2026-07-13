---
search:
  exclude: true
---

# <span class="name">:While Statement</span> {: .heading}

```
 
       |
       :While bexp
       |
       .-------.
       |       |
       |       andor
       |       |
       |<------'
       |
       code
       |
       .---------------.
       |               |
       :End[While]     :Until bexp
       |               |
       |               .-------.
       |               |       |
       |               |       andor
       |               |       |
       |               |<------'
       |               |
       |<--------------'
       |
```
