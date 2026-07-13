---
search:
  exclude: true
---

# <span class="name">Primitive Operators</span> {: .heading}

|Glyph|Glyph Name     |Operator                                                         |Syntax              |
|-----|---------------|-----------------------------------------------------------------|--------------------|
|`[]←`|&nbsp;         |[Assignment Indexed Modified](../other-syntax/assignment/assignment-indexed-modified.md)    |`{R}←X[I]f←Y`       |
|`←`  |Left Arrow     |[Assignment Modified](../other-syntax/assignment/assignment-modified.md)                    |`{R}←Xf←Y`          |
|`←`  |Left Arrow     |[Assignment Selective Modified](../other-syntax/assignment/assignment-selective-modified.md)|`{R}←(EXP X)f←Y`    |
|`@`  |At             |[At](at.md)                                                      |`R←{X}(f@g)Y`       |
|`⍤`  |Jot Diaeresis  |[Atop](atop.md)                                                  |`{R}←{X}f⍤gY`       |
|`[]` |&nbsp;         |[Axis with Dyadic Operand](../other-syntax/axis/axis-with-dyadic-operand.md)          |`R←Xf[B]Y`          |
|`[]` |&nbsp;         |[Axis with Monadic Operand](../other-syntax/axis/axis-with-monadic-operand.md)        |`R←f[B]Y`           |
|`⍛`  |Jot Underbar   |[Behind](behind.md)                                              |`{R}←{X}f⍛gY`       |
|`∘`  |Jot            |[Beside](beside.md)                                              |`{R}←{X}f∘gY`       |
|`∘`  |Jot            |[Bind](bind.md)                                                  |`{R}←A∘fY{R}←(f∘B)Y`|
|`⍨`  |Tilde Diaeresis|[Commute](commute.md)                                            |`{R}←{X}f⍨Y`        |
|`⍨`  |Tilde Diaeresis|[Constant](constant.md)                                          |`R←{X}(A⍨)Y`        |
|`¨`  |Diaeresis      |[Each with Dyadic Operand](each/each-with-dyadic-operand.md)          |`{R}←Xf¨Y`          |
|`¨`  |Diaeresis      |[Each with Monadic Operand](each/each-with-monadic-operand.md)        |`{R}←f¨Y`           |
|`⌶`  |IBeam          |[I-Beam](i-beam/index.md)                       |`R←{X}(A⌶)Y`        |
|`.`  |Dot            |[Inner Product](inner-product.md)                                |`R←Xf.gY`           |
|`⌸`  |Quad Equal     |[Key](key.md)                                                    |`R←{X}f⌸Y`          |
|`∘.` |&nbsp;         |[Outer Product](outer-product.md)                                |`{R}←X∘.gY`         |
|`⍥`  |Circle Dieresis|[Over](over.md)                                                  |`{R}←{X}f⍥gY`       |
|`⍣`  |Star Diaeresis |[Power](power.md)                                                |`{R}←{X}(f⍣g)Y`     |
|`⍤`  |Jot Diaeresis  |[Rank](rank.md)                                                  |`R←{X}(f⍤B)Y`       |
|`⌿`  |Slash Bar      |[Reduce First N Wise](reduce-first/reduce-first-n-wise.md)                    |`R←Xf⌿[K]Y`         |
|`⌿`  |Slash Bar      |[Reduce First](reduce-first/index.md)                                  |`R←f⌿Y`             |
|`/`  |Slash          |[Reduce N Wise](reduce/reduce-n-wise.md)                                |`R←Xf/[K]Y`         |
|`/`  |Slash          |[Reduce](reduce/index.md)                                              |`R←f/[K]Y`          |
|`⍀`  |Slope Bar      |[Scan First](scan-first.md)                                      |`R←f⍀Y`             |
|`\`  |Slope          |[Scan](scan.md)                                                  |`R←f\[K]Y`          |
|`&`  |Ampersand      |[Spawn](spawn.md)                                                |`{R}←{X}f&Y`        |
|`⌺`  |Quad Diamond   |[Stencil](stencil.md)                                            |`R←(f⌺g)Y`          |
|`⍠`  |Variant        |[Variant](variant.md)                                            |`{R}←{X}(f⍠B)Y`     |
