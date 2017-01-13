from os import path


"""Algorithm parameters"""
params = {

        # Set grammar file
        'GRAMMAR_FILE': "regex.bnf",

        # Specify target for target problems
        'TARGET': "((2[0-5]|1[0-9]|[0-9])?[0-9]\.){3}((2[0-5]|1[0-9]|[0-9])?[0-9])"

}


def set_params(command_line_args):
    """
    This function parses all command line arguments specified by the user.
    If certain parameters are not set then defaults are used (e.g. random
    seeds, elite size). Sets the correct imports given command line
    arguments. Sets correct grammar file and fitness function. Also
    initialises save folders and tracker lists in utilities.trackers.

    :param command_line_args: Command line arguments specified by the user.
    :return: Nothing.
    """

    from representation import grammar
    import utilities.algorithm.command_line_parser as parser

    cmd_args, unknown = parser.parse_cmd_args(command_line_args)

    # Join original params dictionary with command line specified arguments.
    # NOTE that command line arguments overwrite all previously set parameters.
    params.update(cmd_args)

    # Parse grammar file and set grammar class.
    params['BNF_GRAMMAR'] = grammar.Grammar(path.join("..", "grammars",
                                            params['GRAMMAR_FILE']))
