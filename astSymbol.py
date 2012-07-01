#!/usr/bin/python
# report warning for similar names in a Python script.
# parse Python file into ast, then get names in the ast,
# then detect similar names.
import sys
from sys import argv
import ast
from pprint import pprint

# pip install python-Levenshtein
from Levenshtein import distance

_short_name_len = 2
_similar_len = 2


class getNames(ast.NodeVisitor):
    def __init__(self):
        self._names = {}

    def children_visit(self, parent):
        for child in ast.iter_child_nodes(parent):
            self.visit(child)

    def addName(self, name, node):
        entry = (name, node.__class__.__name__, node.lineno, node.col_offset)
        idstr = entry[0]
        try:
            idset = self._names[idstr]
        except KeyError:
            self._names[idstr] = set()
            idset = self._names[idstr]
        idset.add(entry)

    def getNames(self):
        return self._names

    # TODO: add support for finding names in 'visit_import' and other
    # statements.

    def visit_Name(self, node):
        self.addName(node.id, node)
        return self.children_visit(node)

    def visit_FunctionDef(self, node):
        self.addName(node.name, node)
        return self.children_visit(node)

    def visit_ClassDef(self, node):
        self.addName(node.name, node)
        return self.children_visit(node)

    def visit_Attribute(self, node):
        self.addName(node.attr, node)
        return self.children_visit(node)


def getSimilars(names):
    keys = names.keys()
    similars = {}
    for i, key in enumerate(keys):
        if len(key) <= _short_name_len:
            continue
        for j, sub in enumerate(keys[i + 1:], i + 1):
            if distance(key, sub) <= _similar_len:
                addSimilar(similars, key, sub)
    return similars


def getSimilarEntry(s, key):
    try:
        it = s[key]
    except KeyError:
        s[key] = {'similars': [], 'refs': []}
        it = s[key]
    return it


def addSimilar(s, key, sub):
    entry = getSimilarEntry(s, key)
    for ref in entry['refs']:
        if sub in s[ref]['similars']:
            return
    entry['similars'].append(sub)

    getSimilarEntry(s, sub)['refs'].append(key)


if __name__ == '__main__':
    if len(argv) != 2:
        sys.stderr.write('Usage: %s aPyFile.py\n' % argv[0])
        sys.exit(1)

    with open(argv[1]) as inFile:
        codestr = inFile.read()
    pyast = ast.parse(codestr, argv[1], 'exec')
    pyast = ast.fix_missing_locations(pyast)
    names = getNames()
    names.visit(pyast)
    pprint(
        [(key, sorted(entry['similars']))
         for key, entry in getSimilars(names.getNames()).items()
         if entry['similars']])
