from LinkedList import LinkedList
import numpy as np

class Trie:
    class Reference:
        def __init__(self, data):
            self.data = data

    class Node:
        def __init__(self, letter="", children=LinkedList(), is_end=False):
            self.letter = letter
            self.children = children
            self.is_end = is_end
    
    def __init__(self, sequences=set()):
        self.root = self.Node("", LinkedList())
        self.word_count = 0
        self.end_to_index = dict() 
        for sequence in sequences:
            self.append(sequence)

    #Query

    def __len__(self)->int:
        return self.word_count
    
    #Recursive helper of `depth_counts`
    def __depth_counts(self, root: Node, 
                       curr_freq: Reference = Reference(0),
                       depth: int = 0, depth_to_count: list = [])->list:
        #Add to the root frequency with the frequencies of its children
        root_frequency = 0
        #Recurse on each of `root`'s children down to the last node
        # while updating the depth count list
        for node in root.children:
            child = node.get()
            #Add to the size of the depth count list when necessary
            if depth == len(depth_to_count):
                depth_to_count.append(0)
            #Recurse on the child with an incremented depth
            self.__depth_counts(child, curr_freq, 
                                depth+1, depth_to_count)
            #Add to the frequency with the current child's frequency
            # if it is a word end
            if child.is_end:
                curr_freq.data += len(self.end_to_index[child])
            #Add to the count for this depth
            depth_to_count[depth] += curr_freq.data
            #Append the current frequency to `frequencies`
            root_frequency += curr_freq.data
        #Set the current frequency to the root frequency
        # so that the previous call and gets the right frequency
        curr_freq.data = root_frequency
        return depth_to_count
    
    #Generate a list maping depth to the numnber of letters there
    def depth_counts(self)->list: 
        return self.__depth_counts(
            self.root, self.Reference(0), 0, []
        )

    #Search/Traversal

    def __contains__(self, word: str, instance: int = 0)->bool:
        #Going down the Trie and checking for matches
        # until the full word is found using a 
        # child-node-searching algorithm
        parent = self.root
        children = parent.children
        for letter in word:
            #Iterating through the children 
            #and checking for a match
            found = False
            child = None
            for node in children:
                child = node.get()
                if child.letter != letter:
                    continue
                found = True
                break
            #If no matching child was found, stop
            if not found:
                break
            #Advance the parent and children
            parent = child
            children = parent.children
        #Check that it has as many instances as required
        return (len(self.end_to_index[parent]) >= instance)
    
    #Get a node at the end of a certain word
    def __get_word_end_node(self, word: str)->Node:
        #Going down the Trie and checking letters 
        # until the full word is found using a 
        # child-node-searching algorithm
        parent = self.root
        children = parent.children
        for letter in word:
            #Iterating through the children 
            #and checking for a match
            found = False
            child = None
            for node in children:
                child = node.get()
                if child.letter != letter:
                    continue
                found = True
                break
            #Break if no match is found
            if not found:
                break
            #Advance the parent and children
            parent = child
            children = parent.children
        return parent

    #Build strings by visiting every node beyond a certain node
    def __subtree(self, root: Node, word: str = "", result_list: list = [])->list:
        #Append the result and return if it is a leaf node
        if not len(root.children):
            result_list.append(word)
            return result_list
        #Otherwise recurse on each of its children down to the last node
        for node in root.children:
            child = node.get()
            #Recurse on the child with the word
            # extended by the child's letter
            self.__subtree(child, word+child.letter, result_list)
        return result_list
    
    def unique(self)->list:
        return self.__subtree(self.root, "", [])

    #Recursive helper of `popular`
    def __popular(self, root: Node, 
                  word: str = "",
                  max_occurrences: Reference = Reference(0), 
                  max_word: Reference = Reference(""))->list:
        #If the rooot is a word end and that word 
        # occurs with more or the same frequency than the others,
        # assign `max_word` to it and `max_occurrences` to its occurrence count
        if root.is_end:
            occurrences = len(self.end_to_index[root])
            if occurrences >= max_occurrences.data:
                max_occurrences.data = occurrences
                max_word.data = word
        #Recurse on each of its children down to the last node 
        # to search for a more popular word
        for node in root.children:
            child = node.get()
            #Recurse on the child with the word
            # extended by the child's letter
            self.__popular(
                child, word+child.letter, 
                max_occurrences, max_word
            )
        return max_word.data

    def popular(self):
        return self.__popular(
            self.root, "", 
            self.Reference(0), 
            self.Reference("")
        )

    #Get the complete strings of all branches to which 
    # a word lies on or could extend to
    def nearest(self, word: str, min_matches=1)->str:
        base_str = ""
        matches = 0
        #Going down the Trie and checking for matches 
        # using a child-node-searching algorithm.
        parent = self.root
        children = parent.children
        for letter in word:
            #Iterating through the children 
            #and checking for a match
            found = False
            child = None
            for node in children:
                child = node.get()
                if child.letter != letter:
                    continue
                found = True
                break
            #If no matching node was found, stop
            if not found:
                break
            #Add to the result and match count
            base_str += letter
            matches += 1
            #Advance the parent and children
            parent = child
            children = parent.children
        #If the last match wasn't a leaf 
        # and there aren't enough matches, return an empty list
        if len(parent.children) and matches < min_matches:
            return ""
        #Otherwise, return a list of all permutations
        # stemming from the last match
        return self.__popular(
            parent, base_str, 
            self.Reference(0), self.Reference("")
        )
    
    #Modification

    #Add a word to the Trie while tracking letter frequencies
    def append(self, word: str):
        #Going down the Trie and appending letters as needed using a 
        # child-node-searching algorithm
        parent = self.root
        children = parent.children
        for letter in word:
            #If none of the letters of the current children 
            # are a match to the current letter, 
            # insert the letter as a new node
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
                child = self.Node(letter, LinkedList())
                parent.children.append(child)
            #Advance the parent and children
            parent = child
            children = parent.children
        #Update word end to index list dictionary
        if not parent.is_end:
            self.end_to_index[parent] = [self.word_count]
            parent.is_end = True
        else:
            self.end_to_index[parent].append(self.word_count)
        #Update word count
        self.word_count += 1

    #Go to every index greater a deleted one and decrement it
    def __reindex(self, deleted_index: int):
        for _, indicies in self.end_to_index.items():
            for i in range(len(indicies)):
                if indicies[i] < deleted_index:
                    continue
                indicies[i] -= 1

    #Delete a word from the Trie
    def delete(self, word: str, prefix: str = "", instance: int = 0)->bool:
        prefix_end = self.__get_word_end_node(prefix)
        #Stop if the word isn't in the Trie
        if prefix_end == None:
            return False
        #Going down the Trie and checking for matches 
        # using a child-node-searching algorithm.
        parent = prefix_end
        children = parent.children
        first_letter_node = None
        for letter in word:
            #Iterating through the children 
            #and checking for a match
            found = False
            child = None
            _node = None
            for node in children:
                _node = node
                child = node.get()
                if child.letter != letter:
                    continue
                found = True
                break
            #If no matching node was found, return
            if not found:
                return False
            #If the child is the first letter node of the prefix
            # set the first letter node
            if children is prefix_end.children:
                first_letter_node = _node
            #Otherwise, if  it is a node with 2+ children,
            # move the prefix end to it
            if len(child.children) > 1:
                prefix_end = child
            #Advance the parent and children
            parent = child
            children = parent.children
        #Stop if the parent isn't an end node
        if not parent.is_end:
            return False
        #Delete the apropriate index from 
        # the word end to index list dict
        indicies = self.end_to_index[parent]
        #Return if there is no nth instance of the word
        if len(indicies) < instance:
            return False
        #Otherwise, delete the instance
        deleted_index = indicies[instance - 1]
        indicies.pop(instance - 1)
        #Remove the word end from the word end to indicies
        # dict and detach the word from the prefix node
        # if that was the only instance of it
        if not len(indicies):
            self.end_to_index.pop(parent)
            #Detach only if the parent has no children
            if not len(parent.children):
                prefix_end.children.pop(first_letter_node)
        #Update all the index lists
        self.__reindex(deleted_index)
        #Decrement word count
        self.word_count -= 1
        return True
                
    def __prune_all_below(self, root: Node, indicies = []):
        #Recurse down to the last node. 
        #Save any encountered
        # indicies and delete the node
        for node in root.children:
            child = node.get()
            #Recurse on the child
            self.__prune_all_below(child, indicies)
            #Saving indicies
            if child.is_end:
                indicies += self.end_to_index[child]
                #Remove it from the 
                # word end to index list dict since
                # it will be deleted 
                self.end_to_index.pop(child)
            #Deletion
            root.children.pop(node)
        #Return the index list
        return indicies
    
    #Recursive helper of `prune`. Returns how many were deleted
    def __prune(self, depth_to_count: list, 
                root: Node, 
                min_index_count: int, min_bias: float,
                curr_freq: Reference = Reference(0), 
                depth=0)->int:
        #If there are no children
        # set current frequency to 0 because 
        # it must be based on the frequencies of the children.
        #Then return
        if not len(root.children):
            curr_freq.data = 0 
            return
        #Save the frequencies of the children in an array that will be populated
        # during iteration through the children
        frequencies = []
        #Track if any are deleted
        some_deleted = False
        #Recursively iterate over the Trie and populate `frequencies`
        for node in root.children:
            child = node.get()
            #Recurse on the child
            # with an incremented depth
            _some_deleted = self.__prune(
                depth_to_count, child,
                min_index_count, min_bias,
                curr_freq,
                depth+1
            )
            some_deleted = (some_deleted or _some_deleted)
            #Add to the frequency with the current child's frequency
            # if it is a word end
            if child.is_end:
                curr_freq.data += len(self.end_to_index[child])
            #Append the current frequency to `frequencies`
            frequencies.append(curr_freq.data)
        #Check for the validity of each node and delete if it
        # is invalid
        n_children = sum(frequencies)
        base_proportion = 1/len(frequencies)
        min_proportion = base_proportion + min_bias
        if min_proportion > 1:
            min_proportion = 1
        # Track the number of vacated indicies(explained later)
        #  so it can be subtracted from `n_children` later
        num_vacated = 0
        # Track frequency index
        i = 0
        # Iterating and checking/deleting
        for node in root.children:
            child = node.get()
            #Check that the letter count at
            # this depth is acceptable
            valid_depth_count = (depth_to_count[depth] >= min_index_count)
            #If the depth count is invalid,
            # delete all its children,
            # vacate the child's index data to the root 
            #  if its a word end,
            # and then delete the child itself
            if not valid_depth_count:
                child = node.get()
                #Vacate its index data
                # and remove it from the end to indicies dict
                # if its a word end
                if child.is_end:
                    #Increment `num_vacated`
                    num_vacated += 1
                    #Vacating. Only vacate if the 
                    # root isn't the Trie root
                    if not root is self.root:
                        indicies = self.end_to_index[child]
                        if not root.is_end:
                            self.end_to_index[root] = indicies
                            root.is_end = True
                        else:
                            self.end_to_index[root] += indicies
                    #Deletion from the word end to index list dict
                    self.end_to_index.pop(child)
                #Remove it from the children
                root.children.pop(node)
                #Update deletion flag
                some_deleted = True
                #Incrememnt i and continue
                i += 1 
                continue
            #Check that
            # this letter's frequency relative to the other 
            # children is acceptable
            valid_frequency = (frequencies[i]/n_children >= min_proportion)
            #If the frequency is invalid, 
            # delete the child and all below it.
            #Take all the indicies that were in the lower nodes and give it
            # to the root
            if not valid_frequency:
                #Deleting all below the child
                indicies = self.__prune_all_below(child, [])
                #Add the number
                #If the child is a word end,
                # add its indicies to `indicies` 
                # and delete it from the word end to index list dict
                if child.is_end:
                    indicies += self.end_to_index[child]
                    self.end_to_index.pop(child)
                #Add to `num_vacated`
                num_vacated += len(indicies)
                #Saving the indicies in the root
                if len(indicies) and not root is self.root:
                    if not root.is_end:
                        self.end_to_index[root] = indicies
                        root.is_end = True
                    else:
                        self.end_to_index[root] += indicies
                #Deleting the child
                root.children.pop(node)
                #Update the deletion flag
                some_deleted = True
            #Increment i
            i += 1
        #Subtract out the number of vacations
        n_children -= num_vacated
        #Set the current frequency to `n_children`
        # so that the previous call gets the right frequency
        curr_freq.data = n_children
        return some_deleted
    
    #Rebuild the word end to index list dict
    def rebuild_index(self):
        #Tuple like class with a less than comparator
        # for less than comparison
        class Tuple:
            def __init__(self, data=[]):
                self.data = data

            def __lt__(self, other)->bool:
                return self.data[0] < other.data[0]
            
            def __iter__(self):
                return self.data.__iter__()
            
            def __next__(self):
                return self.data.__next__()
            
        #Gather all indicies, pointers 
        # to the letter they are mapped to,
        # and indicies of where in their list they appaer
        # into a list
        indicies_and_data = []
        for end_node, indicies in self.end_to_index.items():
            for i in range(len(indicies)):
                to_append = Tuple([indicies[i], end_node, i])
                indicies_and_data.append(to_append)
        #Update word count
        self.word_count = len(indicies_and_data)
        #Sort the list
        indicies_and_data = np.sort(indicies_and_data)
        #Replace the indices associated with each end node
        # with the appropriate indicies
        for i in range(len(indicies_and_data)):
            _, end_node, list_index = indicies_and_data[i]
            self.end_to_index[end_node][list_index] = i
        
    #Prune the tree of depths with too few letters
    # and letters that don't appear frequently 
    # enough among the children of their parent letters.
    def prune(self, min_index_vote: float, min_bias: float = 0):
        depth_counts = self.depth_counts()
        some_deleted = self.__prune(
            depth_counts, self.root, 
            min_index_vote*self.word_count, min_bias,
            self.Reference(0), 0
        )
        #Rebuild the index after all the pruning
        # if any were deleted
        if some_deleted:
            self.rebuild_index()

    #Recursive helper of `decompress`
    def __decompress(self, root: Node, 
                     word: str = "", result_list: list = [])->list:
        #If it is a word end node, 
        # place the result in the list 
        # at the appropriate indexes
        if root.is_end:
            for index in self.end_to_index[root]:
                result_list[index] = word
        #Recurse on each of its children down to the last node
        for node in root.children:
            child = node.get()
            #Recurse on the child with the word extended by the child's letter
            self.__decompress(child, word+child.letter, result_list)
        return result_list

    #Get all the words out of the tree
    def decompress(self)->list:
        words = ["" for _ in range(self.word_count)]
        self.__decompress(self.root, "", words)
        return words
