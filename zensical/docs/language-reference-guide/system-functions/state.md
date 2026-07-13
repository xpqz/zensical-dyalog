---
search:
  boost: 2
---
<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕STATE STATE
</div>






# <span class="name">State of Object</span> <span class="command">R←⎕STATE Y</span> {: .heading}



`Y` must be a simple character scalar or vector which is taken to be the name of an APL object or a system variable. The result returned is a nested vector of 4 elements as described below. `⎕STATE` supplies information about shadowed or localised objects that is otherwise unobtainable.


|-----|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
|`1⊃R`|Boolean vector, element set to 1 if and only if this level shadows `Y` . Note: `(⍴1⊃R)=⍴⎕LC`                                                                 |
|`2⊃R`|Numeric vector giving the stack state of this name as it entered this level. Note: `(⍴2⊃R)=⍴⎕LC` 0=not on stack 1=suspended 2=pendent (may also be suspended)|
|`3⊃R`|Numeric vector giving the name classification of `Y` as it entered this level. Note: `(⍴3⊃R)=+/1⊃R`                                                          |
|`4⊃R`|Vector giving the contents of `Y` before it was shadowed at this level. Note: `(⍴4⊃R)=+/0≠3⊃R`                                                               |


<h2 class="example">Example</h2>
```apl

      ⎕FMT∘⎕OR¨'FN1' 'FN2' 'FN3'
    ∇ FN1;A;B;C      ∇ FN2;A;C               ∇ FN3;A
[1]   A←1        [1]   A←'HELLO'         [1]   A←100
[2]   B←2        [2]   B←'EVERYONE'      [2]   ∘
[3]   C←3        [3]   C←'HOW ARE YOU?'      ∇
[4]   FN2        [4]  FN3
    ∇                ∇

      )SI
#.FN3[2]*
#.FN2[4]
#.FN1[4]

      ⎕STATE 'A'
 1 1 1  0 0 0  2 2 0   HELLO  1

       ⎕FMT∘⎕OR¨'foo' 'goo'
      ∇ foo;⎕IO       ∇ goo;⎕IO     
 [1]    ⎕IO←0    [1]    ⎕IO←1       
 [2]    goo      [2]    ⎕STATE'⎕IO' 
      ∇               ∇             

       foo
 1 1  0 0  ¯1 ¯1  0 1 

```


