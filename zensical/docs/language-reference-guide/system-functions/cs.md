---
search:
  boost: 2
---
<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕CS CS
</div>






# <span class="name">Change Space</span> <span class="command">\{R\}←\{X\}⎕CS Y</span> {: .heading}



`Y` must be namespace reference (ref) or a simple character scalar or vector identifying the name of a namespace.


If specified, `X` is a simple character scalar, vector, matrix or a nested vector of character vectors identifying zero or more workspace objects to be *exported* into the namespace `Y`.


The identifiers in `X` and `Y` may be simple names or compound names separated by `'.'` and including the names of the special namespaces `'⎕SE'`, `'#'`, and `'##'`.


The result `R` is the full name (starting `#.`) of the space in which the function or operator was executing prior to the `⎕CS`.



`⎕CS` changes the space in which the current function or operator is running to the namespace `Y` and returns the original space, in which the function was previously running, as a shy result.  **After the** `⎕CS`, references to *global* names (with the exception of those specified in `X`) are taken to be references to *global* names in `Y`.  References to *local* names (that is, those local to the current function or operator) are, with the exception of those with name class `9`, unaffected. Therefore any names in the new space that match local names in the containing defined function will be invisible. Local names with name class `9` are also not visible.


When the function or operator terminates, the calling function resumes execution in its original space.


The names listed in `X` are temporarily *exported* to the namespace `Y`.  If objects with the same name exist in `Y`, these objects are effectively *shadowed* and are inaccessible. Note that Dyadic `⎕CS` may be used only if there is a traditional function in the state indicator (stack). Otherwise there would be no way to retract the export. In this case (for example in a clear workspace) `DOMAIN ERROR` is reported.


Note that calling `⎕CS` with an empty argument `Y` obtains the namespace in which a function is currently executing.


<h2 class="example">Example</h2>


This simple example illustrates how `⎕CS` may be used to avoid typing long pathnames when building a tree of GUI objects.  Note that the objects `NEW` and `OPEN` are created as children of the `FILE` menu as a result of using `⎕CS` to change into the `F.MB.FILE` namespace.
```apl
     ∇ MAKE_FORM;F;OLD
[1]    'F'⎕WC'Form'
[2]    'F.MB'⎕WC'MenuBar'
[3]    'F.MB.FILE'⎕WC'Menu' '&File'
[4]
[5]    OLD←⎕CS'F.MB.FILE'
[6]    'NEW'⎕WC'MenuItem' '&New'
[7]    'OPEN'⎕WC'MenuItem' '&Open'
[8]    ⎕CS OLD
[9]
[10]   'F.MB.EDIT'⎕WC'Menu' '&Edit'
[11]
[12]   OLD←⎕CS'F.MB.EDIT'
[13]   'UNDO'⎕WC'MenuItem' '&Undo'
[14]   'REDO'⎕WC'MenuItem' '&Redo'
[15]   ⎕CS OLD
[16]   ...
     ∇
```


<h2 class="example">Example</h2>


Suppose a form `F1` contains buttons `B1` and `B2`. Each button maintains a count of the number of times it has been pressed, and the form maintains a count of the total number of button presses. The single callback function `PRESS` and its subfunction `FMT` can reside in the form itself
```apl
      )CS F1
#.F1
      ⍝ Note that both instances reference
      ⍝ the same callback function
      'B1'⎕WS'Event' 'Select' 'PRESS'
      'B2'⎕WS'Event' 'Select' 'PRESS'
 
      ⍝ Initialise total and instance counts.
      TOTAL ← B1.COUNT ← B2.COUNT ← 0
```
```apl

 
    ∇ PRESS MSG
[1]   'FMT' 'TOTAL'⎕CS⊃MSG ⍝     Switch to instance space
[2]   (TOTAL COUNT)+←1   ⍝    Incr total & instance count
[3]   ⎕WS'Caption'(COUNT FMT TOTAL)⍝ Set instance caption
    ∇
```
```apl

 
    ∇ CAPT←INST FMT TOTL      ⍝ Format button caption.
[1]   CAPT←(⍕INST),'/',⍕TOTL  ⍝ For example, 40/100.
    ∇
```


<h2 class="example">Example</h2>


This example uses `⎕CS` to explore a namespace tree and display the structure.  Note that it must export its own name (tree) each time it changes space, because the name tree is global.
```apl
      ∇ tabs tree space;subs     ⍝ Display namespace tree
[1]    tabs,space
[2]    'tree'⎕CS space
[3]    →(⍴subs←↓⎕NL 9)↓0
[4]    (tabs,'.   ')∘tree¨subs
     ∇ 
 
      )NS x.y
#.x.y
      )NS z
#.z
      ''tree '#'
#
.   x
.   .   y
.   z
```

!!! note
    `⎕CS` is not permitted in a dfn or dop. If used therein it will cause a `NONCE ERROR`.


