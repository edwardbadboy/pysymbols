#!/usr/bin/python
# experiment symtable module in Python.
import sys
from sys import stdout, stderr, argv, exit
from pprint import pprint
import symtable


class indenter(object):
    _printInd = False

    def __init__(self, indent, rawOut=stdout):
        self._indent = indent
        self._rawOut = rawOut

    def write(self, str_):
        if indenter._printInd == True:
            self._rawOut.write('\t' * self._indent)
            indenter._printInd = False
        if '\n' in str_:
            indenter._printInd = True
        self._rawOut.write(str_)


def dumpSymtable(code, fname):
    table = symtable.symtable(code, fname, "exec")
    printSymtable(table, 0)


def printSymtable(table, indent):
    ind = indenter(indent, stderr)
    ind.write('%s-%s\n' % (table.get_name(), table.get_type()))
    pprint(map(sym2str, table.get_symbols()), ind)
    ind.write("\n")
    for nested in table.get_children():
        printSymtable(nested, indent + 1)


def sym2str(sym):
    r = "%s r:%r a:%r f:%r" % (
            sym.get_name(), sym.is_referenced(), sym.is_assigned(),
            sym.is_free())
    return r


if __name__ == "__main__":
    if len(argv) != 2:
        sys.stderr.write("Usage: %s aPythonFile.py\n" % argv[0])
        exit(1)
    with open(argv[1]) as inFile:
        code = inFile.read()
    dumpSymtable(code, argv[1])
