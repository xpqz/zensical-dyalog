---
search:
  exclude: true
---

# <span class="name">:Select Statement</span> {: .heading}

```
 
       |
       :Select aexp
       |
       |<----------------------------------------------.
       |                                               |
       .-------.-------.---------------.               |
       |       |       |               |               |
       |       :Else   :Case aexp      :CaseList aexp  |
       |       |       |               |               |
       |       |       |<--------------'               |
       |       |       |                               |
       |       code    code                            |
       |       |       |                               |
       |<------'       `-------------------------------'
       |
       :End[Select]
```
