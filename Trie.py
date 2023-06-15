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
            #Returning when
            # there are no more nodes to traverse
            if not len(children):
                return False
            #Iterating through the children 
            #and checking for matches otherwise
            for node in children:
                child = node.get()
                if child.letter != letter:
                    continue
                #When a match happens, stop iterating 
                # and advance the parent and children pointers down
                # the Trie
                parent = child
                children = parent.children
                break
            #Increment index
            index += 1
        return True
    
    #Get the full branch with which a word has any matches
    def nearest(self, word: str)->bool:
        result = ""
        #Going down the Trie and checking for matches 
        # using a breadth-first-search-like algorithm
        parent = self.root
        children = parent.children
        for letter in word:
            #Returning when
            # there are no more nodes to traverse
            if not len(children):
                return result
            #Iterating through the children 
            #and checking for matches otherwise
            found = False
            for node in children:
                child = node.get()
                if child.letter != letter:
                    continue
                #When a match happens, stop iterating 
                # and advance the parent and children pointers down
                # the Trie
                found = True
                parent = child
                children = parent.children
                break
            #If no matching node was found, stop
            if not found:
                break
            #Add to the result
            result += letter
        #Return if all letters were found
        if len(result) == len(word):
            return result
        #Go down the rest of the branch based on 
        # the rightmost most popular children
        while len(children):
            #Select the most poular child
            popular = self.root
            for node in children:
                child = node.get()
                if child.frequency < popular.frequency:
                    continue
                popular = child
            #Advance the parent and children on the popular path
            parent = popular
            children = parent.children
            #Add to the result
            result += parent.letter
        return result

    def match_count(self, word: str)->int:
        match_count = 0
        #Going down the Trie and ytacking matches 
        # until the full word is found using a 
        # breadth-first-search-like algorithm
        parent = self.root
        children = parent.children
        for letter in word:
            #Returning when
            # there are no more nodes to traverse
            if not len(children):
                return match_count
            #Iterating through the children 
            #and tracking matches otherwise
            for node in children:
                child = node.get()
                if child.letter != letter:
                    continue
                #When a match happens, increment the match count,
                # stop iterating,
                # and advance the parent and children pointers down
                # the Trie
                match_count += 1
                parent = child
                children = parent.children
                break
        return match_count
    
    #Add a word to the Trie while tracking letter frequencies
    def append(self, word: str):
        #Going down the Trie and appending letters as needed using a 
        # breadth-first-search-like algorithm
        parent = self.root
        children = parent.children
        for letter in word:
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
            #Increment letter count
            self.letter_count += 1
    
    #Get a node at the end of a certain word
    def __get_word_end_node(self, word: str)->Node:
        result = self.root
        #Going down the Trie and checking letters 
        # until the full word is found using a 
        # breadth-first-search-like algorithm
        parent = self.root
        children = parent.children
        for letter in word:
            #Returning when
            # there are no more nodes to traverse
            if not len(children):
                result = None
                break
            #Iterating through the children 
            #and checking for matches otherwise
            for node in children:
                child = node.get()
                if child.letter != letter:
                    continue
                #When a match happens, 
                # set the result to the matching node,
                # stop iterating,
                # and advance the parent and children pointers down
                # the Trie
                result = child
                parent = child
                children = parent.children
                break
        return result

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
        for letter in word:
            #No more nodes to traverse means it could not be found, so simply return
            if not len(children):
                return False
            #Going down the Trie and updating frequencies otherwise
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
        
    #Check if the depth's letter count is sufficient  
    # and the proportion of the node's letter 
    # among the the children of its parent is large enough
    def __valid(self, child: Node, root: Node,
                depth_to_count, depth, 
                min_letters, branch_fraction):
        #Get the number of letters at this depth
        depth_total = depth_to_count[depth]
        #Get the proportion of this letter 
        # out of all letters in this set of children
        proportion = child.frequency/len(root.children)
        #Check that both meet the requirements
        if depth_total >= min_letters \
        and proportion >= branch_fraction:
            return True
        return False

    #Recursive helper of `prune` with no prefix protection
    def __prune_no_protect(self, depth_to_count: list, 
                           root: Node, 
                           min_letters: int, branch_fraction: float, 
                           depth=0):
        #Recursively iterate over the Trie and 
        # delete words/letters that 
        # don't appear frequently enough
        for node in root.children:
            child = node.get()
            self.__prune_no_protect(
                depth_to_count, child, 
                min_letters, branch_fraction,
                depth+1
            )
            #If the node is invalid,
            # subtract out its frequency 
            # and delete it
            if not self.__valid(child, root,
                                depth_to_count, depth,
                                min_letters, branch_fraction):
                self.letter_count -= root.frequency
                root.children.pop(node)

    #Recursive helper of `prune` with prefix protection
    def __prune_prefix_protect(self, depth_to_count: dict, 
                               root: Node, 
                               min_letters: int, branch_fraction: float, 
                               depth=0):
        #Recursively iterate over the Trie and 
        # delete words/letters that 
        # don't appear frequently enough and aren't prefixes
        for node in root.children:
            child = node.get()
            self.__prune_prefix_protect(
                depth_to_count, child, 
                min_letters, branch_fraction,
                depth+1
            )
            #The child must not have children and must be invalid to
            # be deleted. This protects prefixes.
            #If the child is invalid,
            # subtract out its frequency from the total letter count
            # and delete it
            if not len(child.children) \
            and not self.__valid(child, root, 
                                depth_to_count, depth,
                                min_letters, branch_fraction):
                self.letter_count -= child.frequency
                root.children.pop(node)
    
    #Recursive helper of `depth_counts`
    def __depth_counts(self, root: Node, 
                       depth = 0, depth_to_count=[])->list:
        #Update the depth to count list
        # and recurse on each of `root`'s children down to the last node
        for node in root.children:
            child = node.get()
            #Add the visited letter to the depth count
            if depth == len(depth_to_count):
                depth_to_count.append(child.frequency)
            else:
                depth_to_count[depth] += child.frequency
            self.__depth_counts(child, depth+1, depth_to_count)
        return depth_to_count
    
    #Generate a list maping depth to the numnber of letters there
    def depth_counts(self)->list: 
        return self.__depth_counts(self.root)
        
    #Prune the tree of letters that are part of depths that have too few letters
    # and letters at those depths that don't appear frequently enough.
    def prune(self, min_letters: int, 
              branch_fraction: float, protect_prefixes: bool = True):
        if protect_prefixes:
            self.__prune_prefix_protect(
                self.depth_counts(), self.root, 
                min_letters, branch_fraction
            )
        else:
            self.__prune_no_protect(
                self.depth_counts(), self.root, 
                min_letters, branch_fraction
            )

    #Recursive helper of `decompress`
    def __decompress(self, root: Node, 
                     result_list: list = [], word: str = "")->list:
        #Decrement frequency
        if root.frequency:
            root.frequency -= 1
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
            if root.frequency:
                root.frequency -= 1
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
