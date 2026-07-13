# <span class="name">Recursion</span> {: .heading}

A recursive dfn can refer to itself using its name explicitly, but because we allow unnamed functions, we also need a special symbol for implicit self-reference: `'∇'`. For example:
```apl
      fact←{          ⍝ Factorial ⍵.
          ⍵≤1: 1      ⍝ Small ⍵, finished,
          ⍵×∇ ⍵-1     ⍝ Otherwise recur.
      }
```

Implicit self-reference using `'∇'` has the further advantage that it incurs less interpretative overhead and is therefore quicker. Tail calls using `'∇'` are particularly efficient.

Recursive dops refer to their derived functions, that is the operator bound with its operand(s) using `∇` or the operator itself using the compound symbol: `∇∇`. The first form of self reference is by far the more frequently used.
```apl
      pow←{           ⍝ Function power.
          ⍺=0:⍵       ⍝ Apply function operand ⍺ times.
          (⍺-1)∇ ⍺⍺ ⍵ ⍝ ⍺⍺ ⍺⍺ ⍺⍺ ... ⍵
      }
```

<h2 class="example">Example</h2>

The following example shows a rather contrived use of the second form of (operator) self reference. The `exp` operator composes its function operand with itself on each recursive call. This gives the effect of an exponential application of the original operand function:
```apl
      exp←{               ⍝ Exponential fn application.
          ⍺=0:⍺⍺ ⍵        ⍝ Apply operand 2*⍺ times.
          (⍺-1)⍺⍺∘⍺⍺ ∇∇ ⍵ ⍝ (⍺⍺∘⍺⍺)∘( ... ) ... ⍵
      }
      succ←{1+⍵}          ⍝ Successor (increment).
      10 succ exp 0
1024
```

<h2 class="example">Example</h2>
```apl
     ∇pow←{ ⍝ Function power.
[1]        ⍺=0:⍵ ⍝ Apply function operand ⍺ times.
[2]        (⍺-1)∇ ⍺⍺ ⍵ ⍝ ⍺⍺ ⍺⍺ ⍺⍺ ... ⍵
[3]    }
     ∇
      4 ⍟ pow 5000
¯0.2720968003

```

## Example: Pythagorean triples

The following sequence shows an example of combining dfns and dops in an attempt to find Pythagorean triples: `(3 4 5)(5 12 13)` ...
```apl
 
      sqrt←{⍵*0.5}              ⍝ Square root.
 
      sqrt 9 16 25
3 4 5
 
      hyp←{sqrt+/⊃⍵*2}          ⍝ Hypoteneuse of triangle.
 
      hyp(3 4)(4 5)(5 12)
5 6.403124237 13
 
      intg←{⍵=⌊⍵}               ⍝ Whole number?
 
      intg 2.5 3 4.5
0 1 0
 
      pyth←{intg hyp ⍵}         ⍝ Pythagorean pair?
 
      pyth(3 4)(4 9)(5 12)
1 0 1
 
      pairs←{,⍳⍵ ⍵}             ⍝ Pairs of numbers 1..⍵.
 
      pairs 3
 1 1  1 2  1 3  2 1  2 2  2 3  3 1  3 2  3 3
 
      filter←{(⍺⍺ ⍵)/⍵}         ⍝ Op: ⍵ filtered by ⍺⍺.
 
      pyth filter pairs 12      ⍝ Pythagorean pairs 1..12
 3 4  4 3  5 12  6 8  8 6  9 12  12 5  12 9
```

So far, so good, but we have some duplicates: `(6 8)` is just double `(3 4)`.
```apl
 
      rpm←{                    ⍝ Relatively prime?
          ⍵=0:⍺=1              ⍝ C.f. Euclid's gcd.
          ⍵ ∇ ⍵|⍺
      }/¨                      ⍝ Note the /¨
 
      rpm(2 4)(3 4)(6 8)(16 27)
0 1 0 1
 
      rpm filter pyth filter pairs 20
 3 4  4 3  5 12  8 15  12 5  15 8
```

We can use an operator to combine the tests:
```apl
      and←{                    ⍝ Lazy parallel 'And'.
          mask←⍺⍺ ⍵            ⍝ Left predicate selects...
          mask\⍵⍵ mask/⍵       ⍝ args for right predicate.
      }
 
      pyth and rpm filter pairs 20
 3 4  4 3  5 12  8 15  12 5  15 8
```

Better, but we still have some duplicates: `(3 4) (4 3)`
```apl
      less←{</⊃⍵}
      less(3 4)(4 3)
1 0
 
      less and pyth and rpm filter pairs 40
 3 4  5 12  7 24  8 15  9 40  12 35  20 21
```

And finally, as promised, triples:
```apl
      {⍵,hyp ⍵}¨less and pyth and rpm filter pairs 35
 3 4 5  5 12 13  7 24 25  8 15 17  12 35 37  20 21 29
```

## A Larger Example

Function `tokens` uses nested local dfns to split an APL expression into its constituent tokens. Note that all calls on the inner functions: `lex, acc`,  and the unnamed dfn in each token case, are *tail calls*. In fact, the *only* stack calls are those on function: `all`, and the unnamed function: `{⍵∨¯1⌽⍵}`, within the "Char literal" case.

```apl
    tokens←{                        ⍝ Lex of APL src line.
        alph←⎕A,⎕Á,'_∆⍙',26↑17↓⎕AV  ⍝ Alphabet for names.
        all←{+/^\⍺∊⍵}               ⍝ No. of leading ⍺∊⍵.
        acc←{(⍺,↑/⍵)lex⊃↓/⍵}        ⍝ Accumulate tokens.
        lex←{
            0=⍴⍵:⍺ ⋄ hd←↑⍵          ⍝ Next char else done.
 
            hd=' ':⍺{               ⍝ White Space.
                size←⍵ all' '
                ⍺ acc size ⍵
            }⍵
 
            hd∊alph:⍺{              ⍝ Name
                size←⍵ all alph,⎕D
                ⍺ acc size ⍵
            }⍵
 
            hd∊'⎕:':⍺{              ⍝ System Name/Keyword
                size←⍵ all hd,alph
                ⍺ acc size ⍵
            }⍵
 
            hd='''':⍺{              ⍝ Char literal
                size←+/^\{⍵∨¯1⌽⍵}≠\hd=⍵
                ⍺ acc size ⍵
            }⍵
 
            hd∊⎕D,'¯':⍺{            ⍝ Numeric literal
                size←⍵ all ⎕D,'.¯E'
                ⍺ acc size ⍵
            }⍵
 
            hd='⍝':⍺ acc(⍴⍵)⍵       ⍝ Comment
            ⍺ acc 1 ⍵               ⍝ Single char token.
        }
        (0⍴⊂'')lex,⍵
    }
      display tokens'xtok←size↑srce ⍝ Next token'
.→-------------------------------------------------.
| .→---. .→. .→---. .→. .→---. .→-. .→-----------. |
| |xtok| |←| |size| |↑| |srce| |  | |⍝ Next token| |
| '----' '-' '----' '-' '----' '--' '------------' |
'∊-------------------------------------------------'
```
