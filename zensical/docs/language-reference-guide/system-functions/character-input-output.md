---
search:
  boost: 2
---





# <span class="name">Character Input/Output</span> <span class="command">⍞</span> {: .heading}



`⍞` is a variable which communicates between the user's terminal and APL.  Its behaviour depends on whether it is being assigned or referenced.


When `⍞` is assigned with a vector or a scalar, the array is displayed without the normal ending new-line character.  Successive assignments of vectors or scalars to `⍞` without any intervening input or output cause the arrays to be displayed on the same output line.


<h2 class="example">Example</h2>
```apl
      ⍞←'2+2' ⋄ ⍞←'=' ⋄ ⍞←4
2+2=4
```


Output through `⍞` is independent of the print width in `⎕PW`.  The way in which lines exceeding the print width of the terminal are treated is dependent on the characteristics of the terminal.  Numeric output is formatted in the same manner as direct output (see [Programmer's Guide: "Display of Arrays"](../../../programming-reference-guide/introduction/arrays/display-of-arrays)).


When `⍞` is assigned with a higher-rank array, the output is displayed in the same manner as for direct output except that the print width `⎕PW` is ignored.


When `⍞` is referenced, terminal input is expected without any specific prompt, and the response is returned as a character vector.


If the `⍞` request was preceded by one or more assignments to `⍞` without any intervening input or output, the last (or only) line of the output characters are returned as part of the response.

<h2 class="example">Example</h2>
```apl
      mat←↑⌽⍞⍞⍞⍞⍞
```

<h2 class="example">Examples</h2>
```apl
      ⍞←'OPTION : ' ⋄ R←⍞
OPTION : INPUT
 
      R
OPTION : INPUT
 
      ⍴R
14
```


The output of simple arrays of rank greater than 1 through `⍞` includes a new-line character at the end of each line.  Input through `⍞` includes the preceding output through `⍞` since the last new-line character.


A soft interrupt causes an `INPUT INTERRUPT` error if entered while `⍞` is awaiting input, and execution is then suspended (unless the interrupt is trapped):

```apl
      R←⍞
```


(Interrupt)
```apl
INPUT INTERRUPT
```




A time limit is imposed on input through `⍞` if `⎕RTL` is set to a non-zero value:
```apl
      ⎕RTL←5 ⋄ ⍞←'PASSWORD ? ' ⋄ R←⍞
PASSWORD ?
TIMEOUT
      ⎕RTL←5 ⋄ ⍞←'PASSWORD : ' ⋄ R←⍞
                                   ^
```


The `TIMEOUT` interrupt is a trappable event.



