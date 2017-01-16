import re
from copy import copy
from itertools import zip_longest

from algorithm.parameters import params
from representation import individual, tree
from utilities.representation.check_methods import get_output, generate_codon
from utilities.stats import trackers


def combine_snippets():
    """
    As the snippets repository grows, we can start to combine
    neighboring snippets to build bigger snippets. Eventually we hope this
    can just build the perfect solution. Iteratively builds snippets until
    no more snippets can be built form the current library.

    :return: Nothing.
    """

    # Find the number of snippets at T.
    original_snippets = len(trackers.snippets)
    
    # Perform first pass of concatenation.
    updated_snippets = concatenate()

    # Initialise counter for concatenation interations.
    no_passes = 1

    if not params['SILENT']:
        print(no_passes, "pass  \tOriginal:", original_snippets,
              "\tNew:", updated_snippets)

    while updated_snippets != original_snippets:
        # Keep concatenating snippets until no more concatenations can be made.

        # Save old T+1
        pre_updated_snippets = copy(updated_snippets)
        
        # Perform concatenation.
        updated_snippets = concatenate()

        # Set new T as old T+1
        original_snippets = pre_updated_snippets

        # Increment counter
        no_passes += 1

        if not params['SILENT']:
            print(no_passes, "passes\tOriginal:",
                  original_snippets, "\tNew:", updated_snippets)


