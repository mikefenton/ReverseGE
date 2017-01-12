------------
#Introduction
------------

ReverseGE allows you to reverse-engineer a target string. Given a 
grammar which can generate the target string, ReverseGE will output a 
genome which will map to that same target string using that grammar. 
While the process is deterministic, and as such will produce the same
derivation tree structure, codons in the genome are randomly chosen from
within a specified range. This means that multiple genomes will map to
the same solution (i.e. running ReverseGE multiple times will result in 
multiple different genomes, all of which map to the same solution tree).

ReverseGE is based on PonyGE (https://github.com/jmmcd/ponyge2), and as 
such genomes produced by ReverseGE can be used to seed solutions in 
PonyGE.

The ReverseGE development team can be contacted at:

    Michael Fenton <michaelfenton1@gmail.com>

ReverseGE is copyright (C) 2017.

------------
#Requirements
------------

ReverseGE requires Python 3.5 or higher.

--------------
#Running ReverseGE
--------------

We don't provide any setup script. You can run an example problem just 
by typing:

    $ cd src
    $ python ReverseGE.py

This will run an example problem which reverse engineers the target 
symbolic regression string:

    plog(np.sin(np.sin(psqrt(x[3]+np.exp(np.tanh(np.sin(np.exp(x[4]))))*plog(pdiv(x[1]*pdiv(x[3],plog(x[1]))-psqrt(np.sin(np.sin(np.exp(70.06)))),plog(x[1])*np.tanh(psqrt(x[4])*plog(np.tanh(x[0])))*39.80-x[1]+plog(np.sin(np.tanh(x[0])*x[0]))))))))

##Target String

The target string can be set by passing in the flag:
 
    --target [STRING]
    
from the command line, where `[STRING]` is a string representing the 
target. 

The target string can also be set directly in the parameters
dictionary in `src.algorithm.parameters.params`.

##Grammar File

The grammar file can be specified by passing in the flag:

    --grammar_file [GRAMMAR]
    
from the command line, where `[GRAMMAR]` is a string of the name of the
grammar file to be used. Grammar files are located in the grammars 
folder.

The grammar file can also be set directly in the parameters
dictionary in `src.algorithm.parameters.params`.

*__NOTE__ that the name of the grammar file requires the full file*
*extension.*

##Codon Size

The only parameter available to the user is to select the maximum codon 
size. This value specifies the range from which each codon in the genome
is selected. This is the only random step in the entire algorithm, and
has no bearing on the outcome of the solution (since the use of grammars
implies a many-to-one mapping).

There are a number of flags that can be used for passing values via the
command-line. To see a full list of these just run the following:

    $ python load_solution.py --help
