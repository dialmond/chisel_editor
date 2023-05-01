# `chisel_editor`
a vim-like text editor to sculpt text

## what is it?
my french course offered a poetry workshop taught by this Quebecois poet. through zoning out (I was tired, ok?) and my mediocre comprehension of the french language, I picked up something like this:

> Poetry is fundamentally differerent from other art forms. When you make a statue, you start with a stone block, everything you can do is there, and it is the artist's job to carve out the statue. But when you write, you start with nothing and you build up into your poem.

so sculpting is a process of removal and writing is a process of addition.

`chisel_editor` reimagines writing as a process of removal. a user starts out with an infinite block of characters, your stone, and can *only* remove characters from it, likening the creation of a poem to that of a statue.

[![asciicast](https://asciinema.org/a/Rz3sq0zmZMHiAQMsJTX4uJJVy.svg)](https://asciinema.org/a/Rz3sq0zmZMHiAQMsJTX4uJJVy)

## how to use it?
* use `./chisel.py <filename>` to edit a file
* navigate with arrow keys + vim keys + b/w + page up/page down + clicking
* press 'space' to chisel away a character. just like with sculpting, you cannot undo something like this
* press '.' to set the max size of your block. again, once set you cannot increase this value, only decrease it
