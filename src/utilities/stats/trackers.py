"""Utilities for tracking progress of runs, including time taken per
generation, fitness plots, fitness caches, etc."""

snippets = {}
# This dict stores the snippets for compiling a complete solution. The key for
# each entry is the portion of the target string on which the output
# matches, along with the root node of the subtree. The value is the subtree.
