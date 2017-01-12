from re import match, finditer, DOTALL, MULTILINE
from sys import maxsize

from algorithm.parameters import params


class Grammar(object):
    """
    Parser for Backus-Naur Form (BNF) Context-Free Grammars.
    """
        
    def __init__(self, file_name):
        """
        Initialises an instance of the grammar class. This instance is used
        to parse a given file_name grammar.

        :param file_name: A specified BNF grammar file.
        """
        
        if file_name.endswith("pybnf"):
            # Use python filter for parsing grammar output as grammar output
            # contains indented python code.
            self.python_mode = True
        
        else:
            # No need to filter/interpret grammar output, individual
            # phenotypes can be evaluated as normal.
            self.python_mode = False
        
        # Initialise empty dict for all production rules in the grammar.
        # Initialise empty dict of permutations of solutions possible at
        # each derivation tree depth.
        self.rules, self.permutations = {}, {}
        
        # Initialise dicts for terminals and non terminals, set params.
        self.non_terminals, self.terminals, self.concat_NTs = {}, {}, {}
        self.climb_NTs = {}
        self.start_rule, self.codon_size = None, params['CODON_SIZE']
        self.min_path, self.max_arity, self.min_ramp = None, None, None

        # Set regular expressions for parsing BNF grammar.
        self.ruleregex = '(?P<rulename><\S+>)\s*::=\s*(?P<production>(?:(?=\#)\#[^\r\n]*|(?!<\S+>\s*::=).+?)+)'
        self.productionregex = '(?=\#)(?:\#.*$)|(?!\#)\s*(?P<production>(?:[^\'\"\|\#]+|\'.*?\'|".*?")+)'
        self.productionpartsregex = '\ *([\r\n]+)\ *|([^\'"<\r\n]+)|\'(.*?)\'|"(.*?)"|(?P<subrule><[^>|\s]+>)|([<]+)'
        
        # Read in BNF grammar, set production rules, terminals and
        # non-terminals.
        self.read_bnf_file(file_name)
        
        # Check the minimum depths of all non-terminals in the grammar.
        self.check_depths()
        
        # Check which non-terminals are recursive.
        self.check_recursion(self.start_rule["symbol"], [])
        
        # Set the minimum path and maximum arity of the grammar.
        self.set_arity()
        
        # Generate lists of recursive production choices and shortest
        # terminating path production choices for each NT in the grammar.
        # Enables faster tree operations.
        self.set_grammar_properties()
        
        # Find production choices which can be used to concatenate
        # subtrees.
        self.find_concatination_NTs()
            
    def read_bnf_file(self, file_name):
        """
        Read a grammar file in BNF format. Parses the grammar and saves a
        dict of all production rules and their possible choices.

        :param file_name: A specified BNF grammar file.
        :return: Nothing.
        """
        
        with open(file_name, 'r') as bnf:
            # Read the whole grammar file.
            content = bnf.read()
            
            for rule in finditer(self.ruleregex, content, DOTALL):
                # Find all rules in the grammar
                
                if self.start_rule is None:
                    # Set the first rule found as the start rule.
                    self.start_rule = {"symbol": rule.group('rulename'),
                                       "type": "NT"}
                
                # Create and add a new rule.
                self.non_terminals[rule.group('rulename')] = {
                    'id': rule.group('rulename'),
                    'min_steps': maxsize,
                    'expanded': False,
                    'recursive': True,
                    'b_factor': 0}
                
                # Initialise empty list of all production choices for this
                # rule.
                tmp_productions = []
                
                for p in finditer(self.productionregex,
                                  rule.group('production'), MULTILINE):
                    # Iterate over all production choices for this rule.
                    # Split production choices of a rule.

                    if p.group('production') is None or p.group(
                            'production').isspace():
                        # Skip to the next iteration of the loop if the
                        # current "p" production is None or blank space.
                        continue

                    # Initialise empty data structures for production choice
                    tmp_production, terminalparts = [], ''

                    # special case: GERANGE:dataset_n_vars will be transformed
                    # to productions 0 | 1 | ... | n_vars-1
                    GE_RANGE_regex = r'GE_RANGE:(?P<range>\w*)'
                    m = match(GE_RANGE_regex, p.group('production'))
                    if m:
                        try:
                            if m.group('range') == "dataset_n_vars":
                                # set n = number of columns from dataset
                                n = params['FITNESS_FUNCTION'].n_vars
                            else:
                                # assume it's just an int
                                n = int(m.group('range'))
                        except (ValueError, AttributeError):
                            raise ValueError("Bad use of GE_RANGE: "
                                             + m.group())

                        for i in range(n):
                            # add a terminal symbol
                            tmp_production, terminalparts = [], ''
                            symbol = {
                                "symbol": str(i),
                                "type": "T",
                                "min_steps": 0,
                                "recursive": False}
                            tmp_production.append(symbol)
                            self.terminals[str(i)] = rule.group('rulename')
                            tmp_productions.append({"choice": tmp_production,
                                                    "recursive": False,
                                                    "NT_kids": False})
                        # don't try to process this production further
                        # (but later productions in same rule will work)
                        continue
                    
                    for sub_p in finditer(self.productionpartsregex,
                                          p.group('production').strip()):
                        # Split production into terminal and non terminal
                        # symbols.
                        
                        if sub_p.group('subrule'):
                            if terminalparts:
                                # Terminal symbol is to be appended to the
                                # terminals dictionary.
                                symbol = {"symbol": terminalparts,
                                          "type": "T",
                                          "min_steps": 0,
                                          "recursive": False}
                                tmp_production.append(symbol)
                                self.terminals[terminalparts] = \
                                    rule.group('rulename')
                                terminalparts = ''
                            
                            tmp_production.append(
                                {"symbol": sub_p.group('subrule'),
                                 "type": "NT"})
                        
                        else:
                            # Unescape special characters (\n, \t etc.)
                            terminalparts += ''.join(
                                [part.encode().decode('unicode-escape') for
                                 part in sub_p.groups() if part])
                    
                    if terminalparts:
                        # Terminal symbol is to be appended to the terminals
                        # dictionary.
                        symbol = {"symbol": terminalparts,
                                  "type": "T",
                                  "min_steps": 0,
                                  "recursive": False}
                        tmp_production.append(symbol)
                        self.terminals[terminalparts] = rule.group('rulename')
                    tmp_productions.append({"choice": tmp_production,
                                            "recursive": False,
                                            "NT_kids": False})
                
                if not rule.group('rulename') in self.rules:
                    # Add new production rule to the rules dictionary if not
                    # already there.
                    self.rules[rule.group('rulename')] = {
                        "choices": tmp_productions,
                        "no_choices": len(tmp_productions)}
                    
                    if len(tmp_productions) == 1:
                        # Unit productions.
                        print("Warning: Grammar contains unit production "
                              "for production rule", rule.group('rulename'))
                        print("       Unit productions consume GE codons.")
                else:
                    # Conflicting rules with the same name.
                    raise ValueError("lhs should be unique",
                                     rule.group('rulename'))
    
    def check_depths(self):
        """
        Run through a grammar and find out the minimum distance from each
        NT to the nearest T. Useful for initialisation methods where we
        need to know how far away we are from fully expanding a tree
        relative to where we are in the tree and what the depth limit is.
            
        :return: Nothing.
        """
        
        # Initialise graph and counter for checking minimum steps to Ts for
        # each NT.
        counter, graph = 1, []
        
        for rule in sorted(self.rules.keys()):
            # Iterate over all NTs.
            choices = self.rules[rule]['choices']
                                    
            # Set branching factor for each NT.
            self.non_terminals[rule]['b_factor'] = self.rules[rule][
                'no_choices']
            
            for choice in choices:
                # Add a new edge to our graph list.
                graph.append([rule, choice['choice']])

        while graph:
            removeset = set()
            for edge in graph:
                # Find edges which either connect to terminals or nodes
                # which are fully expanded.
                if all([sy["type"] == "T" or
                        self.non_terminals[sy["symbol"]]['expanded']
                        for sy in edge[1]]):
                    removeset.add(edge[0])
            
            for s in removeset:
                # These NTs are now expanded and have their correct minimum
                # path set.
                self.non_terminals[s]['expanded'] = True
                self.non_terminals[s]['min_steps'] = counter
            
            # Create new graph list and increment counter.
            graph = [e for e in graph if e[0] not in removeset]
            counter += 1
    
    def check_recursion(self, cur_symbol, seen):
        """
        Traverses the grammar recursively and sets the properties of each rule.

        :param cur_symbol: symbol to check.
        :param seen: Contains already checked symbols in the current traversal.
        :return: Boolean stating whether or not cur_symbol is recursive.
        """
        
        if cur_symbol not in self.non_terminals.keys():
            # Current symbol is a T.
            return False
        
        if cur_symbol in seen:
            # Current symbol has already been seen, is recursive.
            return True

        # Append current symbol to seen list.
        seen.append(cur_symbol)
        
        # Get choices of current symbol.
        choices = self.rules[cur_symbol]['choices']
        nt = self.non_terminals[cur_symbol]
        
        recursive = False
        for choice in choices:
            for sym in choice['choice']:
                # Recurse over choices.
                recursive_symbol = self.check_recursion(sym["symbol"], seen)
                recursive = recursive or recursive_symbol
        
        # Set recursive properties.
        nt['recursive'] = recursive
        seen.remove(cur_symbol)
        
        return nt['recursive']
    
    def set_arity(self):
        """
        Set the minimum path of the grammar, i.e. the smallest legal
        solution that can be generated.

        Set the maximum arity of the grammar, i.e. the longest path to a
        terminal from any non-terminal.

        :return: Nothing
        """
        
        # Set the minimum path of the grammar as the minimum steps to a
        # terminal from the start rule.
        self.min_path = self.non_terminals[self.start_rule["symbol"]][
            'min_steps']
        
        # Initialise the maximum arity of the grammar to 0.
        self.max_arity = 0
        
        # Find the maximum arity of the grammar.
        for NT in self.non_terminals:
            if self.non_terminals[NT]['min_steps'] > self.max_arity:
                # Set the maximum arity of the grammar as the longest path
                # to a T from any NT.
                self.max_arity = self.non_terminals[NT]['min_steps']
        
        # Add the minimum terminal path to each production rule.
        for rule in self.rules:
            for choice in self.rules[rule]['choices']:
                NT_kids = [i for i in choice['choice'] if i["type"] == "NT"]
                if NT_kids:
                    choice['NT_kids'] = True
                    for sym in NT_kids:
                        sym['min_steps'] = self.non_terminals[sym["symbol"]][
                            'min_steps']
        
        # Add boolean flag indicating recursion to each production rule.
        for rule in self.rules:
            for prod in self.rules[rule]['choices']:
                for sym in [i for i in prod['choice'] if i["type"] == "NT"]:
                    sym['recursive'] = self.non_terminals[sym["symbol"]][
                        'recursive']
                    if sym['recursive']:
                        prod['recursive'] = True
    
    def set_grammar_properties(self):
        """
        Goes through all non-terminals and finds the production choices with
        the minimum steps to terminals and with recursive steps.
        
        :return: Nothing
        """
        
        for nt in self.non_terminals:
            # Loop over all non terminals.
            # Find the production choices for the current NT.
            choices = self.rules[nt]['choices']
            
            for choice in choices:
                # Set the maximum path to a terminal for each produciton choice
                choice['max_path'] = max([item["min_steps"] for item in
                                          choice['choice']])

            # Find shortest path to a terminal for all production choices for
            # the current NT. The shortest path will be the minimum of the
            # maximum paths to a T for each choice over all chocies.
            min_path = min([choice['max_path'] for choice in choices])
            
            # Set the minimum path in the self.non_terminals dict.
            self.non_terminals[nt]['min_path'] = [choice for choice in
                                                  choices if choice[
                                                      'max_path'] == min_path]

            # Find recursive production choices for current NT. If any
            # constituent part of a production choice is recursive,
            # it is added to the recursive list.
            self.non_terminals[nt]['recursive'] = [choice for choice in
                                                   choices if choice[
                                                       'recursive']]

    def find_concatination_NTs(self):
        """
        Scour the grammar class to find non-terminals which can be used to
        combine/concatenate derivation trees. Build up a list of such
        non-terminals. A concatenation non-terminal is one in which at least
        one production choice contains multiple non-terminals. For example:

            <e> ::= (<e><o><e>)|<v>

        is a concatenation NT, since the production choice (<e><o><e>) can
        concatenate multiple NTs together. Note that this choice also includes
        a combination of terminals and non-terminals.

        :return: Nothing.
        """
    
        # Iterate over all non-terminals/production rules.
        for rule in sorted(self.rules.keys()):
        
            # Find NTs which have production choices which can concatenate
            # two NTs.
            concat = [choice for choice in self.rules[rule]['choices'] if
                      choice['NT_kids'] and len([sym for sym in choice[
                      'choice'] if sym['type'] == "NT"]) > 1]
            
            climb = [choice for choice in self.rules[rule]['choices'] if
                      choice['NT_kids'] and len([sym for sym in choice[
                      'choice'] if sym['type'] == "NT"]) == 1]
            
            if concat:
                # We can concatenate NTs.
                for choice in concat:
                                        
                    symbols = [sym['symbol'] for sym in choice['choice'] if
                               sym['type'] == "NT"]

                    for sym in symbols:
                        # We add to our self.concat_NTs dictionary. The key is
                        # the root node we want to concatenate with another
                        # node. This way when we have a node and wish to see
                        # if we can concatenate it with anything else, we
                        # simply look up this dictionary.
                        conc = [choice['choice'], rule, [[sym['symbol'],
                                                          sym['type']] for sym
                                                         in choice['choice']]]
                                                
                        if sym not in self.concat_NTs:
                            self.concat_NTs[sym] = [conc]
                        else:
                            if conc not in self.concat_NTs[sym]:
                                self.concat_NTs[sym].append(conc)

            if climb:
                # We can use these choices to generate parents for single NTs.
                for choice in climb:
                    
                    symbols = [sym['symbol'] for sym in choice['choice']]
                    
                    NT = [sym['symbol'] for sym in choice['choice'] if
                          sym['type'] == "NT"][0]

                    # We add to our self.climb_NTs dictionary. The key is the
                    # root node we want to find a parent for. This way when we
                    # have a node and wish to see if we can find a parent
                    # for it, we simply look up this dictionary.
                    cl = [choice['choice'], rule, symbols]
                    
                    if NT not in self.climb_NTs:
                        self.climb_NTs[NT] = [cl]
                    else:
                        if cl not in self.climb_NTs[NT]:
                            self.climb_NTs[NT].append(cl)

    def __str__(self):
        return "%s %s %s %s" % (self.terminals, self.non_terminals,
                                self.rules, self.start_rule)
