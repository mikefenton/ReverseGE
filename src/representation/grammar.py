from re import match, finditer, DOTALL, MULTILINE

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
                
        # Initialise dicts for rules, terminals and non terminals.
        self.non_terminals, self.terminals, self.concat_NTs = {}, {}, {}
        self.rules, self.climb_NTs, self.start_rule = {}, {}, None

        # Set regular expressions for parsing BNF grammar.
        self.ruleregex = '(?P<rulename><\S+>)\s*::=\s*(?P<production>(?:(?=\#)\#[^\r\n]*|(?!<\S+>\s*::=).+?)+)'
        self.productionregex = '(?=\#)(?:\#.*$)|(?!\#)\s*(?P<production>(?:[^\'\"\|\#]+|\'.*?\'|".*?")+)'
        self.productionpartsregex = '\ *([\r\n]+)\ *|([^\'"<\r\n]+)|\'(.*?)\'|"(.*?)"|(?P<subrule><[^>|\s]+>)|([<]+)'
        
        # Read in BNF grammar, set production rules, terminals and
        # non-terminals.
        self.read_bnf_file(file_name)

        # Set boolean flag for which production choices contain non-terminals.
        self.set_NT_kids()
        
        # Find production choices which can be used to concatenate_multi_NT
        # subtrees.
        self.find_concatination_NTs()
        
        # Set maximum codon size as the
        params['CODON_SIZE'] = 2 * max([self.rules[rule]["no_choices"] for rule in
                                        sorted(self.rules.keys())])
                    
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
                    'id': rule.group('rulename')}
                
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
                                "type": "T"}
                            tmp_production.append(symbol)
                            if str(i) not in self.terminals:
                                self.terminals[str(i)] = \
                                    [rule.group('rulename')]
                            elif rule.group('rulename') not in \
                                self.terminals[str(i)]:
                                self.terminals[str(i)].append(
                                    rule.group('rulename'))
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
                                          "type": "T"}
                                tmp_production.append(symbol)
                                if terminalparts not in self.terminals:
                                    self.terminals[terminalparts] = \
                                        [rule.group('rulename')]
                                elif rule.group('rulename') not in \
                                    self.terminals[terminalparts]:
                                    self.terminals[terminalparts].append(
                                        rule.group('rulename'))
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
                                  "type": "T"}
                        tmp_production.append(symbol)
                        if terminalparts not in self.terminals:
                            self.terminals[terminalparts] = \
                                [rule.group('rulename')]
                        elif rule.group('rulename') not in \
                            self.terminals[terminalparts]:
                            self.terminals[terminalparts].append(
                                rule.group('rulename'))
                    tmp_productions.append({"choice": tmp_production,
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

    def set_NT_kids(self):
        """
        Set boolean flag for which production choices contain non-terminals.

        :return: Nothing
        """
    
        # Add the minimum terminal path to each production rule.
        for rule in self.rules:
            for choice in self.rules[rule]['choices']:
                NT_kids = [i for i in choice['choice'] if i["type"] == "NT"]
                if NT_kids:
                    choice['NT_kids'] = True

    def find_concatination_NTs(self):
        """
        Scour the grammar class to find non-terminals which can be used to
        combine/concatenate_multi_NT derivation trees. Build up a list of such
        non-terminals. A concatenation non-terminal is one in which at least
        one production choice contains multiple non-terminals. For example:

            <e> ::= (<e><o><e>)|<v>

        is a concatenation NT, since the production choice (<e><o><e>) can
        concatenate_multi_NT multiple NTs together. Note that this choice also includes
        a combination of terminals and non-terminals.

        :return: Nothing.
        """
    
        # Iterate over all non-terminals/production rules.
        for rule in sorted(self.rules.keys()):
            
            # Find NTs which have production choices which can concatenate_multi_NT
            # two NTs.
            multi_concat = [choice for choice in self.rules[rule]['choices'] if
                            choice['NT_kids'] and len([sym for sym in choice[
                            'choice'] if sym['type'] == "NT"]) > 1]
            
            single_concat = [choice for choice in self.rules[rule]['choices'] if
                             choice['NT_kids'] and len([sym for sym in choice[
                            'choice'] if sym['type'] == "NT"]) == 1]
            
            if multi_concat:
                # We can concatenate_multi_NT NTs.
                for choice in multi_concat:
                                        
                    symbols = [sym['symbol'] for sym in choice['choice'] if
                               sym['type'] == "NT"]

                    for sym in symbols:
                        # We add to our self.concat_NTs dictionary. The key is
                        # the root node we want to concatenate_multi_NT with another
                        # node. This way when we have a node and wish to see
                        # if we can concatenate_multi_NT it with anything else, we
                        # simply look up this dictionary.
                        conc = [choice['choice'], rule, [[sym['symbol'],
                                                          sym['type']] for sym
                                                         in choice['choice']]]
                                                
                        if sym not in self.concat_NTs:
                            self.concat_NTs[sym] = [conc]
                        else:
                            if conc not in self.concat_NTs[sym]:
                                self.concat_NTs[sym].append(conc)

            if single_concat:
                # We can use these choices to generate parents for single NTs.
                for choice in single_concat:
                    
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
