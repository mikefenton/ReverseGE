import argparse


def parse_cmd_args(arguments):
    """
    Parser for command line arguments specified by the user. Specified command
    line arguments over-write parameter file arguments, which themselves
    over-write original values in the algorithm.parameters.params dictionary.

    The argument parser structure is set up such that each argument has the
    following information:

        dest: a valid key from the algorithm.parameters.params dictionary
        type: an expected type for the specified option (i.e. str, int, float)
        help: a string detailing correct usage of the parameter in question.

    Optional info:

        default: The default setting for this parameter.
        action : The action to be undertaken when this argument is called.

    NOTE: You cannot add a new parser argument and have it evaluate "None" for
    its value. All parser arguments are set to "None" by default. We filter
    out arguments specified at the command line by removing any "None"
    arguments. Therefore, if you specify an argument as "None" from the
    command line and you evaluate the "None" string to a None instance, then it
    will not be included in the eventual parameters.params dictionary. A
    workaround for this would be to leave "None" command line arguments as
    strings and to eval them at a later stage.

    :param arguments: Command line arguments specified by the user.
    :return: A dictionary of parsed command line arguments, along with a
    dictionary of newly specified command line arguments which do not exist
    in the params dictionary.
    """

    # Initialise parser
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Welcome to ReverseGE - Help
        -------------------
        The following are the available command line args:""")

    # GRAMMAR FILE
    parser.add_argument('--grammar_file', dest='GRAMMAR_FILE', type=str,
                        help='Sets the grammar to be used, requires string.')
    
    # TARGET
    parser.add_argument('--target', dest='TARGET', type=str,
                        help='Target string to reverse-engineer.')

    # PRINTING
    parser.add_argument('--silent', dest='SILENT', default=None,
                        action='store_true',
                        help='Prevents any output from being printed to the '
                             'command line.')
    
    # Parse command line arguments using all above information.
    args, unknown = parser.parse_known_args(arguments)

    # All default args in the parser are set to "None". Only take arguments
    # which are not "None", i.e. arguments which have been passed in from
    # the command line.
    cmd_args = {key: value for key, value in vars(args).items() if value is
                not None}

    return cmd_args, unknown
