from LinkedList import LinkedList

class Trie:
    class Node:
        def __init__(self, letter="", children=LinkedList(), frequency=1):
            self.letter = letter
            self.children = children
            self.frequency = frequency
    
    def __init__(self, sequences=set()):
        self.root = self.Node("", LinkedList(), 0)
        self.letter_count = 0
        for sequence in sequences:
            self.append(sequence)

    def __contains__(self, word: str)->bool:
        #Going down the Trie and checking letters 
        # until the full word is found using a 
        # breadth-first-search-like algorithm
        parent = self.root
        children = parent.children
        index = 0
        while index < len(word):
            letter = word[index]
            #Adding the letter as a child node when 
            # there are no more nodes to traverse
            if not len(children):
                return False
            #Going down the Trie and updating frequencies otherwise
            for node in children:
                child = node.get()
                if child.letter != letter:
                    continue
                parent = child
                children = parent.children
                break
            #Increment index
            index += 1
        return True
    
    #Recursive helper of `tree_report`
    def __tree_report(self, root: Node, 
                      depth = 0, letter_to_depth_to_freq=dict())->dict:
        #Add the visited letter to the dictionary
        if root.letter not in letter_to_depth_to_freq:
            letter_to_depth_to_freq[root.letter] = {depth: root.frequency}
        elif depth not in letter_to_depth_to_freq[root.letter]:
            letter_to_depth_to_freq[root.letter][depth] = root.frequency
        else:
            letter_to_depth_to_freq[root.letter][depth] += root.frequency
        #Then recurse on each of its children down to the last node
        for node in root.children:
            child = node.get()
            self.__tree_report(child, depth+1, letter_to_depth_to_freq)
        return letter_to_depth_to_freq
    
    #Generate a dict maping letters to dicts mapping each depth leval 
    # of the tree to the number of occurrences of that letter
    def tree_report(self)->dict: 
        return self.__tree_report(self.root)
    
    #Get a node at the end of a certain word
    def __get_word_end_node(self, prefix: str)->Node:
        result = self.root
        #Going down the Trie and checking letters 
        # until the full word is found using a 
        # breadth-first-search-like algorithm
        parent = self.root
        children = parent.children
        index = 0
        while index < len(prefix):
            letter = prefix[index]
            #Adding the letter as a child node when 
            # there are no more nodes to traverse
            if not len(children):
                result = None
                break
            #Going down the Trie and updating frequencies otherwise
            for node in children:
                child = node.get()
                if child.letter != letter:
                    continue
                result = child
                parent = child
                children = parent.children
                break
            #Increment index
            index += 1
        return result
    
    #Add a word to the Trie while tracking letter frequencies
    def append(self, word: str):
        #Going down the Trie and appending letters as needed using a 
        # breadth-first-search-like algorithm
        parent = self.root
        children = parent.children
        index = 0
        while index < len(word):
            letter = word[index]
            #Going down the Trie and 
            # incrementing the frequency of the letter if it is found.
            #If none of the letters of the current children are right, 
            # insert the new letter
            found = False
            child = None
            for node in children:
                child = node.get()
                if child.letter != letter:
                    continue
                found = True
                break
            #Adding the letter as a child node when 
            # there are no more nodes to traverse
            if not found:
                child = self.Node(letter, LinkedList(), 0)
                parent.children.append(child)
            #Increment the child's frequency
            # and advance the parent and children
            child.frequency += 1
            parent = child
            children = parent.children
            #Increment letter count and index
            self.letter_count += 1
            index += 1
    
    #Delete a word from the Trie starting from the end of a choosen prefix.
    #We can only delete when
    # 1. There is an unbroken sequence of 0-frequency nodes
    # (after subtracting from their frequencies)
    # down to the bottom starting from the prefix end
    # 2. When there is some chain of 0-frequencies 
    # and we arent protecting prefixes
    def delete(self, word: str, prefix: str = "", protect_prefixes=True)->bool:
        #Going down the Trie and decrementing/deleting letters 
        # as needed using a breadth-first-search-like algorithm
        #First get the node at the end of the prefix
        prefix_end = self.__get_word_end_node(prefix)
        if prefix == None:
            return False
        #Search for the letters while moving the prefix end to the last
        # non-zero node after a subtract
        parent = prefix_end
        children = parent.children
        index = 0
        while index < len(word):
            letter = word[index]
            #No more nodes to traverse means it could not be found, so simply return
            if not len(children):
                return False
            #Going down the Trie and updating frequencies/deleting otherwise
            for node in children:
                child = node.get()
                if child.letter != letter:
                    continue
                #Subtract from frequency if it is 
                # on the path to the end of the word
                if child.frequency:
                    child.frequency -= 1
                    self.letter_count -= 1
                    #Move the prefix end to the parent if the child node
                    # still has frequency
                    if child.frequency:
                        prefix_end = parent
                #Aadvance the parent and children
                parent = child
                children = parent.children
                break
            #Increment index
            index += 1
        #Delete all from the prefix node down to the bottom of the Trie
        # if the last non-zero node isn't a leaf node and either
        # we aren't protecting prefixes 
        # or the last 0-frequency node is a leaf(the 0-frequency nodes go down to the bottom).
        if len(prefix_end.children) \
        and (not protect_prefixes or not len(parent.children)):
            #Find the first letter node again
            first_child = None #This should be a linked list node
            for node in parent.children:
                child = node.get()
                if child.letter == word[0]:
                    first_child = node
                    break
            #Remove the branch of the prefix end
            prefix_end.children.pop(first_child)
        return True
    
    #Calculate the total number of letters at a depth level
    def __depth_total(letter_to_depth_to_freq, depth):
        depth_total = 0
        for letter in letter_to_depth_to_freq:
            depth_to_freq = letter_to_depth_to_freq[letter]
            if depth in depth_to_freq:
                depth_total += depth_to_freq[depth]
        return depth_total
        
    
    #Recursive helper of `prune` with no prefix protection
    def __prune_no_protect(self, letter_to_depth_to_freq: dict, 
                           root: Node, min_letters: int, 
                           min_depth_fraction: float, 
                           depth=0):
        #If the depth's count is too low or 
        # current node's depth proportion is too low,
        # remove and subtract out its frequency
        depth_total = Trie.__depth_total(letter_to_depth_to_freq, depth)
        if depth_total < min_letters \
        or root.frequency/depth_total < min_depth_fraction:
            self.letter_count -= root.frequency
            root.frequency = 0
        #Free memory
        del depth_total
        #Recursively iterate over the Trie and 
        # delete words/letters that 
        # don't appear frequently enough
        for node in root.children:
            child = node.get()
            self.__prune_no_protect(
                letter_to_depth_to_freq, child, 
                min_letters, min_depth_fraction,
                depth+1
            )
            #If the child's frequency was too low, 
            # it would have been set to 0. 
            #So if it isn't 0, continue
            if child.frequency > 0:
                continue
            #Otherwise, delete the child
            root.children.pop(node)

    #Recursive helper of `prune` with prefix protection
    def __prune_prefix_protect(self, letter_to_depth_to_freq: dict, 
                               root: Node, min_letters: int, 
                               min_depth_fraction: float, 
                               depth=0):
        #If the depth's count is too low or 
        # current node's depth proportion is too low,
        # mark it by making its frequency negative
        depth_total = Trie.__depth_total(letter_to_depth_to_freq, depth)
        if depth_total < min_letters \
        or root.frequency/depth_total < min_depth_fraction:
            root.frequency *= -1
        #Free memory
        del depth_total
        #Recursively iterate over the Trie and 
        # delete words/letters that 
        # don't appear frequently enough and aren't prefixes
        for node in root.children:
            child = node.get()
            self.__prune_prefix_protect(
                letter_to_depth_to_freq, child, 
                min_letters, min_depth_fraction,
                depth+1
            )
            #If the child's frequency was too low, 
            # it would have been set to a negative value. 
            #So if it isn't negative, continue
            if child.frequency >= 0:
                continue
            #Otherwise:
            # Revert the frequency
            child.frequency = abs(child.frequency)
            # If the child has no children or we aren't protecting prefixes,
            # subtract out its frequency from the total letter count
            # and delete it since it is not a prefix
            if not len(child.children):
                self.letter_count -= child.frequency
                root.children.pop(node)
        
    #Prune the tree of letters that are part of depths that have too few letters
    # and letters at those depths that don't appear frequently enough.
    def prune(self, min_letters: int, 
              min_depth_fraction: float, protect_prefixes: bool = True):
        if protect_prefixes:
            self.__prune_prefix_protect(
                self.tree_report(), self.root, 
                min_letters, min_depth_fraction
            )
        else:
            self.__prune_no_protect(
                self.tree_report(), self.root, 
                min_letters, min_depth_fraction
            )

    #Recursive helper of `decompress`
    def __decompress(self, root: Node, 
                     result_list: list = [], word: str = "")->list:
        #Decrement frequency
        def decrement_freq():
            root.frequency -= 1
        def decrement_no_freq():
            pass
        decrement = decrement_freq if root.frequency else decrement_no_freq
        decrement()
        #Append the result and return if it is a leaf node
        # and it still has a frequency
        if not len(root.children):
            result_list.append(word)
            return result_list
        #Otherwise recurse on each of its children down to the last node
        for node in root.children:
            #Extract a word from the letters
            child = node.get()
            #Decrement root frequency
            # for each child node traversed from it
            decrement()
            #Recurse on the child
            self.__decompress(child, result_list, word+child.letter)
            #Having the condition of no children before deletion
            # ensures prefix safety until the end
            if not child.frequency and not len(child.children):
                root.children.pop(node)
        return result_list

    #Get all the words out of the tree while emptying it
    def decompress(self)->list:
        words = list()
        while len(self.root.children):
            self.__decompress(self.root, words)
        self.letter_count = 0
        return words
