---
search:
  boost: 2
---

<!-- Hidden search keywords -->
<div style="display: none;">
  2011⌶
</div>

# <span class="name">Read DataTable</span> <span class="command">R←\{X\}2011⌶Y</span> {: .heading}

!!! note
    **.NET Framework only**

This function performs a *block read* from an instance of the ADO.NET object System.Data.DataTable. This object may only be read using an explicit row-wise loop, which is slow at the APL level. `2011⌶` implements an *internal* row-wise loop which is much faster on large arrays. Furthermore, the function handles NULL values and the conversion of .NET data types to the appropriate internal APL form in a more efficient manner than can otherwise be achieved. These 3 factors together mean that the function provides a significant improvement in performance compared to calling the row-wise programming interface directly at the APL level.

`Y` is a scalar or a 1 or 2-item array containing:

1. A reference to an instance of `System.Data.DataTable`.
2. An optional vector which specifies the values to which a `System.DBNull` should be mapped in the corresponding columns of the result 

The result `R` depends upon the value of the  Variant option Invert. This the primary option with a default value of 0.

## Invert Option (Boolean)

|---|----------------------------------------------------------------------------------------------------------------|
|0  |The result `R` is a matrix with the same shape as the DataTable referenced by `⊃Y`.                             |
|`1`|The result `R` is vector whose length is the same as the number of columns in the DataTable referenced by `⊃Y`. |

The optional left argument `X` is a numeric vector with the same length as the number of columns in the result in the DataTable referenced by `⊃Y`:

|---|---|
|1|Specifies that the corresponding column of the result should be converted to a string using the `ToString` method of the data type of column in question.|
|2|Specifies that numbers of type `System.Int64` in the corresponding column of the result should be converted to DECFs (NOT into .NET objects, which is the default)|
|4|Specifies that if the type of the corresponding column is `System.String` the entire column should be returned as a character matrix rather than a vector of character vectors. Any nulls will be replaced with a row of spaces. This applies only when **Invert** is 1.|
|5|Combines 1 and 4.|

<h2 class="example">Examples</h2>
```apl
      ⎕USING←'' 'System.Data,system.data.dll'
      
      dt←⎕NEW DataTable

      add_col←{col←⍺.Columns.Add ⍬ ⋄ col.DataType←⍵}
      dt add_col System.String          
      dt add_col System.Int32            
      dt add_col System.Int64             
```
```apl

      in←⍉↑('One' 'Two')(1 2)(6401 6402)
      2010⌶ dt in

      ⎕←out←2011⌶ dt                              
┌───┬─┬──────┐
│One│1│ 6401 │
├───┼─┼──────┤
│Two│2│ 6402 │
└───┴─┴──────┘
      out[;3].GetType
System.Int64  System.Int64
```
```apl
      0 0 2(2011⌶) dt ⍝ Convert 3rd col to DECF
┌───┬─┬────┐
│One│1│6401│
├───┼─┼────┤
│Two│2│6402│
└───┴─┴────┘
```
```apl
      1 1 1(2011⌶)dt ⍝ Convert all values to text
┌───┬─┬────┐
│One│1│6401│
├───┼─┼────┤
│Two│2│6402│
└───┴─┴────┘
```
```apl
      ((2011⌶)⍠('Invert' 1)) dt
┌─────────┬───┬────────────┐
│┌───┬───┐│1 2│ 6401  6402 │
││One│Two││   │            │
│└───┴───┘│   │            │
└─────────┴───┴────────────┘
```
```apl
       4 0 0((2011⌶)⍠('Invert' 1))dt
┌───┬───┬────────────┐
│One│1 2│ 6401  6402 │
│Two│   │            │
└───┴───┴────────────┘
```
```apl
       5 5 5((2011⌶)⍠('Invert' 1))dt ⍝ Convert to cmats
┌───┬─┬────┐
│One│1│6401│
│Two│2│6402│
└───┴─┴────┘
```

## Handling Nulls
```apl
      2010⌶dt(1 3⍴⎕NULL) ⍝ Add a row of nulls
      ⎕←out←2011⌶ dt 
┌───┬──┬──────┐
│One│1 │ 6401 │
├───┼──┼──────┤
│Two│2 │ 6402 │
├───┼──┼──────┤
│   │  │      │
└───┴──┴──────┘
      out[3;].GetType
 System.DBNull  System.DBNull  System.DBNull
```
```apl

      2011⌶ dt ('this is null' 'this too' 'and this')
┌────────────┬────────┬────────┐
│One         │1       │ 6401   │
├────────────┼────────┼────────┤
│Two         │2       │ 6402   │
├────────────┼────────┼────────┤
│this is null│this too│and this│
└────────────┴────────┴────────┘

```

## Performance Considerations

First for comparison is shown the type of code that is required to read a DataTable by looping:
```apl
      t←3⊃⎕AI ⋄ data1←↑(⌷dt.Rows).ItemArray ⋄ (3⊃⎕AI)-t
191
```

The above expression turns the `dt.Rows` collection into an array using `⌷`, and *mixes* the ItemArray properties to produce the result. Although here there is no explicit loop, involved, there is an implicit loop required to reference each item of the collection in succession. This operation performs at about 200 rows/sec.

`2011⌶` does the looping entirely in compiled code and is significantly faster:
```apl
      GetDT←2011⌶
      t←3⊃⎕AI ⋄ data2←GetDT dt ⋄ (3⊃⎕AI)-t
25
```

In the first case, `2011⌶` created 365 instances of System.DateTime objects in the workspace. If we are willing to receive the timestamps in the form of strings, we can read the data almost an order of magnitude faster:
```apl
      t←3⊃⎕AI ⋄ data3←0 0 0 1 GetDT dt ⋄ (3⊃⎕AI)-t
3
```

The left argument to `2011⌶` allows you to flag columns which should be returned as the `ToString()` value of each object in the flagged columns. Although the resulting array looks identical to the original, it is not: The fourth column contains character vectors:
```apl
      ¯2 4↑data3
 364  even  4  18-01-2011 14:03:29
 365  odd   5  19-01-2011 14:03:29
```

Depending on your application, you may need to process the text in the fourth column in some way – but the overall performance will probably still be very much better than it would be if DateTime objects were used.

