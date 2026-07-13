# <span class="name">Public Fields</span> {: .heading}

A *Public* Field may be accessed from outside an Instance or a Class. Note that the default is *Private*.

Class `DomesticParrot` has a `Name` Field which is defined to be Public and Instance (by default).
```apl
:Class DomesticParrot: Parrot
    :Field Public Name
    
    ∇ egg nm
      :Access Public
      :Implements Constructor
      Name←nm
    ∇
    ...
:EndClass ⍝ DomesticParrot
```

The Name field is initialised by the Class constructor.
```apl
      pet←⎕NEW DomesticParrot'Polly'
      pet.Name
Polly
```

The Name field may also be modified directly:
```apl
      pet.Name←⌽pet.Name
      pet.Name
ylloP
```
