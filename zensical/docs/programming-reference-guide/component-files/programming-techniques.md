# <span class="name">Programming Techniques</span> {: .heading}

## Controlling Multi-User Access

Obviously, Dyalog APL contains mechanisms that prevent data getting mixed up if two users update a file at the same time. However, it is the programmer's responsibility to control the logic of multi-user updates.

For example, suppose two people are updating our database at the same time. The first checks to see if there is an entry for `'Geoff'`, sees that there isn't so adds a new record. Meanwhile, the second user is checking for the same thing, and so also adds a record for `'Geoff'`. Each user would be running code similar to that shown below:
```apl
    ∇  UPDATE;DATA;NAMES
[1]    ⍝ Using the component file
[2]    'PERSONNEL' ⎕FSTIE 1
[3]    NAMES←⊃∘⎕FREAD ¨ 1,¨⍳¯1+2⊃⎕FSIZE 1
[4]    →END×⍳(⊂'Geoff')∊NAMES
[5]    ('Geoff' 41 'Hounslow')⎕FAPPEND 1
[6]    END:⎕FUNTIE 1
    ∇
```

The system function `⎕FHOLD` provides the means for the user to temporarily prevent other co-operating users from accessing one or more files. This is necessary to allow a single logical update, perhaps involving more than one record or more than one file, to be completed without interference from another user.

The code above is replaced by that below:
```apl
    ∇ UPDATE;DATA;NAMES
[1] ⍝ Using the component file
[2]  'PERSONNEL' ⎕FSTIE 1
[3]  ⎕FHOLD 1
[4]  NAMES←⊃∘⎕FREAD ¨ 1,¨⍳¯1+2⊃⎕FSIZE 1
[5]  →END×⍳(⊂'Geoff')∊NAMES
[6]  ('Geoff' 41 'Hounslow')⎕FAPPEND 1
[7] END:⎕FUNTIE 1 ⋄ ⎕FHOLD ⍳0
    ∇
```

Successive `⎕FHOLD`s on a file executed by different users are queued by Dyalog APL; once the first `⎕FHOLD` is released, the next on the queue holds the file. `⎕FHOLD`s are released by return to immediate execution, by `⎕FHOLD ⍬`, or by erasing the external variable.

It is easy to misunderstand the effect of `⎕FHOLD`. It is NOT a file locking mechanism that prevents other users from accessing the file. It only works if the tasks that wish to access the file co-operate by queuing for access by issuing `⎕FHOLD`s. It would be very inefficient to issue a `⎕FHOLD` on a file then allow the user to interactively edit the data with the hold in operation. What happens if he goes to lunch? Any other user who wants to access the file and cooperates by issuing a `⎕FHOLD` would have to wait in the queue for 3 hours until the first user returns, finishes his update and his `⎕FHOLD` is released. It is usually more efficient (as well as more friendly) to issue `⎕FHOLD`s around a small piece of critical code.

Suppose we had a control file associated with our personnel data base. This control file could be an external variable, or a component file. In both cases, the concept is the same; only the commands needed to access the file are different. In this example, we will use a component file:
```apl
      'CONTROL'⎕FCREATE 1    ⍝ Create control file
      (1 3⍴0 ¯1 0) ⎕FSTAC 1  ⍝ Allow everyone access
      ⍬ ⎕FAPPEND 1           ⍝ Set component 1 to empty
      ⎕FUNTIE 1              ⍝ And untie it
```

Now we'll allow our man that likes long lunch breaks to edit the file, but will control the hold in a more efficient way:
```apl
     ∇  EDIT;CMP;CV
[1]   ⍝ Share-tie the control file
[2]    'CONTROL' ⎕FSTIE 1
[3]   ⍝ Share-tie the data file
[4]    'PERSONNEL' ⎕FSTIE 2
[5]   ⍝ Find out which component the user wants to edit
[6]    ASK:CMP←ASK∆WHICH∆RECORD
[7]   ⍝ Hold the control file
[8]    ⎕FHOLD 1
[9]   ⍝ Read the control vector
[10]   CV←⎕FREAD 1 1
[11]  ⍝ Make control vector as big as the data file
[12]   CV←(¯1+2⊃⎕FSIZE 2)↑CV
[13]  ⍝ Look at flag for this component
[14]   →(FREE,INUSE)[1+CMP⊃CV]
[15]  ⍝ In use - tell user and release hold
[16]  INUSE:'Record in use' ⋄ ⎕FHOLD ⍬ ⋄ →ASK
[17]  ⍝ Ok to use - flag in-use and release hold
[18]  FREE:CV[CMP]←1 ⋄ CV ⎕FREPLACE 1 1⋄ ⎕FHOLD ⍬
[19]  ⍝ Let user edit the record
[20]   EDIT∆RECORD RECORD
[21]  ⍝ When he's finished, clear the control vector
[22]   ⎕FHOLD 1
[23]  CV←⎕FREAD 1 1 ⋄CV[CMP]←0 ⋄ CV ⎕FREPLACE 1 1
[26]   ⎕FHOLD ⍬
[27]  ⍝ And repeat
[28]   →ASK
     ∇
```

Component 1 of our CONTROL file acts as a control vector. Its length is set equal to the number of components in the PERSONNEL file, and an element is set to 1 if a user wishes to access the corresponding data component. Only the control file is ever subject to a `⎕FHOLD`, and then only for a split-second, with no user inter-action being performed whilst the hold is active.

When the first user runs the function, the relevant entry in the control vector will be set to 1. If a second user accesses the database at the same time, he will have to wait briefly whilst the control vector is updated. If he wants the same component as the first user, he will be told that it is in use, and will be given the opportunity to edit something else.

This simple mechanism allows us to lock the components of our file, rather the than entire file. You can set up more informative control vectors than the one above; for example, you could easily put the user name into the control vector and this would enable you to tell the next user who is editing the component he is interested in.
