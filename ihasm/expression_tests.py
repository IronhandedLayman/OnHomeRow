#!/usr/bin/env python

import pprint
import pyparsing
from pyparsing import Literal, Combine, Group, SkipTo, LineEnd, OneOrMore, Word, StringEnd
from pyparsing import QuotedString, Opt, LineStart, oneOf, StringStart
from pyparsing import delimited_list
from pyparsing import alphas, alphanums, Regex
from pyparsing import ParseException, Suppress, ParserElement, Forward
from pyparsing import infixNotation, opAssoc
import argparse as ap

# pyparsing.enable_left_recursion()
ParserElement.enable_packrat()

NUMBER = Regex(r'[1-9][0-9]*')
ADDOP = Literal('+')
SUBOP = Literal('-')

EXPR = infixNotation(
        NUMBER,
        [
            (ADDOP, 2, opAssoc.RIGHT, None),
            (SUBOP, 2, opAssoc.RIGHT, None),
        ],
)

def main():
    print("hi")
    print(repr(EXPR.parseString("1 + 2 + 3")))


if __name__=="__main__":
    main()