def concatenate():
    """
    Iterates through all snippets in the snippets dictionary and
    concatenates snippets to make larger snippets.

    :return: Nothing.
    """

    concats = params['BNF_GRAMMAR'].concat_NTs

    # Sort snippets keys.
    sorted_keys = sorted(trackers.snippets.keys())

    # Iterate over all snippets.
    for snippet in sorted_keys:

        # Find current snippet info.
        NT = get_NT_from_str(snippet)

        # Get indexes of the current snippet
        indexes = get_num_from_str(snippet)
        start, end = indexes[0], indexes[1]

        # Find if the snippet root (NT) exists anywhere in the
        # concatenation NTs.
        if NT in concats:

            for concat in concats[NT]:
                # Now we're searching for a specific subset of keys in the
                # snippets dictionary.

                # Generate list of only the desired Non Terminals.
                NTs = concat[2]

                if len(NTs) == 1:
                    # This choice leads directly to the parent, check if parent
                    # snippet already exists.

                    # Child is current snippet.
                    child = [[None, trackers.snippets[snippet]]]
                    
                    generate_key_and_check(start, end, concat, child)

                else:
                    # Find the index of the snippet root in the current
                    # concatenation production choice.
                    NT_locs = [i for i, x in enumerate(NTs) if x[0] == NT]

                    for loc in NT_locs:
                        # We want to check each possible concatenation option.
                        # if speck:
    
                        # Set where the original snippet starts and ends on
                        # the target string.
                        if loc == 0:
                            # The current snippet is at the start of the
                            # concatenation attempt.
                            aft, pre = end, None
    
                        elif start == 0 and loc != 0:
                            # The current snippet is at the start of the target
                            # string, but we are trying to concatenate it with
                            # something before it.
                            break
    
                        elif end == len(params['TARGET']) and loc != \
                                NT_locs[-1]:
                            # The current snippet is at the end of the target
                            # string, but we are trying to concatenate it with
                            # something after it.
                            break
    
                        elif loc == len(NTs):
                            # The current snippet is at the end of the
                            # concatenation attempt.
                            aft, pre = None, start
    
                        else:
                            # The current snippet is in the middle of the
                            # concatenation attempt.
                            aft, pre = end, start
    
                        alt_cs = list(range(len(NTs)))
    
                        # Initialise a list of children to be concatenated.
                        children = [[] for _ in range(len(NTs))]
    
                        # Set original snippet into children.
                        children[loc] = [snippet, trackers.snippets[snippet]]
    
                        # Generate ordered list of alternating indexes of Ts
                        # and NTs to concatenate with a given original NT.
                        b = zip_longest(alt_cs[loc:], reversed(alt_cs[:loc]))
                        alt_cs = [x for x in list(sum(b, ())) if x is not None]
                        alt_cs.remove(loc)
    
                        def check_concatenations(alt_cs, pre, aft, idx, children):
                            """
                            Given a list of the indexes of potential children, find
                            snippets which match adjacent portions of the target
                            string that can be used as these children.
    
                            :param alt_cs: An ordered list of indexes of
                            potential Terminals or Non Terminals to
                            concatenate.
                            :param pre: The start index of the overall snippet
                            on the target string.
                            :param aft: The end index of the overall snippet on
                            the target string.
                            :param children: A list of children to be concatenated.
                            :param idx: The index of the current child.
                            :return: The same inputs, in the same order.
                            """

                            if idx < len(alt_cs):
    
                                # Take the next available unexpanded item from the
                                # list.
                                child_idx = alt_cs[idx]
                                child = NTs[child_idx]

                                # Increment counter.
                                idx += 1
    
                                if pre is None:
                                    # Then we are starting with an NT which
                                    # directly follows the current NT.
    
                                    if child[1] == "T":
                                        # Then we can immediately check if this
                                        # concatenation T is legally allowed
                                        # follow the current NT in the target
                                        # string.
    
                                        # Get output to check for match.
                                        check = child[0]
    
                                        # Get portion of target string to match.
                                        end_point = aft + len(check)
    
                                        target = params['TARGET'][aft:end_point]
    
                                        if target == check:
                                            # The current terminal matches the same
                                            # location on the target string.
    
                                            # Generate fake key for snippets dict.
                                            key = str([aft, end_point])
    
                                            # Increment aft phenotype counter.
                                            aft += len(check)
    
                                            # Create new tree from this terminal.
                                            T_tree = tree.Tree(check, None)
    
                                            # Add to children.
                                            children[child_idx] = [key, T_tree]
    
                                            if alt_cs:
                                                # Recurse to find the next piece of
                                                # the puzzle.
                                                check_concatenations(alt_cs, pre,
                                                                     aft, idx,
                                                                     children)
    
                                    elif child[1] == "NT":
                                        # Check to see if there are any snippets
                                        # which can be concatenated to the current
                                        # block.
    
                                        # This NT comes after the original NT.
                                        str_aft = str(aft)
    
                                        # Find all potential snippets which
                                        # match our criteria.
                                        matches = [v for v in sorted_keys if
                                                   v.split()[0][1:-1] ==
                                                   str_aft and v.split()[2] ==
                                                   child[0]]
    
                                        # Create a copy of this marker otherwise
                                        # each match will over-write it.
                                        aft_c = copy(aft)
    
                                        for match in matches:
                                            # Iterate over all potential matches.
    
                                            # Calculate length of match string.
                                            str_len = get_num_from_str(match)
    
                                            # Increment appropriate phenotype
                                            # counter.
                                            aft_c = aft + str_len[1] - str_len[0]
    
                                            # Add to children.
                                            children[child_idx] = [match,
                                                              trackers.snippets[
                                                                  match]]
    
                                            if alt_cs:
                                                # Recurse to find the next piece of
                                                # the puzzle.
                                                check_concatenations(alt_cs, pre,
                                                                     aft_c, idx,
                                                                     children)
    
                                elif aft is None:
                                    # Then we are starting with an NT which
                                    # directly precedes the current NT.
    
                                    if child[1] == "T":
                                        # Then we can immediately check if this
                                        # concatenation T is legally allowed
                                        # follow the current NT in the target
                                        # string.
    
                                        # Get output to check for match.
                                        check = child[0]
    
                                        # Get portion of target string to match.
                                        start_point = pre - len(check)
    
                                        target = params['TARGET'][
                                                 start_point:pre]
    
                                        if target == check:
                                            # The current terminal matches the same
                                            # location on the target string.
    
                                            # Generate fake key for snippets dict.
                                            key = str([start_point, pre])
    
                                            # Increment pre phenotype counter.
                                            pre -= len(check)
    
                                            # Create new tree from this terminal.
                                            T_tree = tree.Tree(check, None)
    
                                            # Add to children.
                                            children[child_idx] = [key, T_tree]
    
                                            if alt_cs:
                                                # Recurse to find the next piece of
                                                # the puzzle.
                                                check_concatenations(alt_cs, pre,
                                                                     aft, idx,
                                                                     children)
    
                                    elif child[1] == "NT":
                                        # Check to see if there are any snippets
                                        # which can be concatenated to the current
                                        # block.
    
                                        # This NT comes after the original NT.
                                        str_pre = str(pre)
    
                                        # Find all potential snippets which
                                        # match our criteria.
                                        matches = [v for v in sorted_keys if
                                                   v.split()[1][:-1] ==
                                                   str_pre and v.split()[2] ==
                                                   child[0]]
    
                                        # Create a copy of this marker otherwise
                                        # each match will over-write it.
                                        pre_c = copy(pre)
    
                                        for match in matches:
                                            # Iterate over all potential matches.
    
                                            # Calculate length of match string.
                                            str_len = get_num_from_str(match)
    
                                            # Increment appropriate phenotype
                                            # counter.
                                            pre_c = pre - str_len[1] + str_len[0]
    
                                            # Add to children.
                                            children[child_idx] = [match,
                                                              trackers.snippets[
                                                                  match]]
    
                                            if alt_cs:
                                                # Recurse to find the next piece of
                                                # the puzzle.
                                                check_concatenations(alt_cs, pre_c,
                                                                     aft, idx,
                                                                     children)
    
                                else:
                                    # Our starting NT is somewhere in the middle
                                    # of the proposed concatenation.
    
                                    if child[1] == "T":
                                        # Then we can immediately check if this
                                        # concatenation T is legally allowed be
                                        # where it wants to be.
    
                                        # Get output to check for match.
                                        check = child[0]
    
                                        # Get portion of target string to match.
                                        if child_idx > loc:
                                            # This T comes after the original NT.
                                            start_point = aft
                                            end_point = start_point + len(check)
    
                                        else:
                                            # This T comes before the original NT.
                                            start_point = pre - len(check)
                                            end_point = pre
    
                                        target = params['TARGET'][
                                                 start_point:end_point]
    
                                        if target == check:
                                            # The current terminal matches the same
                                            # location on the target string.
    
                                            # Increment appropriate phenotype
                                            # counter.
                                            if child_idx > loc:
                                                # This T comes after the original
                                                # NT.
                                                aft += len(check)
    
                                            else:
                                                # This T comes before the original
                                                # NT.
                                                pre -= len(check)
    
                                            # Generate fake key for snippets dict.
                                            key = str([start_point, end_point])
    
                                            # Create new tree from this terminal.
                                            T_tree = tree.Tree(check, None)
    
                                            # Add to children.
                                            children[child_idx] = [key, T_tree]
    
                                            if alt_cs:
                                                # Recurse to find the next piece of
                                                # the puzzle.
                                                check_concatenations(alt_cs, pre,
                                                                     aft, idx,
                                                                     children)
    
                                    elif child[1] == "NT":
                                        # Check to see if there are any snippets
                                        # which can be concatenated to the current
                                        # block.
    
                                        # Get portion of target string to match.
                                        if child_idx > loc:
                                            # This NT comes after the original NT.
                                            str_aft = str(aft)
                                            matches = [v for v in sorted_keys if
                                                       v.split()[0][1:-1] ==
                                                       str_aft and v.split()[2] ==
                                                       child[0]]
    
                                        else:
                                            # This NT comes before the original NT.
                                            str_pre = str(pre)
                                            matches = [v for v in sorted_keys if
                                                       v.split()[1][:-1] ==
                                                       str_pre and v.split()[2] ==
                                                       child[0]]
    
                                        # Create copies of this markers otherwise
                                        # each match will over-write them.
                                        pre_c, aft_c = copy(pre), copy(aft)
    
                                        for match in matches:
                                            # Iterate over all potential matches.
    
                                            # Calculate length of match string.
                                            str_len = get_num_from_str(match)
    
                                            # Increment appropriate phenotype
                                            # counter.
                                            if child_idx > loc:
                                                # This NT comes after the original
                                                # NT.
                                                aft_c = aft + str_len[1] - str_len[0]
    
                                            else:
                                                # This NT comes before the original
                                                # NT.
                                                pre_c = pre - str_len[1] + str_len[0]
    
                                            # Add to children.
                                            children[child_idx] = [match,
                                                              trackers.snippets[
                                                                  match]]
    
                                            if alt_cs:
                                                # Recurse to find the next piece of
                                                # the puzzle.
                                                check_concatenations(alt_cs, pre_c,
                                                                     aft_c, idx,
                                                                     children)
    
                            elif all([i != [] for i in children]):
                                # We have compiled a full set of potneital
                                # children to concatenate. Generate a key and check
                                # if it exists.
                                generate_key_and_check(pre, aft, concat,
                                                       children)
    
                        # Check whether a concatenation can be performed.
                        check_concatenations(alt_cs, pre, aft, 0, children)

    return len(trackers.snippets)


