import os
import bisect


#binary search a sorted array for the maximum element that is <= value
def binarySearch(array, value):
    return bisect.bisect(array, value) - 1

class NullChars():
    #init with an alphabet and file
    def __init__(self, file, alphabet=None):
        self.alphabet = alphabet
        self.file = file
        self.EOFIndex = -1
        #^start with -1 EOF index, but we need to update this before we convert to text
        #self.sortedKeys, self.rangeDict = ([0], {0: self.EOFIndex})
        #^start with everything nulled out, 0 to infinity
        self.sortedKeys, self.rangeDict = ([], {})
        try:
            with open(self.file, 'r') as f:
                self.fromText(f.read())
        except FileNotFoundError:
            self.fromText('')

    def getSKIndex(self, index):
        return binarySearch(self.sortedKeys, index)

    #insert a null character
    def insert(self, index):
        inDict = self.rangeDict.get(index + 1)
        skIndex = self.getSKIndex(index)

        less_start = less_end = greater_start = greater_end = None
        if skIndex >= 0:
            less_start = self.sortedKeys[skIndex]
            less_end = self.rangeDict[less_start]
            #^less_start <= less_end < index
        if (skIndex + 1) < len(self.sortedKeys):
            greater_start = self.sortedKeys[skIndex +1]
            greater_end = self.rangeDict[greater_start]
            #^index < greater_start <= greater_end

        #case 0: we're inserting something that's already null
        if (self.EOFIndex != -1 and index >= self.EOFIndex
            or (not less_start is None and (less_end == -1 or less_end >= index))):
            pass
        #case 1: (ls,le), (gs,ge) -> (ls, ge)
        elif less_end and greater_start and less_end == greater_start - 2:
            self.rangeDict[less_start] = greater_end
            del self.sortedKeys[skIndex + 1]
            del self.rangeDict[greater_start]
        #case 2: (ls, le) -> (ls, le + 1)
        elif not less_end is None and less_end == index-1:
            self.rangeDict[less_start] = index
        #case 3: (gs, ge) -> (gs, ge+1)
        elif greater_end and greater_end == index-1:
            self.rangeDict[greater_start] = index
        #case 4: (gs,ge) -> (gs-1, ge)
        elif greater_start and greater_start == index + 1:
            del self.rangeDict[greater_start]
            del self.sortedKeys[skIndex + 1]
            self.sortedKeys.insert(skIndex + 1, index)
            self.rangeDict[index] = greater_end
        #case 5: (ls,le) -> (ls-1, le)
        elif not less_start is None and less_start == index + 1:
            del self.rangeDict[less_start]
            del self.sortedKeys[skIndex + 1]
            self.sortedKeys.insert(skIndex + 1, index)
            self.rangeDict[index] = less_end
        #case 6: not a part of any range, insert (index,index)
        else:
            self.sortedKeys.insert(skIndex + 1, index)
            #case 6.b: greatest index, insert (index, infinity)
            #if not greater_end and not less_start is None:
            #    self.rangeDict[index] = index
            #    self.rangeDict[less_start] = index-1
            #else:
            self.rangeDict[index] = index


    #un-null / remove a null character
    def remove(self, index):
        inDict = self.rangeDict.get(index)
        skIndex = self.getSKIndex(index)

        start = self.sortedKeys[skIndex]
        end = self.rangeDict[start]
        #^index \in [start,end]

        #easy case 1: our index is the start of a null range
        if not inDict is None:
            #easy case 1.b: (start,end) = (i,i)
            if start == end:
                del self.sortedKeys[skIndex]
                del self.rangeDict[index]
                #^remove it from sortedKeys and rangeDict
            else:
                self.sortedKeys[skIndex] = index + 1
                del self.rangeDict[index]
                self.rangeDict[index+1] = end
                #^change the starting index
        else:
            #easy case 2.a: it's the end value of range
            self.rangeDict[start] = index-1
            #^change the ending index

            #case 3: we need to split a range
            if not end == index:
                self.rangeDict[index+1] = end
                self.sortedKeys.insert(skIndex+1, index+1)
                #^change (s,e) -> (s,i-1), (i+1, e)
    #TODO: because we only insert into sortedKeys at the next index, there might
    #be some way for me to save time by using a linked list? my only concern is
    #that we also have to binary search that list, however.

    #convert nullchars to text
    def indexToCharacter(self,i):
        return self.alphabet[i % len(self.alphabet)]

    #convert text to a given NullChar array
    def fromText(self, fileString):
        #get the characters index in our alphabet string, add it to c_i|A|
        def characterIndexToIndex(c_i, c):
            try:
                return self.alphabet.index(c) + len(self.alphabet) * c_i
            except:
                raise Exception("alphabet not sufficient", c)

        fileString = fileString.rstrip()
        if len(fileString) < 1:
            self.alphabet = ('abcdefghijklmnopqrstuvwxyz \n'
                             if self.alphabet is None else self.alphabet)
            return None

        if self.alphabet is None:
            alphabet = set()
            for c in fileString:
                alphabet.add(c)
            self.alphabet = sorted(list(alphabet))

        self.sortedKeys = [0]
        self.rangeDict = {0:-1}
        for c_i in range(len(fileString)):
            self.remove(characterIndexToIndex(c_i, fileString[c_i]))
        self.EOFIndex = characterIndexToIndex(c_i, fileString[c_i])+1

    #write current data to file
    def write(self, index):
        if self.EOFIndex == -1:
            raise Exception('must place down an EOF character before writing')
        output = ''
        for c in NullCharsIterator(self):
            output += c
        with open(self.file, 'w') as f:
            f.write(output)

class NullCharsIterator:
    def __init__(self, nullchars, endIndex = None):
        self.nullchars = nullchars
        if endIndex is None:
            endIndex = self.nullchars.EOFIndex
        if self.nullchars.EOFIndex != -1:
            self.endIndex = min(endIndex, self.nullchars.EOFIndex)
        else:
            self.endIndex = -1
        self.index = self.ncIndex = 0
        self.sortedKeyLength = len(self.nullchars.sortedKeys)
        if self.ncIndex < self.sortedKeyLength:
            self.start = self.nullchars.sortedKeys[self.ncIndex]
            self.end = self.nullchars.rangeDict[self.start]
        else:
            self.start, self.end = (None, None)

    def __iter__(self):
        return self

    def __next__(self):
        character =  self.nullchars.indexToCharacter(self.index)
        if ((self.endIndex != -1 and self.index >= self.endIndex)
            or self.end == -1):
            raise StopIteration
        if ((not self.start is None and self.index < self.start)
            or self.start is None):
            self.index += 1
            return character
        #so now we must have self.index > self.start, skip to end
        if not self.end is None:
            self.index = self.end + 1
        self.ncIndex += 1
        #this is our next (s,e) of null characters
        if self.ncIndex < self.sortedKeyLength:
            self.start = self.nullchars.sortedKeys[self.ncIndex]
            self.end = self.nullchars.rangeDict[self.start]
        else:
            self.start, self.end = (None, None)
        character = self.nullchars.indexToCharacter(self.index)
        self.index += 1
        return character
