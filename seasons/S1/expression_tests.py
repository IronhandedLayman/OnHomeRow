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

def tokenAction(something):
    print("Hey look a token! " + repr(something))

def recognizeInteger(x):
    return int(x[0])
    

NUMBER = Regex(r'[1-9][0-9]*').setParseAction(recognizeInteger)
ADDOP = Literal('+').setParseAction(tokenAction)
SUBOP = Literal('-').setParseAction(tokenAction)

def addAction(ops):
    return ops[0][0] + ops[0][2] 

def subAction(ops):
    print(repr(ops))
    return ops[0][0] - ops[0][2] 

EXPR = infixNotation(
        NUMBER,
        [
            (ADDOP, 2, opAssoc.RIGHT, addAction),
            (SUBOP, 2, opAssoc.LEFT, subAction),
        ],
)

def main():
    print(repr(EXPR.parseString("1-2-3-4-5")))


if __name__=="__main__":
    main()
