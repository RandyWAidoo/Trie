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
    
    def delete(self, word: str, prefix: str = "")->bool:
        #Going down the Trie and decrementing/deleting letters 
        # as needed using a breadth-first-search-like algorithm
        #First get the node at the end of the prefix
        prefix_end = self.__get_word_end_node(prefix)
        if prefix == None:
            return False
        #Search for the letters
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
                parent = child
                children = parent.children
                break
            #Increment index
            index += 1
        #Delete all from the prefix node down to the end of the word
        # if the last node of the word is a leaf node
        if not len(parent.children):
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
    
    def __discriminate(self, root: Node, min_count: float):
        #If the current node's frequency is too low,
        # make its frequency negative(it is safe for the zero case as well)
        if root.frequency < min_count:
            root.frequency *= -1
        #Recurseively iterate over the Trie and 
        # delete words/letters that 
        # don't appear frequently enough andd aren't prefixes
        for node in root.children:
            child = node.get()
            self.__discriminate(child, min_count)
            #If the child's frequency was too low, 
            # it would have been set to a negative value. 
            #So if it isn't negative, continue
            if child.frequency >= 0:
                continue
            #Otherwise:
            # If the child has no children, 
            #  delete it since it is not a prefix
            if not len(child.children):
                #Make the frequency positive and subtract it from the letter count
                child.frequency *= -1
                self.letter_count -= child.frequency 
                #Deletion
                root.children.pop(node)
            # Otherwise restore its frequency
            else:
                child.frequency *= -1
        
    def discriminate(self, min_frequency: float):
        min_count = min_frequency/100*self.letter_count
        self.__discriminate(self.root, min_count)

    def __decompress(self, root: Node, result_list: list = [], word: str = "")->list:
        #Recurseively add every new string to the list.
        #New strings are found when a leaf node is found.
        #This process empties the Trie
        #Decrement frequency and letter count
        if root.frequency:
            root.frequency -= 1
            self.letter_count -= 1
        #Append the result and return if it is a leaf node
        if not len(root.children):
            result_list.append(word)
            return result_list
        #Otherwise recurse on each of its children down to the last node
        for node in root.children:
            #Extract a word from the letters
            child = node.get()
            self.__decompress(child, result_list, word+child.letter)
            #Having the condition of no children before deletion
            # ensures prefix safety until the end
            if not child.frequency and not len(child.children):
                root.children.pop(node)
            else:
                pass
        return result_list

    def decompress(self)->list:
        words = list()
        while self.letter_count:
            self.__decompress(self.root, words)
        return words
