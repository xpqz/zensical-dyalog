# <span class="name">Unnamed Namespaces</span> {: .heading}

The monadic form of `⎕NS` makes a new (and unique) unnamed namespace and returns a ref to it.

One use of unnamed namespaces is to represent hierarchical data structures; for example, a simple employee database:

The first record is represented by `JOHN` which is a ref to an unnamed namespace:
```apl
      JOHN←⎕NS ''                         
      JOHN
#.[Namespace]
 
      JOHN.FirstName←'John'
      JOHN.FirstName
John
 
      JOHN.LastName←'Smith'
      JOHN.Age←50
```

Data variables for the second record, `PAUL`, can be established using strand, or vector, assignment:
```apl
      PAUL←⎕NS ''
      PAUL.(FirstName LastName Age←'Paul' 'Brown' 44)
```

The function `SHOW` can be used to display the data in each record (the function is split into 2 lines only to fit on the printed page). Notice that its argument is a ref.
```apl
     ∇ R←SHOW PERSON
[1]    R←PERSON.FirstName,' ',PERSON.LastName
[2]    R, ←' is ',⍕PERSON.Age
     ∇
 
      SHOW JOHN
John Smith is 50
 
      SHOW PAUL
Paul Brown is 44
```

An alternative version of the function illustrates the use of the `:With :EndWith` control structure to execute an expression, or block of expressions, within a namespace:
```apl
     ∇ R←SHOW1 PERSON
[1]    :With PERSON
[2]        R←FirstName,' ',LastName,' is ',(⍕Age)
[3]    :EndWith
     ∇
 
      SHOW1 JOHN
John Smith is 50
```

In this case, as only a single expression is involved, it can be expressed more simply using parentheses.
```apl
     ∇ R←SHOW2 PERSON
[1]    R←PERSON.(FirstName,' ',LastName,' is ',(⍕Age))
     ∇
      SHOW2 PAUL
Paul Brown is 44
```

Dfns also accept refs as arguments:
```apl
      SHOW3←{
        ⍵.(FirstName,' ',LastName,' is ',⍕Age)
      }
 
      SHOW3 JOHN
John Smith is 50
```
