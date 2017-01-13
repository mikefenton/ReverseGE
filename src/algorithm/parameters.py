from os import path


"""Algorithm parameters"""
params = {

        # Set grammar file
        'GRAMMAR_FILE': "Vladislavleva4.bnf",

        # Specify target for target problems
        'TARGET': "plog(np.sin(np.sin(psqrt(x[3]+np.exp(np.tanh(np.sin(np.exp(x[4]))))*plog(pdiv(x[1]*pdiv(x[3],plog(x[1]))-psqrt(np.sin(np.sin(np.exp(70.06)))),plog(x[1])*np.tanh(psqrt(x[4])*plog(np.tanh(x[0])))*39.80-x[1]+plog(np.sin(np.tanh(x[0])*x[0]))))))))"

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
