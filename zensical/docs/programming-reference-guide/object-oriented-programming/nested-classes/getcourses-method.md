---
search:
  exclude: true
---

# <span class="name">GetCourses Method</span> {: .heading}

```apl

    ∇ R←GetCourses;COURSECODES;COURSES;INDEX
      :Access Public
      COURSECODES COURSES INDEX←⎕FREAD GOLFID 1
      R←{⎕NEW GolfCourse ⍵}¨↓⍉↑COURSECODES COURSES
    ∇
```
