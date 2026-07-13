# <span class="name">Example</span> {: .heading}

In this example, Class `Penguin` inherits from `Animal` and includes functions from the plain Namespaces `BirdStuff` and `FishStuff`.
```apl
:Class Penguin: Animal
    :Include BirdStuff
    :Include FishStuff
:EndClass ⍝ Penguin
```

Namespace `BirdStuff` contains 2 functions, both declared as Public methods.
```apl
:Namespace BirdStuff
    ∇ R←Fly
      :Access Public Instance
      R←'Fly, Fly ...'
    ∇
    ∇ R←Lay
      :Access Public Instance
      R←'Lay, Lay ...'
    ∇
:EndNamespace ⍝ BirdStuff
```

Namespace `FishStuff` contains a single function, also declared as a Public method.
```apl
:Namespace FishStuff
    ∇ R←Swim
      :Access Public Instance
      R←'Swim, Swim ...'
    ∇
:EndNamespace ⍝ FishStuff
 
      Pingo←⎕NEW Penguin
      Pingo.Swim
Swim, Swim ...
      Pingo.Lay
Lay, Lay ...
      Pingo.Fly 
Fly, Fly ...
```

This is getting silly - we all know that Penguin's can't fly. This problem is simply resolved by overriding the `BirdStuff.Fly` method with `Penguin.Fly`. We can hide `BirdStuff.Fly` with a Private method in `Penguin` that does nothing. For example:
```apl
:Class Penguin: Animal
    :Include BirdStuff
    :Include FishStuff
    ∇ Fly ⍝ Override BirdStuff.Fly
    ∇
:EndClass ⍝ Penguin
 
      Pingo←⎕NEW Penguin  
      Pingo.Fly
VALUE ERROR
      Pingo.Fly
     ^
```

or we can supersede it with a different Public method, as follows:
```apl
:Class Penguin: Animal
    :Include BirdStuff
    :Include FishStuff
    ∇ R←Fly ⍝ Override BirdStuff.Fly
      :Access Public Instance
      R←'Sadly, I cannot fly'
    ∇
:EndClass ⍝ Penguin
```
```apl
      Pingo←⎕NEW Penguin  
      Pingo.Fly
Sadly, I cannot fly
```
