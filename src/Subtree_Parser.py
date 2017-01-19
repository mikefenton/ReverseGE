from utilities.algorithm.initialise_run import check_python_version

check_python_version()

from datetime import datetime
import sys

from algorithm.parameters import params, set_params
from operators.subtree_parse import combine_snippets, \
    check_snippets_for_solution
from representation.tree import Tree
from utilities.representation.check_methods import generate_codon, \
    check_ind
from utilities.stats import trackers


def assemble_solution(target):
    """
    Given a target string, build up a simple repository of snippets of
    terminals which match certain portions of the target string.
    
    :return: A complete solution in the form of an individual.
    """
    
    if not params['SILENT']:
        print("Target:", target)
    terms = params['BNF_GRAMMAR'].terminals
    rules = params['BNF_GRAMMAR'].rules

    trackers.snippets = {}
    
    for T in sorted(terms.keys()):
        # Iterate over all Terminals.

        # Find all occurances of this terminal in the target string.
        occurrances = []
        index = 0
        while index < len(target):
            index = target.find(T, index)
            if index not in occurrances and index != -1:
                occurrances.append(index)
                index += len(T)
            else:
                break
         
        for idx in occurrances:
            # Check each occurrence of this terminal in the target string.

            for NT in terms[T]:
                
                if any([[T] == i for i in [[sym['symbol'] for sym in
                                            choice['choice']] for choice in
                                           rules[NT]['choices']]]):
                    # Check if current T is the entire production choice of any
                    # particular rule.

                    # Generate a key for the snippets repository.
                    key = " ".join([str([idx, idx+len(T)]), NT])
                    
                    # Get index of production choice.
                    index = [[sym['symbol'] for sym in choice['choice']] for
                             choice in rules[NT]['choices']].index([T])
                    
                    # Get production choice.
                    choice = rules[NT]['choices'][index]['choice']
                    
                    # Generate a tree for this choice.
                    parent = Tree(NT, None)
                    
                    # Generate a codon for this choice.
                    parent.codon = generate_codon(NT, choice)
                    
                    # Set the snippet key for the parent.
                    parent.snippet = key
                    
                    # Create child for terminal.
                    child = Tree(T, parent)
                    
                    # Add child to parent.
                    parent.children.append(child)
                    
                    # Add snippet to snippets repository.
                    trackers.snippets[key] = parent

    if not params['SILENT']:
        print("\nStarting with", len(trackers.snippets), "snippets.\n")

    # Combine snippets to make bigger snippets. Quickly builds up the
    # perfect solution.
    combine_snippets()

    # Check snippets for full correct solution
    solution = check_snippets_for_solution()
        
    if solution:
        return solution

    else:
        print("Error: Target string couldn't be parsed using given grammar.")
        quit()


if __name__ == '__main__':
    t1 = datetime.now()
    set_params(sys.argv)
    solution = assemble_solution(params['TARGET'])
    check_ind(solution, params['TARGET'])
    print("\nGenome:")
    print(solution.genome)
    t2 = datetime.now()
    time_taken = t2 - t1
    if not params['SILENT']:
        print("\nTotal time taken:", time_taken)
