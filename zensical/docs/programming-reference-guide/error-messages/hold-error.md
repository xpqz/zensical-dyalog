

# HOLD ERROR

```apl
12
```

This report is given when an attempt is made to save a workspace using the system function `⎕SAVE` if any external arrays or component files are currently held (as a result of a prior use of the system function `⎕FHOLD`).

## Example
```apl
      ∇HOLD∆SAVE
[1]    ⎕FHOLD 1
[2]    ⎕SAVE 'TEST'
      ∇
 
      'FILE' ⎕FSTIE 1
 
      HOLD∆SAVE
HOLD ERROR
HOLD∆SAVE[2] ⎕SAVE'TEST'
             ^
```
