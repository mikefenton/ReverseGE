from algorithm.parameters import params
from representation import individual


def check_ind(ind, target):
    """
    Checks the mapping of an individual to ensure everything is correct.
    
    :param ind: An instance of the representation.individaul.Individual class.
    :param target: A target string against which to match the phenotype of
    the individual.
    :return: Nothing.
    """
    
    # Re-map individual using genome mapper to check everything is ok.
    new_ind = individual.Individual(ind.genome, None)

    # Check phenotypes are the same.
    if new_ind.phenotype != ind.phenotype:
        print("\nError: Solution doesn't match genome mapping.\n")
        print("Solution:\t", ind.phenotype)
        print("Mapped:  \t", new_ind.phenotype)
        print("Genome:  \t", ind.genome)
        quit()
    
    # Check the phenotype matches the target string.
    elif ind.phenotype != target:
        print("\nError: solution doesn't match target.\n")
        print("Target:  ", target)
        print("Solution:", ind.phenotype)
        quit()
        
    else:
        # Check the tree matches the phenotype.
        check_output(ind)


def check_output(ind):
    """
    Check the phenotype of an individual to ensure it matches the output of
    all individaul nodes.
    
    :param ind: An individaul to be checked.
    :return: Nothing.
    """
    
    if ind.phenotype != get_output(ind.tree):
        print("Error: Phenotype doesn't match tree output")
        print("Phenotype:\n\t", ind.phenotype, "\nTree output:\n\t", get_output(ind.tree))


def check_genome_from_tree(ind_tree, space=""):
    """
    Goes through a tree and checks each codon to ensure production choice is
    correct.
    
    :param ind_tree: The representation.tree.Tree class derivation tree of
    an individual.
    :return: Nothing.
    """
    
    if ind_tree.children:
        # print(space, ind_tree.root)
        space += " "
        # This node has children and thus must have an associated codon.
        
        if not ind_tree.codon:
            print("Error: "
                  "utilities.check_methods.check_genome_from_tree. "
                  "Node with children has no codon.")
            print(ind_tree.children)
            quit()
        
        # Check production choices for node root.
        productions = params['BNF_GRAMMAR'].rules[ind_tree.root]
        
        # Select choice based on node codon.
        selection = ind_tree.codon % productions['no_choices']
        choice = productions['choices'][selection]
        
        # Build list of roots of the chosen production.
        prods = [sym['symbol'] for sym in choice['choice']]
        roots = []
        
        # Build list of the roots of all node children.
        for kid in ind_tree.children:
            if kid.parent != ind_tree:
                print("Error: Child doesn't match parent")
            roots.append(kid.root)
        
        # Match production roots with children roots.
        if roots != prods:
            print("Error: "
                  "utilities.check_methods.check_genome_from_tree. "
                  "Codons are incorrect for given tree.")
            print("Codon productions:\t", prods)
            print("Actual children:  \t", roots)
            quit()
    
    for kid in ind_tree.children:
        # Recurse over all children.
        check_genome_from_tree(kid, space)


def get_output(ind_tree):
    """
    Calls the recursive build_output(self) which returns a list of all
    node roots. Joins this list to create the full phenotype of an
    individual. This two-step process speeds things up as it only joins
    the phenotype together once rather than at every node.

    :param ind_tree: a full tree for which the phenotype string is to be built.
    :return: The complete built phenotype string of an individual.
    """
       
    return "".join(build_output(ind_tree))


def build_output(tree):
    """
    Recursively adds all node roots to a list which can be joined to
    create the phenotype.

    :return: The list of all node roots.
    """
    
    output = []
    for child in tree.children:
        if not child.children:
            # If the current child has no children it is a terminal.
            # Append it to the output.
            output.append(child.root)
        
        else:
            # Otherwise it is a non-terminal. Recurse on all
            # non-terminals.
            output += build_output(child)
    
    return output


def ret_true(obj):
    """
    Returns "True" if an object is there. E.g. if given a list, will return
    True if the list contains some data, but False if the list is empty.
    
    :param obj: Some object (e.g. list)
    :return: True if something is there, else False.
    """

    if obj:
        return True
    else:
        return False


def generate_codon(NT, choice):
    """
    Given a list of choices and a choice from that list, generate and return a
    codon which will result in that production choice being made.

    :param NT: A root non-terminal node from which production choices are made.
    :param choice: A production choice from the available choices of the
    given NT.
    :return: A codon that will give that production choice.
    """

    productions = params['BNF_GRAMMAR'].rules[NT]

    # Find the production choices from the given NT.
    choices = [choice['choice'] for choice in productions['choices']]

    # Find the index of the chosen production and set a matching codon based
    # on that index.
    try:
        prod_index = choices.index(choice)
    except ValueError:
        print("Error: Specified choice", choice, "not a valid choice for "
                                                 "NT", NT)
        quit()
    
    codon_range = range(productions['no_choices'],
                        params['CODON_SIZE'],
                        productions['no_choices'])
    codon = codon_range[0] + prod_index
        
    # Generate a valid codon.
    return codon
