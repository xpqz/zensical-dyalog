




# <span class="name">Load without Latent Expression</span> <span class="command">)XLOAD \{ws\}</span> {: .heading}



This command causes the named stored workspace to be loaded.  The current active workspace is lost.


`)XLOAD` is identical in effect to [`)LOAD`](load.md) except that `)XLOAD` does **not** cause the expression defined by the latent expression [`⎕LX`]../system-functions/lx) in the saved workspace to be executed.



