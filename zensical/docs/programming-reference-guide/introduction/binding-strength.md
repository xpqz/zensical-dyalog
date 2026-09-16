---
tags:
  - Explanation
---

#  Binding Strength

For two entities `X` and `Y` that are adjacent in an expression (that is, `X Y`), the binding strength between them and
the result of the bind is shown in this table:

<table>
    <tbody>
    <tr>
        <td>&#160;</td>
        <td>&#160;</td>
        <th colspan="7"><strong>Y</strong></th>
    </tr>
    <tr>
        <td>&#160;</td>
        <td>&#160;</td>
        <th><strong>A</strong></th>
        <th><strong>F</strong></th>
        <th><strong>H</strong></th>
        <th><strong>MOP</strong></th>
        <th><strong>DOP</strong></th>
        <th><strong>DOT</strong></th>
        <th><strong>IDX</strong></th>
    </tr>
    <tr>
        <td rowspan="10" style="text-align: center;"><strong>X</strong></td>
        <td><strong>A</strong></td>
        <td>
            6: A
        </td>
        <td>
            3: AF
        </td>
        <td>
            3: AF
        </td>
        <td>
            4: F
        </td>
        <td>
            &#160;
        </td>
        <td>
            7: REF
        </td>
        <td>
            4: A
        </td>
    </tr>
    <tr>
        <td><strong>F</strong></td>
        <td>
            2: A
        </td>
        <td>
            1: F
        </td>
        <td>
            4: F
        </td>
        <td>
            4: F
        </td>
        <td>&#160;</td>
        <td>&#160;</td>
        <td>
            4: F
        </td>
    </tr>
    <tr>
        <td><strong>H</strong></td>
        <td>
            &#160;
        </td>
        <td>
            1: F
        </td>
        <td>
            4: F
        </td>
        <td>
            4: F
        </td>
        <td>&#160;</td>
        <td>&#160;</td>
        <td>
            4: H
        </td>
    </tr>
    <tr>
        <td><strong>AF</strong></td>
        <td>
            2: A
        </td>
        <td>
            1: F
        </td>
        <td>&#160;</td>
        <td>&#160;</td>
        <td>&#160;</td>
        <td>&#160;</td>
        <td>&#160;</td>
    </tr>
    <tr>
        <td><strong>MOP</strong></td>
        <td>&#160;</td>
        <td>&#160;</td>
        <td>
            4: ERR
        </td>
        <td>&#160;</td>
        <td>&#160;</td>
        <td>&#160;</td>
        <td>&#160;</td>
    </tr>
    <tr>
        <td><strong>DOP</strong></td>
        <td>
            5: MOP
        </td>
        <td>
            5: MOP
        </td>
        <td>
            5: MOP
        </td>

        <td>&#160;</td>
        <td>&#160;</td>
        <td>&#160;</td>
        <td>&#160;</td>
    </tr>
    <tr>
        <td><strong>JOT</strong></td>
        <td>
            5: MOP
        </td>
        <td>
            5: MOP
        </td>
        <td>
            5: MOP
        </td>
        <td>
            4: F
        </td>
        <td>&#160;</td>
        <td>&#160;</td>
        <td>&#160;</td>
    </tr>
    <tr>
        <td><strong>DOT</strong></td>
        <td>
            6: ERR
        </td>
        <td>
            5: MOP
        </td>
        <td>
            5: MOP
        </td>
        <td>&#160;</td>
        <td>
            6: ERR
        </td>
        <td>&#160;</td>
        <td>&#160;</td>
    </tr>
    <tr>
        <td><strong>REF</strong></td>
        <td>
            7: A
        </td>
        <td>
            7: F
        </td>
        <td>
            7: H
        </td>
        <td>
            7: MOP
        </td>
        <td>
            7: DOP
        </td>
        <td>&#160;</td>
        <td>&#160;</td>
    </tr>
    <tr>
        <td><strong>IDX</strong></td>
        <td>
            3: ERR
        </td>
        <td>
            3: ERR
        </td>
        <td>
            3: ERR
        </td>
        <td>&#160;</td>
        <td>&#160;</td>
        <td>&#160;</td>
        <td>&#160;</td>
    </tr>
    </tbody>

</table>

where

- **A**: Array[^1], for example, `0 1 2 'hello' ⍺ ⍵`
- **F**: Function[^1] {primitive | defined | derived | system}, for example, `+ - +.× myfn ⎕CR {⍺ ⍵}`
- **H**: Hybrid[^1] function/operator, that is, `/ ⌿ \ ⍀`
- **AF**: Bound left argument, for example, `2+`
- **MOP**: Monadic operator[^1], for example, `¨ ⍨ &`
- **DOP**: Dyadic operator, for example, `⍣ ⍠ ⍤ ⌸`
- **JOT**: Jot, that is, compose/null operand `∘`
- **DOT**: Dot, that is, reference/product `.`
- **IDX**: square-bracketed expression, for example, `[⍺+⍳⍵]`
- **ERR**: Error

In this table:

- the higher the number, the stronger the binding
- an empty field indicates no binding for this combination; an error.

For example, in the expression `a b.c[d]`, where `a`, `b`, `c` and `d` are arrays, the binding proceeds:

```apl
      a b . c [d]
       6 7 6 4      ⍝ binding strengths between entities
→     a (b.) c [d]
       0    7 4
→     a (b.c) [d]
       6     4
→     (a(b.c))[d]
```

[^1]: Indicates a "first-class" entity, which can be parenthesised or named.