def generate_key_and_check(pre, aft, concat, children):
    """
    Will generate a snippet key and check if it exists in the repository. If
    snippet is not in the repository, adds it.

    :param pre: The start index of the overall snippet on the target string.
    :param aft: The end index of the overall snippet on the target string.
    :param concat: The information necessary to concatenate a list of snippets.
    Includes the root NT that will form the new root node of the concatenated
    snippet.
    :param children: A dictionary containing the derivation trees of all
    components of the snippet to be concatenated.
    :return: Nothing.
    """

    if pre is None:
        pre = get_num_from_str(children[0][0])[0]

    if aft is None:
        aft = get_num_from_str(children[-1][0])[1]

    # Generate key for proposed concatenation
    new_key = " ".join([str([pre, aft]), concat[1]])

    if new_key in trackers.snippets:
        # No need to concatenate as a perfectly good
        # solution already exists.
        pass

    else:

        # Create list of children.
        children = [i[1] for i in children]

        # We can generate a new snippet by concatenating
        # two existing snippets.
        create_snippet(concat[1], children, concat[0], new_key)


def remove_old_snippets():
    """
    Iterate over the snippets repository and remove snippets which are
    sub-trees of larger snippets as these snippets are useless now.

    :return: Nothing.
    """

    for snippet in sorted(trackers.snippets.keys()):
        # Iterate over all snippets.

        # Get indices of snippet location on target string.
        indices = get_num_from_str(snippet)

        encompassing_snippets = [snip for snip in sorted(
            trackers.snippets.keys()) if get_num_from_str(snip)[0] <
                                 indices[0] and get_num_from_str(snip)[1] >
                                 indices[1]]

        for snip in encompassing_snippets:
            del trackers.snippets[snip]


