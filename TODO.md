# current TODO:
* add :w, :q, :wq functionality
* add visual selection?
* add click to move cursor to index?
* make file reading better. the program's goal should be to use ASCII if it can, but if it needs more characters in its alphabet, use the minimal alphabet possible to get there

# TODO
create an ncurses window. we have a string for our alphabet + variables for `NEWLINE_CHAR` `NULL_CHAR` `SPACE_CHAR` and `EOF_CHAR`.

we keep track of:
  * height / width of the screen
  * location of the cursor on the screen
  * location of the cursor within our infinitary string
  * index where our EOF character is
  * which indices (corresponds to characters our infinitary string) get removed
    * stack? list?
      * do a stack and limit the size to like, 100, some variable
    * nvm, do characters present - bytearray
      * maybe do index-> byte dictionary. asymptotically I think that's faster than instertions
      * or just do a bytearray, but don't even delete indices, just store them as NULL
        * this is good, this actually helps us track user-added NULL chars

the user can move across the window with arrow keys (TODO: add vim keys). up/down moves down lines on our ncurses display. left/right decrements/increments our index. space increments our index and adds a null character at that position that we keep track of to the previous index. press u and we undo that null character. press space on the same index to toggle that null character. enter/period or smtg places an `EOF_CHAR` -- which acts like it deletes everything that comes after that.

press "enter" to see your poem. brings up another window (or god, wouldn't it be so cool to do it side-by-side, splitscreen?)

:w writes your file. :q quits the editor without writing. :wq writes quit.

## Loose list of commands:
  * vim keys for movement
  * space to toggle deleting a character
  * enter/period or smtg to place an `EOF_CHAR`
  * u to undo a deletion - "pops off" last deletion
  * b to go to the previous index corresponding to the start of an alphabet, w to go to the next
  * : to open up command window
    * :wq, :w, and :q
    * maybe :open if I'm feeling spicy
  * chisel `filename` to use the program itself!
  * ^V to do a visual selection -- then press "space" to do a mass null char insertion/remove
    * ^V doesn't sets everything according to the TOGGLE of the first index that gets selected -- otherwise that's just slow

## notes
MAYBE -- characters that are present are bold, characters that are null are normal font-width and darkened.

should we track characters in our final string instead? this would allow us to open up already existing files, too. it's less data to store than to track *every single null char* the user enters.

a gapbuffer version of this would be really cool to implement, but idk how

my problem is that I don't want to start with an infinite string.
ideas:
  * only track characters before the last null character. anything after that and before our EOF file can be generated using modulus + index.
  * when we open a file, don't keep track of our null characters. render them in our draw function
    * i.e automatically assume everything is null *except* for our specified characters, which we find based on their index in the string/bytearray -> index in the infinitary string
    * when we un-null a character, insert it into our array.
    * if we re-null it, set its value to NONE or 00000000 (null byte)
  * when we create a new file, start with an empty string
    * i want to keep track of whatever is less -- the locations of nulls or our final string -- but I don't know which one is going to be smaller when we start a file.
    * idea: we keep track of *ranges* of null chars. that's so smart. everytime we add a null char we see if we can add it to a range. we just search some dictionary for a null char range that either starts 1 after or ends 1 before its index. we have one dictionary based on starting value keys and one dictionary based on ending key vals? we update both as we go so we can get that sweet sweet O(1) lookup time when we want to find where to add a key.
      * this way, the size of our null char dictionary is proportional to the size of our string
    * when we remove a null char, we search our dictionary for the null char. if it's the start/end of a range, we update it. otherwise we know it's in a range, so we binary search for the maximum null char range that starts before its index. O(log n). we split our ranges in the dictionary which is O(1).
    * but how do we remove a null character from an array? how do we find out if it's in a range?
  * whenever we add/remove a null character we always add it to our history stack tho

summary:
* n = length of our string
* null character representation is O(n) in space -- woo hoo
  * we expect one null character range per every character
* adding a character = removing a null character, which is O(log n)
  * is it the start/end of a null char range? if so, update our dictionary, O(1)
  * if not, we find the range that it falls in, O(log n)
* deleting a character = adding a null character, which is O(1)
  * would it be the start/end of a null char range? if so, update our dictionary, O(1)
  * if not, add a new range to our dictionary, O(1)
* writing out a string is O(n log n)
  * we have to sort our dictionary keys first :(
  * but once sorted, we get all the in-between ranges which we can do in O(n) and write out the index-> character there.

new summary:
* adding a character = removing a null character is O(log n)
* deleting a character = adding a null character AND sorting its key is O(log n)
* writing out a string is O(n)
* ^which is actually the same costs of a balanced binary tree

comparison (character array representation):
* adding a character is O(n)
* deleting a character is O(n)
* writing string is O(n)
^ so we beat that! hell yeah B)

* idea: use some deterministic O(1) hash function that hashes indices to letters. and hell, maybe add in a seed, too, that's determined at the start? the function does not have to be periodic but it should always be 100% probability that you'll see a specific character as time goes on. that might look really cool, lol, and you'd have to search a little for your characters
  * you can make more frequently used characters show up more often
* idea: no undo button. you can't undo chiseling a statue, you shouldn't be able to undo something like this. you can only delete.
