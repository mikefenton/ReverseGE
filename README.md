------------
#Introduction
------------

ReverseGE is a GE-specific LR parser. Given a target string and a 
grammar which can generate the target string, ReverseGE will output a 
genome which will map to that same target string using that same 
grammar. 

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
    $ python LR_Parser.py

This will run an example problem which parses the following target 
string:

    Hello world!

##Target String

The target string can be set by passing in the flag:
 
    --target STRING
    
from the command line, where `STRING` is a string representing the 
target. 

The target string can also be set directly in the parameters
dictionary in `src.algorithm.parameters.params`.

##Grammar File

The grammar file can be specified by passing in the flag:

    --grammar_file GRAMMAR
    
from the command line, where `GRAMMAR` is a string of the name of the
grammar file to be used. Grammar files are located in the grammars 
folder.

The grammar file can also be set directly in the parameters
dictionary in `src.algorithm.parameters.params`.

*__NOTE__ that the name of the grammar file requires the full file*
*extension.*

To see a full list of command line flags, just run the following:

    $ python LR_Parser.py --help