def create_snippet(parent, children, choice, key):
    """
    Given a parent NT and a list of child trees, create a new tree that acts as
    the parent of the given children. Generates this tree as a snippet and
    adds the new snippet to the trackers.snippets library.

    :param parent: A non-terminal root.
    :param children: A list of derivation tree instances.
    :param choice: The chosen production choice.
    :param key: A new key for the trackers.snippets dictionary.
    :return: Nothing.
    """

    # Initialise new instance of the tree class to act as new snippet.
    new_tree = tree.Tree(parent, None)

    # Generate a codon to match the given production choice.
    new_tree.codon = generate_codon(parent, choice)

    # Add the children to the new node
    for child in children:
        new_tree.children.append(child)

        # Set the parent of the child to the new node
        child.parent = new_tree

    # Add new snippet to snippets dictionary
    trackers.snippets[key] = new_tree


def get_num_from_str(string):
    """
    Given a string of a snippet, return the indexes of that snippet.

     in: '[1, 2] <RE>'

     out: [1, 2]

    :param string: A string defining a snippet.
    :return: The indexes of that snippet.
    """

    # Get index portion of string
    # try:
    index = re.findall("\[\d+, \d+\]", string)
    # except TypeError:
    #     print("TypeError.\n", string)
    #     quit()
    return eval(index[0])


def get_NT_from_str(string):
    """
    Given a string of a snippet, return the NT of that snippet.

     in: '[1, 2] <RE>'

     out: '<RE>'

    :param string: A string defining a snippet.
    :return: The NT of that snippet.
    """

    # Get index portion of string
    index = re.findall("\<.+\>", string)
    return index[0]


def check_snippets_for_solution():
    """
    Check the snippets repository to see if we have built up the correct
    solution yet.

    :return: An individual representing the correct solution if it exists,
    otherwise None.
    """

    # Initialise None biggest snippet
    biggest_snippet = [0, None]

    for snippet in sorted(trackers.snippets.keys()):
        # Check each snippet to find the largest one.

        # Find length of snippet
        index = get_num_from_str(snippet)
        length = index[1] - index[0]

        if length > biggest_snippet[0]:
            # We have a new biggest snippet.
            biggest_snippet = [length, snippet]

    largest_snippet = get_output(trackers.snippets[biggest_snippet[1]])
    largest_indexes = get_num_from_str(biggest_snippet[1])
    spaces = "".join([" " for _ in range(largest_indexes[0] - 1)])

    if not params['SILENT']:
        print("\nTarget:         ", params['TARGET'])
        if spaces:
            print("Largest snippet:", spaces, largest_snippet)
        else:
            print("Largest snippet:", largest_snippet)
    
        if largest_snippet != params['TARGET']:
            print("Snippet key:    ", biggest_snippet[1])

    if largest_snippet == params['TARGET']:
        # We have a perfect match

        # Generate individual that represents the perfect solution.
        ind = individual.Individual(None, trackers.snippets[biggest_snippet[
            1]])

        # Return ind.
        return ind
