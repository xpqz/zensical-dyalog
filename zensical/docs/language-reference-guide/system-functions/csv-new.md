---
search:
  boost: 2
---

# Comma Separated Values `{R}←{X} ⎕CSV Y`

```text
{R}←{X} ⎕CSV Y
```
[Key to notation](../key-to-notation.md)

This function imports and exports Comma Separated Value (CSV) data. Monadic `⎕CSV` imports data from a CSV file or converts CSV text into an APL array; dyadic `⎕CSV` exports an APL array to a CSV file or converts it into CSV text. Separators, quoting, numeric formats and fixed-width layouts are controlled through the [variant operator](../primitive-operators/variant.md) `⍠`.

[Examples](#examples) · [Import specification](#import-monadic) · [Export specification](#export-dyadic) · [Further examples](#further-examples)

## Examples

Create `sales.csv` in the current working directory with the following contents. The examples use `⎕IO←1`; array results are shown with boxed display.

```text
Product,Sales
Widgets,1912
Gimlets,205
Dingbats,189
```

### Read a CSV file

Name the file, say which columns are numeric, and say that the first record is a header:

```apl
⎕IO←1
data hdr←⎕CSV 'sales.csv' '' (1 2) 1
data
```

```text
┌────────┬────┐
│Widgets │1912│
├────────┼────┤
│Gimlets │205 │
├────────┼────┤
│Dingbats│189 │
└────────┴────┘
```

```apl
hdr
```

```text
┌───────┬─────┐
│Product│Sales│
└───────┴─────┘
```

```apl
+/data[;2]
```

```text
2306
```

The four elements of the right argument are the source (`'sales.csv'`), the file encoding (`''`: deduce it), the column types (`1 2`: character, numeric) and the header-row indicator (`1`: the first record is a header, returned separately). With the source alone, every field is returned as text and the header is just another row:

```apl
⎕CSV 'sales.csv'
```

```text
┌────────┬─────┐
│Product │Sales│
├────────┼─────┤
│Widgets │1912 │
├────────┼─────┤
│Gimlets │205  │
├────────┼─────┤
│Dingbats│189  │
└────────┴─────┘
```

### Write a CSV file

Using `data` and `hdr` from the import above, give the data and header on the left and a new file name on the right:

```apl
bytes←data hdr ⎕CSV 'sales-copy.csv'
```

This creates `sales-copy.csv` with the same records as `sales.csv`. The [shy](../../programming-reference-guide/introduction/results.md#shy-results) result is the number of bytes written, which depends on the encoding and line endings. An existing file signals `FILE NAME ERROR`; see [Replace an existing file](#replace-an-existing-file) for deliberate replacement.

### Convert text without a file

CSV data already in the workspace can be converted directly. A vector of lines must be marked as nested data with `'N'` (or enclosed), otherwise its items are taken to be the source, encoding and column types:

```apl
lines←'Product,Sales' 'Widgets,1912' 'Gimlets,205'
⎕CSV lines 'N'
```

```text
┌───────┬─────┐
│Product│Sales│
├───────┼─────┤
│Widgets│1912 │
├───────┼─────┤
│Gimlets│205  │
└───────┴─────┘
```

## Internal format

Arrays that result from importing CSV data or arrays that are suitable for exporting as CSV data are represented by 3 possible structures:

- A table (a matrix whose elements are character vectors or scalars, or numbers).
- A vector, each of whose items contain field (column) values. Character field values are character matrices; numeric field values are numeric vectors.
- A vector, each of whose items contain field (column) values. Character field values are vectors of character vectors; numeric field values are numeric vectors.

When importing CSV data, all fields are assumed to be character fields unless otherwise specified (see [Column Types](#columntypes)). A field that contains only "numbers" will not be converted to numeric data unless specified as being numeric.

## Metacharacters

Some characters in a CSV file are metacharacters that define the structure of the data; for example, the field separator character between fields. Characters that are not metacharacters are literal characters. The variant options `QuoteChar`, `EscapeChar`, and `DoubleQuote` make it possible to interpret metacharacters as literal characters, and thus permit fields to contain field separator characters, leading and trailing spaces, and line-endings.

Fixed-width fields do not require these options and they are ignored if fixed-width fields are being processed.

## Import (monadic)

```text
R←⎕CSV Y
```

`Y` is an array that specifies just the source of the CSV data (see below) or a 1,2,3 or 4-element vector containing:

|-----|---------------------------|
|`[1]`|Source of CSV Data         |
|`[2]`|Description of the CSV data|
|`[3]`|Column Types               |
|`[4]`|Header Row Indicator       |

*Source* can be one of:

- a character vector or scalar containing a file name
- a native tie number
- a character vector or scalar containing CSV data with embedded newline characters. To avoid this source being interpreted as a file name, `Y[2]` must be specified as `'S'`.
- a vector of character vectors and/or scalars containing CSV data with implicit newlines after each character vector or scalar

*Description*

If `Y[1]` is a file name or tie number *Description* can be one of:

- a character vector specifying the file encoding such as `'UTF-8'` (see [File Encodings](nget.md)).
- a 256-element numeric vector that maps each possible byte value (0-255) to a Unicode code point (1st element = Unicode code point corresponding to byte value 0, and so on). ¯1 indicates that the corresponding byte value is not mapped to any character. Apart from ¯1, no value can appear in the table more than once.

If omitted or empty, the file encoding is deduced (see [File handling](#file-handling)).

If `Y[1]` is a character array containing CSV data *Description* is a character scalar `'S'` (simple) or `'N'` (nested). The default is `'N'`

*Column Types*{ #columntypes }

This is a scalar numeric code or vector of numeric codes that specifies the field types from the list below. If *Column Types* is zilde or omitted, the default is 1 (all fields are character).

|---|---|
|`0`|The field is ignored.|
|`1`|The field contains character data.|
|`2`|The field is to be interpreted as being numeric. Empty cells and cells which cannot be converted to numeric values are not tolerated and cause an error to be signalled.|
|`3`|The field is to be interpreted as being numeric but invalid numeric values are tolerated. Empty fields and fields which cannot be converted to numeric values are replaced with the `Fill` variant option (default `0`).|
|`4`|The field is to be interpreted numeric data but invalid numeric data is tolerated. Empty fields and fields which cannot be converted to numeric values are returned instead as character data; this type is disallowed when variant option `Invert` is set to `1`.|
|`5`|The field is to be interpreted as being numeric but empty fields are tolerated and are replaced with the `Fill` variant option (default `0`). Non-empty cells which cannot be converted to numeric values are not tolerated and cause an error to be signalled.|

If *Column Types* is specified by a scalar `4`, all numeric data in all fields are converted to numbers.

*Header Row Indicator*

This is a Boolean value (default 0) to specify whether or not the first record in a CSV file is a list of column labels. If *Header Row Indicator* is 1, the first record (the *header row*) is treated differently from other records. It is assumed to contain character data (labels) regardless of `Y[3]` and is returned separately in the result.

### Variant options

Monadic `⎕CSV` can be applied using the _variant_ operator with the options shown in [](#variantoptionsforcsv). The principal option is `Invert`.

Table: Variant options for `⎕CSV` { #variantoptionsforcsv }

|Name       |Meaning                                     |Default|
|-----------|--------------------------------------------|-------|
|`Decimal`    |The decimal mark in numeric fields - one of `'.'` or `','` |   `'.'`|
|`DoubleQuote`|A Boolean that indicates whether (`1`) or not (`0`) a quote character within a quoted field is represented by two consecutive quote characters     |`1`    |
|`EscapeChar` |The escape character, which can be specified as an empty character vector (meaning none is defined) or a character scalar                |`''`   |
|`Fill`       |The numeric value substituted for invalid numeric data in  columns of type 3   |`0`    |
|`Invert`<br><small>principal</small>|A number specifying how the CSV data should be returned. Possible values are:<ul><li>`0` – A table (a matrix whose elements are character vectors or scalars or numbers).</li><li>`1` – A vector, each of whose items contain field (column) values. Character field values are character matrices; numeric field values are numeric vectors.</li><li>`2` – A vector, each of whose items contain field (column) values. Character field values are vectors of character vectors; numeric field values are numeric vectors.</li></ul>    |`0`    |
|`QuoteChar`  |The field quote character (delimiter), which can be specified as an empty character vector (meaning none is defined) or a character scalar                 |`"`    |
|`Ragged`     |A Boolean specifying whether records with varying numbers  of fields are allowed; see notes below                                                          |`0`    |
|`Records`    |The maximum number of records to process or 0 for no limit.                    |`0`    |
|`Separator`  |The field separator, any single character. If `Widths` is other than `⍬`, `Separator` is ignored.                                                            |`','`  |
|`Thousands`  |The thousands separator in numeric fields, which can be specified as an empty character vector (meaning no separator is defined) or a character scalar   |`''`   |
|`Trim`       |A Boolean specifying whether undelimited/unescaped whitespace is trimmed at the beginning and end of fields            |`1`    |
|`Widths`     |A vector of numeric values describing the width (in characters) of the corresponding columns in the CSV source, or `⍬` for variable width delimited fields|`⍬`    |

The `Separator`, `QuoteChar`, and `EscapeChar` characters, when defined, must be different.

Other [variant options defined for export](#variantoptionsforcsv2) are also accepted but ignored.

### `QuoteChar`, `EscapeChar`, and `DoubleQuote`

If `EscapeChar` is set, then any character can be prefixed by the escape character. The escape character is typically defined as `'\'`. The escape character immediately followed by the character `c` is the literal character `c`, even if `c` alone would have been a metacharacter.

If `QuoteChar` is set, then fields can be delimited by the specified quote character. Within quoted fields all characters except the quote character, and the escape character if defined, are literal characters.

If `DoubleQuote` is set to `1`, then two consecutive quote characters within a quoted field are interpreted as the single literal quote character.

### Result

The result `R` contains the imported data.

If `Y[4]` does not specify that the data contains a header, then `R` contains the entire data in the form specified by the `Invert` variant option.

If `Y[4]` does specify that the data contains a header, then `R` is a 2-element vector where:

- `R[1]` is the imported data excluding the header.
- `R[2]` is a vector of character vectors containing the header record.

### Notes

- When `Y` specifies just the source of the CSV data, it does not need to be enclosed or ravelled to create a 1-element vector.
- `Y[2]`, the description of the source, distinguishes an otherwise ambiguous character vector source (which could contain either CSV data or a file name). The other source forms are unambiguous but the description, when given, must still match the given source type.
- Tab-separated fields can be imported by specifying `'Separator' (⎕UCS 9)`.
- Fields containing embedded new lines are supported (they must, of course, appear in quotes or be prefixed by the escape character). On import, line endings are always converted to a single line feed character.
- If `Ragged` is not set, then all records must have the same number of fields (character delimited format) or same number of characters (fixed width field format).
- If `Ragged` is set:
    - The expected number of columns must be specified using the `Widths` variant option and/or the column types in `Y[3]`.
    - In character delimited format, all processed records are implicitly extended or truncated as required so that they contain the expected number of fields; implicitly added fields will be empty.
    - In fixed width format, all processed records are implicitly extended with spaces or truncated as required so that they contain as many characters as are specified in the `Widths` option declaration.

### File handling

Data can be read from a named file or a tied native file. A tied native file can be read in sections by repeatedly invoking `⎕CSV` for a specified maximum number of records (specified by the `Records` variant option) until no more data is read.

In all cases the files must contain text using one of the supported encodings (see [File Encodings](nget.md)). The method used to determine the file encoding is as follows:

- If a Byte Order Mark (BOM) is encountered at the start of the file, it is used regardless of `Y[2]` (if specified). However, the BOM can only be encountered if the file is read from the start - specifically, if a native file is read in sections, any BOM present will only be encountered when the first section is read.
- Otherwise, the file will be read and decoded according to the file encoding in `Y[2]` if specified.
- Otherwise:
    - Native files will be decoded as if `'UTF-8'` had been specified.
    - Files specified by name will be examined and the likely file encoding will be deduced using the same heuristics performed by `⎕NGET`.

In addition:

- native files are read from the current file position. On successful completion, the file position will be at the first unprocessed character (end of file if the `Records` variant option is not specified). If an error is signalled the file position is undefined.
- the result does not report the file encoding or line ending type as it does with `⎕NGET`. If this information is required, then it must be obtained by other means.

## Export (dyadic)

```text
{R}←X ⎕CSV Y
```

The left argument `X` is either:

- a matrix or a vector of vectors/matrices containing the data to be converted to CSV format.
- or a 2-element vector containing a matrix or vector of vectors/matrices containing the data to be converted to CSV format, and a vector of character vectors containing the header record.

`Y` is a 1 or 2-element vector containing:

|-----|---------------------------------------|
|`[1]`|Destination of CSV Data (see below)    |
|`[2]`|Description of the CSV data (see below)|

*Destination* - can be one of:

- a character vector or scalar containing a file name
- a native tie number
- an empty character vector, indicating that the CSV data is to be returned in the result `R`

*Description*

If `Y[1]` is a file name or tie number, *Description* can be:

- a character vector specifying the file encoding such as `'UTF-8'` (see [File Encodings](nget.md)).
- a 256-element numeric vector that maps each possible byte value (0-255) to a Unicode code point (1st element = Unicode code point corresponding to byte value 0, and so on). ¯1 indicates that the corresponding byte value is not mapped to any character. Apart from ¯1, no value can appear in the table more than once.

If `Y[1]` is empty, *Description* can be a character scalar `'S'` (simple) or `'N'` (nested). If omitted, the default is `'S'`.

### Variant options

Dyadic `⎕CSV` can be applied using the _variant_ operator with the options shown in [](#variantoptionsforcsv2).

Table: Variant options for dyadic `⎕CSV` { #variantoptionsforcsv2 }

|Name|Meaning|Default|
|---|---|---|
|`Decimal`|the decimal mark in numeric fields - one of `'.'` or `','`|`'.'`|
|`DoubleQuote`|A Boolean which indicates whether (`1`) or not (`0`) a quote character within a quoted field is represented by two consecutive quote characters|`1`|
|`EscapeChar`|The escape character, which can be specified as an empty character vector (meaning none is defined) or a character scalar|`0`|
|`ForceQuotes`|A number specifying the degree to which quotes are applied around fields, even if not strictly required. Possible values are:<ul><li>`0` – add only if required</li><li>`1` – add to all fields containing character data and to fields containing numeric data if required</li><li>`2` – add to all fields, even if not required</li></ul>If `ForceQuotes` is a scalar, the value applies to all columns; if it is a vector of values, then each value applies to the corresponding column.|`0`|
|`IfExists`|a character vector `'Error'` or `'Replace'` which specifies, when creating a named file which already exists, whether to overwrite it ( `'Replace'` ) or signal an error ( `'Error'` )|`'Error'`|
|`LineEnding`|the line ending sequence - see [Line separators:](nget.md)|(13 10) on Windows; 10 on other platforms|
|`QuoteChar`|The field quote character (delimiter), which can be specified as an empty character vector (meaning none is defined) or a character scalar|`"`|
|`Separator`|the field separator, any single character. If `Widths` is other than `⍬` , `Separator` is ignored.|`','`|
|`Thousands`|the thousands separator in numeric fields, which can be specified as an empty character vector (meaning no separator is defined) or a character scalar|`''`|
|`Trim`|a Boolean specifying whether whitespace is trimmed at the beginning and end of character fields|`1`|
|`Widths`|a vector of numeric values describing the width (in characters) of the corresponding columns in the CSV source, or `⍬` for variable width delimited fields|`⍬`|

The `Separator`, `QuoteChar`, and `EscapeChar` characters, when defined, must be different.

Other [variant options defined for import](#variantoptionsforcsv) are also accepted but ignored.

The `Overwrite` variant option (a Boolean) remains supported but is deprecated in favour of `IfExists`.

### `QuoteChar`, `EscapeChar`, and `DoubleQuote`

- The CSV text will be generated such that it can be read back according to the corresponding rules for import.
- If these options do not permit this (for example, a field contains the quote character and neither `DoubleQuote` or `EscapeChar` are set) an error is signalled.
- Quoting and Escaping is used as conservatively as possible.
- If both `QuoteChar` and `EscapeChar` are set, quoting is favoured.

### Result

If `Y` specifies that the CSV data is written to a file, then `R` is the number of bytes (not characters) written, and is [shy](../../programming-reference-guide/introduction/results.md#shy-results).

Otherwise, `R` is the CSV data in the format specified in Y, and is not shy.

`⎕CSV` output is not affected by [`⎕PP`](pp.md); numeric values are always represented with full precision.

### Notes

- When `Y` contains only the destination of the CSV data (that is, omits the description in its second element) it does not have to be enclosed to form a single element vector.
- Native files are written from the current file position. On successful completion, the file position will be at the end of the written data. If an error is signalled the amount of data written is undefined.
- If the file encoding specifies that a BOM is required and output is to a native file, it will only be written if the file position is initially at 0 - that is, the start of the file is being written.
- When fixed width fields are written, character data shorter than the specified width is padded with spaces to the right and character data longer than the specified width signals an error. Numeric data is converted to character data as far as possible so that it fits into the specified width. If this is not possible, an error is signalled.
- Tab-separated fields can be exported by specifying `'Separator' (⎕UCS 9)`.
- Fields containing a single embedded new line are supported. On export, line feed characters are mapped back to the defined line ending sequence.

## Further examples

These examples cover additional representations, options and file layouts. File-based examples specify the required contents; save each file in the current working directory before running its example.

### Text representations

A single character vector with embedded line endings must be marked as simple data with `'S'`, otherwise it is taken to be a file name:

```apl
⎕CSV ('Product,Sales',(⎕UCS 10),'Widgets,1912') 'S'
```

```text
┌───────┬─────┐
│Product│Sales│
├───────┼─────┤
│Widgets│1912 │
└───────┴─────┘
```

Using `data` and `hdr` from [Read a CSV file](#read-a-csv-file), an empty destination returns the CSV text as the result, as one character vector or, with `'N'`, as a vector of lines:

```apl
data hdr ⎕CSV ''
```

```text
Product,Sales
Widgets,1912
Gimlets,205
Dingbats,189
```

```apl
data hdr ⎕CSV '' 'N'
```

```text
┌─────────────┬────────────┬───────────┬────────────┐
│Product,Sales│Widgets,1912│Gimlets,205│Dingbats,189│
└─────────────┴────────────┴───────────┴────────────┘
```

### Replace an existing file

By default, exporting to an existing file signals `FILE NAME ERROR`. To replace `sales-copy.csv` deliberately, use `IfExists`:

```apl
bytes←data hdr (⎕CSV⍠'IfExists' 'Replace') 'sales-copy.csv'
```

This overwrites the file. It uses `data` and `hdr` from [Read a CSV file](#read-a-csv-file).

### Numeric columns and bad data

Fields are text unless a column type says otherwise. The type also decides what happens to empty or non-numeric fields. Consider `stock.csv`:

```text
Item,Qty,Price
Bolt,10,0.25
Nut,,0.10
Washer,n/a,0.05
```

Type `2` is strict:

```apl
⎕CSV 'stock.csv' '' (1 2 2) 1
```

```text
DOMAIN ERROR: Non-numeric data in record 3, field 2 (⎕IO=1)
```

Type `3` replaces anything that is not a number with the `Fill` value, `0` by default:

```apl
(⎕CSV⍠'Fill' ¯1) 'stock.csv' '' (1 3 3) 1
```

```text
┌────────────────┬────────────────┐
│┌──────┬──┬────┐│┌────┬───┬─────┐│
││Bolt  │10│0.25│││Item│Qty│Price││
│├──────┼──┼────┤│└────┴───┴─────┘│
││Nut   │¯1│0.1 ││                │
│├──────┼──┼────┤│                │
││Washer│¯1│0.05││                │
│└──────┴──┴────┘│                │
└────────────────┴────────────────┘
```

Type `4` converts what it can and keeps the rest as text. As a scalar it applies to every column, which is the quickest way to load a file whose layout you do not know yet:

```apl
⎕CSV 'stock.csv' '' 4 1
```

```text
┌─────────────────┬────────────────┐
│┌──────┬───┬────┐│┌────┬───┬─────┐│
││Bolt  │10 │0.25│││Item│Qty│Price││
│├──────┼───┼────┤│└────┴───┴─────┘│
││Nut   │   │0.1 ││                │
│├──────┼───┼────┤│                │
││Washer│n/a│0.05││                │
│└──────┴───┴────┘│                │
└─────────────────┴────────────────┘
```

Type `5` tolerates empty fields (replaced by `Fill`) but not non-numeric text, and `0` skips a column altogether. The full list is under [Column Types](#columntypes).

### Columns instead of rows

`Invert` returns the data one column at a time: `2` gives each character column as a vector of vectors and each numeric column as a numeric vector, ready to assign to separate names:

```apl
(product sales) hdr←(⎕CSV⍠'Invert' 2) 'sales.csv' '' (1 2) 1
sales
```

```text
1912 205 189
```

```apl
product
```

```text
┌───────┬───────┬────────┐
│Widgets│Gimlets│Dingbats│
└───────┴───────┴────────┘
```

`Invert` `1` differs only in returning character columns as character matrices.

### Other separators and decimal marks

Create `sales.tsv` with these records, using a tab between fields:

```text
Product	Sales
Widgets	1912
Gimlets	205
```

```apl
(⎕CSV⍠'Separator' (⎕UCS 9)) 'sales.tsv' '' (1 2) 1
```

```text
┌──────────────┬───────────────┐
│┌───────┬────┐│┌───────┬─────┐│
││Widgets│1912│││Product│Sales││
│├───────┼────┤│└───────┴─────┘│
││Gimlets│205 ││               │
│└───────┴────┘│               │
└──────────────┴───────────────┘
```

Files written with a decimal comma use a different field separator too. Save the following as `umsatz.csv`. Several options are given as a vector of name-value pairs:

```text
Produkt;Umsatz
Widgets;1912,50
Gimlets;205,00
```

```apl
(⎕CSV⍠('Separator' ';')('Decimal' ',')) 'umsatz.csv' '' (1 2) 1
```

```text
┌────────────────┬────────────────┐
│┌───────┬──────┐│┌───────┬──────┐│
││Widgets│1912.5│││Produkt│Umsatz││
│├───────┼──────┤│└───────┴──────┘│
││Gimlets│205   ││                │
│└───────┴──────┘│                │
└────────────────┴────────────────┘
```

The same options apply on export. `Thousands` names a thousands separator, `''` by default.

### Quoted fields

A field containing the separator, a quote or a line ending is quoted, and a quote inside a quoted field is doubled. `⎕CSV` reads such files without further options. Save this example as `quoted.csv`:

```text
Name,Note
"Smith, John","She said ""hello"""
"Jones, Ann","Two
lines"
```

```apl
⊃⎕CSV 'quoted.csv' '' ⍬ 1
```

```text
┌───────────┬────────────────┐
│Smith, John│She said "hello"│
├───────────┼────────────────┤
│Jones, Ann │Two             │
│           │lines           │
└───────────┴────────────────┘
```

On export, quotes are added only where needed unless `ForceQuotes` says otherwise:

```apl
X←2 2⍴'Smith, John' 'She said "hello"' 'Ann' ('Two',(⎕UCS 10),'lines')
X ⎕CSV ''
```

```text
"Smith, John","She said ""hello"""
Ann,"Two
lines"
```

```apl
X (⎕CSV⍠'ForceQuotes' 2) ''
```

```text
"Smith, John","She said ""hello"""
"Ann","Two
lines"
```

`QuoteChar`, `EscapeChar` and `DoubleQuote` change the quoting rules themselves; see [Metacharacters](#metacharacters).

### Large files, a chunk at a time

A tied native file is read from its current position, so the `Records` option lets a file be processed a chunk at a time. This function totals the second column of a UTF-8 file with the same layout as `sales.csv`: one header row, then a text column and a numeric column.

Define the function in the editor:

```apl
∇ total←CsvTotal file;tn;chunk;header;error;⎕IO
  ⎕IO←1
  tn←file ⎕NTIE 0
  :Trap 0
      total←0
      chunk header←(⎕CSV⍠'Records' 1000) tn 'UTF-8' (1 2) 1
      :While 0<≢chunk
          total+←+/chunk[;2]
          chunk←(⎕CSV⍠'Records' 1000) tn 'UTF-8' (1 2)
      :EndWhile
  :Else
      error←⎕DMX
      ⎕NUNTIE tn
      ⎕SIGNAL⊂('EN' error.EN)('Message' error.Message)
  :EndTrap
  ⎕NUNTIE tn
∇
```

```apl
CsvTotal 'sales.csv'
```

```text
2306
```

The header-row indicator is supplied only on the first call. The encoding is supplied on every call because a Byte Order Mark is encountered only at the start of the file. The function releases the native-file tie on success and on a processing error.

### Ragged records

By default every record must have the same number of fields. With `Ragged`, short records are extended with empty fields and long ones truncated, to the number of columns implied by the column types (or by `Widths`):

```apl
(⎕CSV⍠'Ragged' 1) ('a,1' 'b' 'c,3,x') 'N' (1 3)
```

```text
┌─┬─┐
│a│1│
├─┼─┤
│b│0│
├─┼─┤
│c│3│
└─┴─┘
```

### Fixed-width fields

`Widths` gives the width in characters of each column; the separator is then ignored. Save the following as `fixed.txt`, preserving the spaces:

```text
Product Sales
Widgets  1912
Gimlets   205
```

```apl
(⎕CSV⍠'Widths' (8 5)) 'fixed.txt' '' (1 2) 1
```

```text
┌──────────────┬───────────────┐
│┌───────┬────┐│┌───────┬─────┐│
││Widgets│1912│││Product│Sales││
│├───────┼────┤│└───────┴─────┘│
││Gimlets│205 ││               │
│└───────┴────┘│               │
└──────────────┴───────────────┘
```

<!-- Hidden search keywords -->
<div style="display: none;">
  ⎕CSV CSV
</div>
