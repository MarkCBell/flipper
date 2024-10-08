
''' A module for representing triangulations along with laminations and mapping classes on them.

Provides one class: EquippedTriangulation. '''

from itertools import product
from random import choice
import multiprocessing
import re

import flipper

def inverse(word):
    ''' Return the inverse of a word by reversing and swapcasing it. '''
    
    return tuple(letter.swapcase() for letter in reversed(word))

def generate_ordering(letters):
    ''' Return a function which determines if v >= w (with respect to the short-lex ordering).
    
    If v or w contains any letter not in letters then returns False. '''
    
    positions = dict((letter, index) for index, letter in enumerate(letters))
    return lambda v, w: all(x in positions for x in v) and \
        all(y in positions for y in w) and \
        [len(v)] + [positions[x] for x in v] >= [len(w)] + [positions[y] for y in w]

##########################################################################
# A helper function  that can be pickled for multiprocessing.
def _worker_thread_word(Q, A):
    while True:
        data = Q.get()
        if data is None: break
        
        surface, length, prefix, options = data
        # We need to rebuild the ordering as this couldn't be passed through the pickle.
        options['order'] = generate_ordering(options['letters'])
        for output in surface._all_words_joined(length, prefix, **options):
            A.put(output)
    A.put(None)

def _worker_thread_mapping_class(Q, A):
    while True:
        data = Q.get()
        if data is None: break
        
        surface, length, prefix, options = data
        # We need to rebuild the ordering as this couldn't be passed through the pickle.
        options['order'] = generate_ordering(options['letters'])
        for output in surface._all_mapping_classes(length, prefix, **options):
            A.put(output)
    A.put(None)


