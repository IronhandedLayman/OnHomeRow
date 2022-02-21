#!/usr/bin/env python

from pyparsing import Literal, Combine, Group, SkipTo, LineEnd, OneOrMore, Word, StringEnd
from pyparsing import QuotedString, Opt, LineStart
from pyparsing import delimited_list
from pyparsing import alphas, alphanums
from pyparsing import ParseException
import argparse as ap

VERSION="0.0"

PARSER_LANG="""
#arch SBNO 
TODO:    ; this is a comment in a mature assembler
TODO:    section commands like .label test1
TODO:    binary data lines like  .data 01 10 FE F6 00 a5 a5 a5
TODO:    ascii data lines like .ascii "hi there"
TODO:    code lines like SBN a, b
TODO:    inline expressions and pre-calculated values
"""

# Start off with the building blocks
# an Identifier is simply an alpha word. I will add support for alphanumeric identifiers later.
IDENTIFIER=Word(alphas, alphanums)
OPCODE=Word(alphas)
EXPRESSION=Word(alphanums+"+-*/%$")

# pragmas cannot have comments. They are specifically the hash symbol, a pragma identifier, and then the value the pragma has.
PRAGMA_START=Literal("#")
PRAGMA_IDENTIFIER=IDENTIFIER("pragma_identifier")
PRAGMA_VALUE=IDENTIFIER("pragma_value")

PRAGMA=Combine(PRAGMA_START+PRAGMA_IDENTIFIER)+PRAGMA_VALUE+LineEnd()

# Comments start with a semicolon, always extend to end of line. 
COMMENT_START = Literal(";")
COMMENT_LINE = COMMENT_START + Group(SkipTo(LineEnd()))("comment") + LineEnd()

# Bundled comments into EOL to get comments on any line for free.
EOL = OneOrMore(COMMENT_LINE | LineEnd())

# Data lines start with the literal .data and continue with a string of hexadecimal words
DATA_START = Literal(".data")
DATA_LINE = DATA_START + Group(SkipTo(EOL))("data")

# Labels need to be a legal identifier
LABEL_START = Literal(".label")
LABEL_LINE = LABEL_START + IDENTIFIER("label") + EOL

# Ascii lines need to have a quoted string in it
ASCII_START = Literal(".ascii")
ASCII_LINE = ASCII_START + Group(QuotedString("\""))("text") + EOL

# Code lines:
# a code line is in the form OPCODE EXPR1,EXPR2,EXPR3... EOL as above
CODE_LINE = LineStart() + OPCODE("opcode") + Opt(delimited_list(EXPRESSION)("args")) + EOL

IHASM_PARSER = OneOrMore(PRAGMA | COMMENT_LINE | DATA_LINE | LABEL_LINE | ASCII_LINE | CODE_LINE) + StringEnd()

def demo(args):
    for input_line in [
            "#arch SBNO",
            "; this is just a comment",
            ".data 01 10 FE F6 00 A5 A5 A5 ; a comment at the end of the line",
            ".label main ; as a test",
            "SBN $test1+4, $pc+4"
            ]:
        ihast_ast = None
        try:
            ihasm_ast = IHASM_PARSER.parseString(input_line)
        except ParseException as err:
            print(err.explain())    
        if ihast_ast is not None:
            print(f'Code line: [[{input_line}]]')
            print(f'Parses as: {repr(ihasm_ast)}')
            print()

def parse_file(args):
    ihasm_ast = None
    try:
        ihasm_ast = IHASM_PARSER.parseFile(args.source_file)
    except ParseException as err:
        print(err.explain())
        exit(1)
    if ihasm_ast is not None:
        print("file parsed!")
        print(repr(ihasm_ast))

def main():
    print(f"ihasm version {VERSION}")
    argp = ap.ArgumentParser(prog='IHASM',
            description="An assembler for toy computers. DO NOT USE IN PRODUCTION.")
    subp = argp.add_subparsers()

    parsep = subp.add_parser(name='parse', description='parses a file and exits')
    parsep.add_argument('source_file', type=ap.FileType('r'), help='The source .ihasm file to parse')
    parsep.set_defaults(func=parse_file)
    demop = subp.add_parser(name='demo', description='tests some use cases of the assembler')
    demop.set_defaults(func=demo)
    args = None

    try:
        args = argp.parse_args()
    except:
        exit(1)

    if args is not None:
        args.func(args)


if __name__ == "__main__":
    main()
