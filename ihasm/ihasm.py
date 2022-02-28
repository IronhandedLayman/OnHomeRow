#!/usr/bin/env python

import pprint
from pyparsing import Literal, Combine, Group, SkipTo, LineEnd, OneOrMore, Word, StringEnd
from pyparsing import QuotedString, Opt, LineStart, oneOf, StringStart
from pyparsing import delimited_list
from pyparsing import alphas, alphanums
from pyparsing import ParseException, Suppress, ParserElement, Forward
from pyparsing import infixNotation, opAssoc
from pyparsing import Regex
import argparse as ap

VERSION="0.0"

ParserElement.enable_packrat()

# Start off with the building blocks
# an Identifier is simply an alphanumeric word.
IDENTIFIER=Word(alphas, alphanums)
OPCODE=Word(alphas)

NUMBER = Regex(r'(0[bx])?[0-9a-f]+')
VARIABLE = Literal('$')+Word(alphanums)
REGISTER = Literal('%')+Word(alphanums)
OPERAND = NUMBER | VARIABLE | REGISTER

NOTOP = Literal('^') #bitwise not
TWOSOP = Literal('~') #two's compliment

ADDOP = Literal('+')
SUBOP = Literal('-')
MULTOP = Literal('*')
ANDOP = Literal('&')
OROP = Literal('|')
RLOP = Literal('<<')
RROP = Literal('>>')

EXPRESSION = infixNotation(
        OPERAND,
        [ 
            (NOTOP,1,opAssoc.RIGHT,None ),
            (TWOSOP,2,opAssoc.LEFT,None),
            (ADDOP,2,opAssoc.LEFT,None ),
            (SUBOP,2,opAssoc.LEFT,None ),
            (MULTOP,2,opAssoc.LEFT,None),
            (ANDOP,2,opAssoc.LEFT,None ),
            (OROP,2,opAssoc.LEFT,None ),
            (RLOP,2,opAssoc.LEFT,None ),
            (RROP,2,opAssoc.LEFT,None ),
        ],
)


EXPRESSIONS = delimited_list(EXPRESSION)

# aaaaaaa,b,c,d,e
#          
LDLIM = Suppress(LineEnd()) 

# pragmas cannot have comments. They are specifically the hash symbol, a pragma identifier, and then the value the pragma has.
PRAGMA_START=Literal("#")
PRAGMA_IDENTIFIER=IDENTIFIER("pragma_identifier")
PRAGMA_VALUE=IDENTIFIER("pragma_value")

PRAGMA=Group(Suppress(PRAGMA_START)+PRAGMA_IDENTIFIER+PRAGMA_VALUE+LDLIM)

# Comments start with a semicolon, always extend to end of line. 
COMMENT_START = Literal(";")
COMMENT_LINE = Suppress(COMMENT_START) + Group(SkipTo(LineEnd())("comment")) + LDLIM

# Bundled comments into EOL to get comments on any line for free.
EOL = COMMENT_LINE | LDLIM

# Data lines start with the literal .data and continue with a string of hexadecimal words
DATA_START = Literal(".data")
DATA_LINE = Suppress(DATA_START) + Group(SkipTo(EOL)("data")) + EOL

# Labels need to be a legal identifier
LABEL_START = Literal(".label")
LABEL_LINE = Suppress(LABEL_START) + Group(IDENTIFIER("label")) + EOL

# Ascii lines need to have a quoted string in it
ASCII_START = Literal(".ascii")
ASCII_LINE = Suppress(ASCII_START) + Group(QuotedString("\"")("text")) + EOL

# Code lines:
# a code line is in the form OPCODE EXPR1,EXPR2,EXPR3... EOL as above
CODE_LINE = Group(OPCODE("opcode") + Opt(EXPRESSIONS)("args")) + EOL

IHASM_PARSER = StringStart() + OneOrMore(PRAGMA | COMMENT_LINE | DATA_LINE | LABEL_LINE | ASCII_LINE | CODE_LINE) + StringEnd()

def demo(args):
    for input_line in [
            "#arch SBNO",
            "; this is just a comment",
            ".data 01 10 FE F6 00 A5 A5 A5 ; a comment at the end of the line",
            ".label main ; as a test",
            ".ascii \"Hello world!\"",
            "SBN $test1+4, $pc+4",
            "OUT"
            ]:
        try:
            print(f'Code line: [[{input_line}]]')
            ihasm_ast = IHASM_PARSER.parseString(input_line)
            print(f'Parses as: {repr(ihasm_ast)}')
            print()
        except ParseException as err:
            print(err.explain())    

def parse_file(args):
    ihasm_ast = None
    pp = pprint.PrettyPrinter(indent=2)
    try:
        ihasm_ast = IHASM_PARSER.parseFile(args.source_file)
        print("File parses as:")
        pp.pprint(ihasm_ast)
    except ParseException as err:
        print(err.explain())
        exit(1)

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

    if args is not None and 'func' in args:
        args.func(args)
    else:
        argp.print_usage()

if __name__ == "__main__":
    main()