class EquippedTriangulation:
    ''' This represents a triangulation along with a collection of named laminations and mapping classes on it.
    
    Most importantly this object can construct a mapping class from a string descriptor.
    See self.mapping_class for additional information. '''
    def __init__(self, triangulation, laminations, mapping_classes):
        assert isinstance(triangulation, flipper.kernel.Triangulation)
        assert isinstance(laminations, (dict, list, tuple))
        assert isinstance(mapping_classes, (dict, list, tuple))
        
        self.triangulation = triangulation
        if isinstance(laminations, dict):
            assert all(isinstance(key, str) for key in laminations)
            assert all(isinstance(laminations[key], flipper.kernel.Lamination) for key in laminations)
            assert all(laminations[key].triangulation == self.triangulation for key in laminations)
            self.laminations = laminations
        else:
            assert all(isinstance(lamination, flipper.kernel.Lamination) for lamination in laminations)
            assert all(lamination.triangulation == self.triangulation for lamination in laminations)
            self.laminations = dict(list(flipper.kernel.utilities.name_objects(laminations)))
        
        if isinstance(mapping_classes, dict):
            assert all(isinstance(key, str) for key in mapping_classes)
            assert all(isinstance(mapping_classes[key], flipper.kernel.Encoding) for key in mapping_classes)
            assert all(mapping_classes[key].source_triangulation == self.triangulation for key in mapping_classes)
            assert all(mapping_classes[key].is_mapping_class() for key in mapping_classes)
            assert all(key.swapcase() not in mapping_classes for key in mapping_classes)
            
            self.pos_mapping_classes = dict(mapping_classes)
            self.neg_mapping_classes = dict((name.swapcase(), self.pos_mapping_classes[name].inverse()) for name in self.pos_mapping_classes)
            self.mapping_classes = dict(list(self.pos_mapping_classes.items()) + list(self.neg_mapping_classes.items()))
        else:
            assert all(isinstance(mapping_class, flipper.kernel.Encoding) for mapping_class in mapping_classes)
            assert all(mapping_class.source_triangulation == self.triangulation for mapping_class in mapping_classes)
            assert all(mapping_class.is_mapping_class() for mapping_class in mapping_classes)
            
            self.pos_mapping_classes = dict(list(flipper.kernel.utilities.name_objects(mapping_classes)))
            self.neg_mapping_classes = dict((name.swapcase(), self.pos_mapping_classes[name].inverse()) for name in self.pos_mapping_classes)
            self.mapping_classes = dict(list(self.pos_mapping_classes.items()) + list(self.neg_mapping_classes.items()))
        
        self.zeta = self.triangulation.zeta
    
    @classmethod
    def from_tuple(cls, objects):
        ''' Create an EquippedTriangulation from a list of triangulations, laminations and mapping classes.
        
        Objects must be a non-empty list where each item is:
        
            1) an triangulation (at most one may be given),
            2) a Lamination,
            3) an Encoding,
            4) a pair (String, Lamination),
            5) a pair (String, Encoding).
        
        All laminations / mapping classes must be defined on the same triangulation
        We will automatically name items of type 2) and 3) sequentially `a, b, ..., z, aa, ab, ...` . '''
        
        triangulation = None
        laminations, mapping_classes = {}, {}
        unnamed_laminations, unnamed_mapping_classes = [], []
        for item in objects:
            if isinstance(item, flipper.kernel.Triangulation):
                if triangulation is None:
                    triangulation = item
                else:
                    if item != triangulation:
                        raise ValueError('Only one triangulation may be given.')
            elif isinstance(item, flipper.kernel.Lamination):
                unnamed_laminations.append(item)
            elif isinstance(item, flipper.kernel.Encoding):
                unnamed_mapping_classes.append(item)
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                name, item2 = item
                if isinstance(name, str):
                    if isinstance(item2, flipper.kernel.Lamination):
                        if name not in laminations:
                            laminations[name] = item2
                        else:
                            raise ValueError('Laminations with identical names.')
                    elif isinstance(item2, flipper.kernel.Encoding):
                        if name not in mapping_classes:
                            mapping_classes[name] = item2
                        else:
                            raise ValueError('Encodings with identical names.')
                    else:
                        raise ValueError('Each item given must be a Lamination, Encoding, (String, Lamination) or (String, Encoding).')
                else:
                    raise ValueError('Item must be named by a string.')
            else:
                raise ValueError('Each item given must be: Triangulation, Lamination, Encoding, (String, Lamination) or (String, Encoding).')
        
        for name, lamination in flipper.kernel.utilities.name_objects(unnamed_laminations, laminations):
            laminations[name] = lamination
        
        for name, encoding in flipper.kernel.utilities.name_objects(unnamed_mapping_classes, mapping_classes):
            mapping_classes[name] = encoding
        
        if triangulation is None:
            if laminations:
                triangulation = list(laminations.values())[0].triangulation
            elif mapping_classes:
                triangulation = list(mapping_classes.values())[0].source_triangulation
            else:
                raise ValueError('A triangulation, Lamination or Encoding must be given.')
        
        if any(lamination.triangulation != triangulation for lamination in laminations.values()):
            raise ValueError('All laminations must be on the same triangulation.')
        if any(mapping_class.source_triangulation != triangulation for mapping_class in mapping_classes.values()):
            raise ValueError('All mapping classes must go from the same triangulation.')
        if any(mapping_class.target_triangulation != triangulation for mapping_class in mapping_classes.values()):
            raise ValueError('All mapping classes must go to the same triangulation.')
        
        return cls(triangulation, laminations, mapping_classes)
    
    def __repr__(self):
        return str(self)
    def __str__(self):
        lam_keys = sorted(self.laminations.keys())
        pos_keys = sorted(self.pos_mapping_classes.keys())
        return f'Triangulation with laminations: {lam_keys} and mapping classes: {pos_keys}'
    def __call__(self, word):
        return self.mapping_class(word)
    
    def random_word(self, length, positive=True, negative=True, letters=None):
        ''' Return a random word of the required length.
        
        The letters to choose from can be specified or, alternatively, the set
        of positive, negative or all (default) mapping classes can be used by using the
        flags postive and negative. '''
        
        assert isinstance(length, flipper.IntegerType)
        
        if letters is None:
            pos_keys = sorted(self.pos_mapping_classes.keys())
            neg_keys = sorted(self.neg_mapping_classes.keys())
            
            if positive and negative:
                letters = pos_keys + neg_keys
            elif positive and not negative:
                letters = pos_keys
            elif not positive and negative:
                letters = neg_keys
            else:
                raise TypeError('At least one of positive and negative must be allowed.')
        
        return '.'.join(choice(letters) for _ in range(length))
    
    def generate_skip(self, length, letters=None):
        ''' Return a dictionary whose keys are substrings that cannot appear in reduced words. '''
        
        letters = letters if letters is not None else sorted(self.mapping_classes, key=lambda x: (len(x), x.lower(), x.swapcase()))
        order = generate_ordering(letters)
        
        skip = dict()
        # Start by finding some common relations:
        # Trivial relations.
        for letter in letters:
            skip[(letter, letter.swapcase())] = tuple()
        # Commuting and braiding.
        for a, b in product(letters, repeat=2):
            A, B = a.swapcase(), b.swapcase()
            if A in letters and B in letters:
                for relator in [(a, b, A, B), (a, b, a, B, A, B)]:
                    if self.mapping_class('.'.join(relator)).is_identity():
                        j = len(relator) // 2
                        for k in range(len(relator)):  # Cycling.
                            ww = relator[k:] + relator[:k]
                            if order(ww[:j], inverse(ww[j:])) and ww[:j] != inverse(ww[j:]):
                                if all(ww[m:n] not in skip for n in range(j+1) for m in range(n)):
                                    skip[ww[:j]] = inverse(ww[j:])
        
        # Then do the actual search to the given relator_len.
        temp_options = {
            'group': True,
            'conjugacy': True,
            'bundle': False,
            'exact': True,
            'letters': letters,
            'order': order,
            'skip': skip,
            'prefilter': None,
            'filter': None
            }
        for i in range(1, length+1):
            relators = [word for word in self._all_words_unjoined(i, tuple(), **temp_options) if self.mapping_class('.'.join(word)).is_identity()]
            for j in range(i // 2, i+1):  # Slice length.
                for relator in relators:
                    for k in range(i):  # Cycling.
                        ww = relator[k:] + relator[:k]
                        if order(ww[:j], inverse(ww[j:])) and ww[:j] != inverse(ww[j:]):
                            if all(ww[m:n] not in skip for n in range(j+1) for m in range(n)):
                                skip[ww[:j]] = inverse(ww[j:])
        
        return skip
    
    def _all_words_unjoined(self, length, prefix, **options):
        ''' Yield all words of given length.
        
        Users should not call directly but should use self.all_words(...) instead.
        Assumes that various options have been set. '''
        
        order = options['order']
        letters = options['letters']
        skip = options['skip']
        lp = len(prefix)
        lp2 = lp + 1
        
        if not options['exact'] or len(prefix) == length:
            prefix_inv = inverse(prefix)
            
            good = True
            if good and options['conjugacy'] and prefix[-1:] == inverse(prefix[:1]): good = False
            if good and options['conjugacy'] and not all(order(prefix[i:] + prefix[:i], prefix) for i in range(lp)): good = False
            if good and options['bundle'] and all(x in letters for x in prefix_inv):
                if not all(order(prefix_inv[i:] + prefix_inv[:i], prefix) for i in range(lp)): good = False
            if good and options['filter'] is not None and not options['filter'](prefix): good = False
            if good:
                yield prefix
        
        if len(prefix) < length:
            for letter in letters:
                prefix2 = prefix + (letter,)
                
                good = True
                if good and options['group'] and prefix and any(prefix2[i:] in skip for i in range(lp2)): good = False
                if good and options['conjugacy'] and not all(order(prefix2[i:2*i], prefix2[:min(i, lp2-i)]) for i in range(lp2 // 2, lp)): good = False
                if good and options['prefilter'] is not None and not options['prefilter'](prefix): good = False
                if good:
                    yield from self._all_words_unjoined(length, prefix2, **options)
    
    def _all_words_joined(self, length, prefix, **options):
        for word in self._all_words_unjoined(length, prefix, **options):
            joined = '.'.join(word)
            yield joined if options['apply'] is None else options['apply'](joined)
    
    def _all_mapping_classes(self, length, prefix, **options):
        for word in self._all_words_unjoined(length, prefix, **options):
            mapping_class = self.mapping_class('.'.join(word))
            yield mapping_class if options['apply'] is None else options['apply'](mapping_class)
    
    def all_words(self, length, prefix=None, **options):
        ''' Yield all words of at most the specified length.
        
        There are several equivalence relations defined on these words.
        Words may represent the same:
        
            - mapping class group element (==),
            - conjugacy class (~~), or
            - fibre class (~?).
        
        Valid options and their defaults:
        
            - equivalence='bundle' -- equivalence relation to use. 'bundle', 'conjugacy', 'group', 'none'
            - exact=False -- skip words that do not have exactly the required length.
            - letters=self.mapping_classes - a list of available letters to use, in alphabetical order.
            - skip=None -- an iterable containing substrings that cannot appear.
            - relator_len=2 -- if skip is not given then search words of length at most this much looking for relations.
            - prefilter=None -- filter the prefixes of words by this function.
            - filter=None -- filter the words by this function.
            - apply=None -- apply the given function to the words.
            - cores=None -- how many cores to use.
            - prefix_depth=4 -- depth to search for prefixes for other cores.
        
        Notes:
        
            - By default letters are sorted by (length, lower case, swapcase).
            - For the equivalence used bundle ==> conjugacy ==> group.
            - The function given toapply must be a pickleable if using multiple cores. '''
        
        # Put the prefix into standard form.
        if prefix is None:
            prefix = tuple()
        if isinstance(prefix, str):
            prefix = tuple(self.decompose_word(prefix))
        else:
            prefix = tuple(prefix)
        
        # Setup options:
        default_options = {
            'equivalence': 'bundle',
            'letters': sorted(self.mapping_classes, key=lambda x: (len(x), x.lower(), x.swapcase())),
            'exact': False,
            'skip': None,
            'relator_len': 2,  # 2 get equal generators, 4 gets commutators and 6 gets braids.
            'prefilter': None,
            'filter': None,
            'apply': None,
            'cores': None,
            'prefix_length': 4
            }
        
        # Install any missing options with defaults.
        for option, default in default_options.items():
            if option not in options: options[option] = default
        
        # Set implications. Possible values for options['equivalence'] are:
        #  None, group, conjugacy, bundle
        options['bundle'] = options['equivalence'] == 'bundle'
        options['conjugacy'] = options['equivalence'] == 'conjugacy' or options['bundle']
        options['group'] = options['equivalence'] == 'group' or options['conjugacy']
        
        # Build the list of substrings that must be avoided.
        if options['skip'] is not None:
            options['skip'] = set(options['skip'])
        elif options['group']:
            options['skip'] = self.generate_skip(options['relator_len'], options['letters'])
        else:
            options['skip'] = set()
        
        # We need to save a copy of the options at this point to pass to the nodes (if we
        # are multiprocessing) as the order function we are about to build is anonymous
        # and so it can't be Pickled.
        node_options = dict(options)
        
        # Build the ordering based on the letters given.
        options['order'] = generate_ordering(options['letters'])
        
        if options['cores'] is None:
            # Just use the single core algorithm:
            yield from self._all_words_joined(length, prefix, **options)
        else:
            temp_options = dict(options)
            temp_options['conjugacy'] = False
            temp_options['bundle'] = False
            temp_options['exact'] = True
            temp_options['filter'] = None
            if options['prefix_length'] <= length:
                prefixes = [(self, length, leaf, node_options) for leaf in self._all_words_unjoined(options['prefix_length'], prefix, **temp_options)]
            else:
                prefixes = []
            
            Q = multiprocessing.Queue()
            A = multiprocessing.Queue()
            P = [multiprocessing.Process(target=_worker_thread_word, args=(Q, A)) for i in range(options['cores'])]
            for p in P: p.daemon = True
            for p in P: p.start()
            
            Q.put((self, min(options['prefix_length']-1, length), prefix, node_options))
            for data in prefixes:
                Q.put(data)
            
            for i in range(options['cores']):
                Q.put(None)
            
            num_completed_cores = 0
            while num_completed_cores < options['cores']:
                result = A.get()
                if result is None:
                    num_completed_cores += 1
                else:
                    yield result
            
            for p in P: p.terminate()
    
    def all_mapping_classes(self, length, prefix=None, **options):
        ''' Yield all mapping classes of at most the specified length.
        
        There are several equivalence relations defined on these mapping classes.
        We may try to only one of each:
        
            - mapping class group element (==),
            - conjugacy class (~~), or
            - fibre class (~?).
        
        Valid options and their defaults:
        
            - equivalence='bundle' -- equivalence relation to use. 'bundle', 'conjugacy', 'group', 'none'
            - exact=False -- skip words that do not have exactly the required length.
            - letters=self.mapping_classes - a list of available letters to use, in alphabetical order.
            - skip=None -- an iterable containing substrings that cannot appear.
            - relator_len=2 -- if skip is not given then search words of length at most this much looking for relations.
            - prefilter=None -- filter the prefixes of words by this function.
            - filter=None -- filter the words by this function.
            - apply=None -- apply the given function to the words.
            - cores=None -- how many cores to use.
            - prefix_depth=3 -- depth to search for prefixes for other cores.
        
        Notes:
        
            - By default letters are sorted by (length, lower case, swapcase).
            - For the equivalence used bundle ==> conjugacy ==> group.
            - The function given toapply must be a pickleable if using multiple cores. '''
        
        # Put the prefix into standard form.
        if prefix is None:
            prefix = tuple()
        if isinstance(prefix, str):
            prefix = tuple(self.decompose_word(prefix))
        else:
            prefix = tuple(prefix)
        
        # Setup options:
        default_options = {
            'equivalence': 'bundle',
            'letters': sorted(self.mapping_classes, key=lambda x: (len(x), x.lower(), x.swapcase())),
            'exact': False,
            'skip': None,
            'relator_len': 2,  # 2 get equal generators, 4 gets commutators and 6 gets braids.
            'prefilter': None,
            'filter': None,
            'apply': None,
            'cores': None,
            'prefix_length': 3
            }
        
        # Install any missing options with defaults.
        for option, default in default_options.items():
            if option not in options: options[option] = default
        
        # Set implications. Possible values for options['equivalence'] are:
        #  None, group, conjugacy, bundle
        options['bundle'] = options['equivalence'] == 'bundle'
        options['conjugacy'] = options['equivalence'] == 'conjugacy' or options['bundle']
        options['group'] = options['equivalence'] == 'group' or options['conjugacy']
        
        # Build the list of substrings that must be avoided.
        if options['skip'] is not None:
            options['skip'] = set(options['skip'])
        elif options['group']:
            options['skip'] = self.generate_skip(options['relator_len'], options['letters'])
        else:
            options['skip'] = set()
        
        # We need to save a copy of the options at this point to pass to the nodes (if we
        # are multiprocessing) as the order function we are about to build is anonymous
        # and so it can't be Pickled.
        node_options = dict(options)
        
        # Build the ordering based on the letters given.
        options['order'] = generate_ordering(options['letters'])
        
        if options['cores'] is None:
            # Just use the single core algorithm:
            yield from self._all_mapping_classes(length, prefix, **options)
        else:
            temp_options = dict(options)
            temp_options['conjugacy'] = False
            temp_options['bundle'] = False
            temp_options['exact'] = True
            temp_options['filter'] = None
            if options['prefix_length'] <= length:
                prefixes = [(self, length, leaf, node_options) for leaf in self._all_words_unjoined(options['prefix_length'], prefix, **temp_options)]
            else:
                prefixes = []
            
            Q = multiprocessing.Queue()
            A = multiprocessing.Queue()
            P = [multiprocessing.Process(target=_worker_thread_mapping_class, args=(Q, A)) for i in range(options['cores'])]
            for p in P: p.daemon = True
            for p in P: p.start()
            
            Q.put((self, min(options['prefix_length']-1, length), prefix, node_options))
            for data in prefixes:
                Q.put(data)
            
            for i in range(options['cores']):
                Q.put(None)
            
            num_completed_cores = 0
            while num_completed_cores < options['cores']:
                result = A.get()
                if result is None:
                    num_completed_cores += 1
                else:
                    yield result
            
            for p in P: p.terminate()
    
    def decompose_word(self, word):
        ''' Return a list of mapping_classes keys whose concatenation is word and the keys are chosen greedly.
        
        Raises a KeyError if the greedy decomposition fails. '''
        
        assert isinstance(word, str)
        
        # By sorting the available keys, longest first, we ensure that any time we
        # get a match it is as long as possible.
        available_letters = sorted(self.mapping_classes, key=len, reverse=True)
        decomposition = []
        for subword in word.split('.'):
            while subword:
                for letter in available_letters:
                    if subword.startswith(letter):
                        decomposition.append(letter)
                        subword = subword[len(letter):]
                        break
                else:
                    raise TypeError(f'After extracting {decomposition}, the remaining {word} cannot be greedly decomposed as a concatination of self.mapping_classes')
        
        return decomposition
    
    def mapping_class(self, word):
        ''' Return the mapping class corresponding to the given word or a random one of given length if given an integer.
        
        The given word is decomposed using self.decompose_word and the composition
        of the mapping classes involved is returned.
        
        Raises a TypeError if the word does not correspond to a mapping class. '''
        
        assert isinstance(word, (str, flipper.IntegerType))
        
        if isinstance(word, flipper.IntegerType):
            word = self.random_word(word)
        
        name = word  # Record the current word so we can use it later to name the mapping class.
        
        # Remove any whitespace.
        word = word.replace(' ', '')
        
        # Check for balanced parentheses.
        counter = 0
        for letter in word:
            if letter == '(': counter += 1
            if letter == ')': counter -= 1
            if counter < 0: raise TypeError('Unbalanced parentheses.')
        if counter != 0: raise TypeError('Unbalanced parentheses.')
        
        # Expand out parenthesis powers.
        # This can fail with a TypeError.
        old_word = None
        while word != old_word:  # While a change was made.
            old_word = word
            for subword, power in re.findall(r'(\([\w_\.]*\))\^(-?\d+)', word):
                decompose = self.decompose_word(subword[1:-1])
                int_power = int(power)
                if int_power > 0:
                    replacement = '.'.join(decompose) * int_power
                else:
                    replacement = '.'.join(letter.swapcase() for letter in decompose[::-1]) * abs(int_power)
                word = word.replace(subword + '^' + power, replacement)
        
        # Remove any remaining parenthesis, these do not have a power and are treated as ^1
        word = word.replace('(', '').replace(')', '')
        
        # Expand out powers without parenthesis. Here we use a greedy algorithm and take the
        # longest mapping class occuring before the power. Note that we only do one pass and so
        # only all pure powers to be expanded once, that is 'aBBB^2^3' is not recognised.
        available_letters = sorted(self.mapping_classes, key=len, reverse=True)
        for letter in available_letters:
            for subword, power in re.findall(rf'({letter})\^(-?\d+)', word):
                int_power = int(power)
                word = word.replace(subword + '^' + power, (letter if int_power > 0 else letter.swapcase()) * abs(int_power))
        
        # This can fail with a TypeError.
        sequence = [item for letter in self.decompose_word(word) for item in self.mapping_classes[letter]]
        return flipper.kernel.Encoding(sequence, _cache={'name': name}) if sequence else self.triangulation.id_encoding()
    
    def lamination(self, name):
        ''' Return the lamination given by name. '''
        
        return self.laminations[name]

