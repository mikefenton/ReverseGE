from algorithm.mapper import mapper


class Individual(object):
    """
    A GE individual.
    """

    def __init__(self, genome, ind_tree):
        """
        Initialise an instance of the individual class (i.e. create a new
        individual).

        :param genome: An individual's genome.
        :param ind_tree: An individual's derivation tree, i.e. an instance
        of the representation.tree.Tree class.
        """

        # The individual needs to be mapped from the given input
        # parameters.
        self.phenotype, self.genome, self.tree, self.nodes, self.invalid, \
            self.depth, self.used_codons = mapper(genome, ind_tree)
