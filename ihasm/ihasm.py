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

## the architecture class to register

class LEGArch:

    OPCODE_MAP={
            "ADD":0, 
            "SUB":1, 
            "AND":2, 
            "OR":3, 
            "NOT":4, 
            "XOR":5,
            "JEQ":32, 
            "JNE":33, 
            "JLT":34, 
            "JLE":35, 
            "JGR":36, 
            "JGE":37,
            "LOAD":8, 
            "SAVE":9, 
            "BREAK":10,
    }

    REGISTER_MAP={
            "r0":0,
            "r1":1,
            "r2":2,
            "r3":3,
            "r4":4,
            "r5":5,
            "pc":6,
            "io":7
    }

    def __init__(self, reg_name):
        self.reg_name = reg_name
        self.variables = {}
        self.pragmas = {}

    def get_name(self):
        return reg_name

    def build(self, ast, pragmas):
        self.pragmas = pragmas
        #grab variables and parse semantics
        self.sem_parse1(ast) 
        return None

    def sem_parse1(self, ast, blen=0):
        if ast.children is not None:
            for ast_child in ast.children:
                blen = self.sem_parse(ast_child, blen)
        termtype = ast.termType
        if termtype=="asm":
            return blen
        elif termtype=="label":
            self.variables[ast.elem]=blen
            return blen
        elif termtype=="ascii":
            return blen + len(ast.elem)
        elif termtype=="data":
            return blen + len(ast.elem)
        elif termtype=="opcode":
            if ast.elem not in LEGArch.OPCODE_MAP:
                raise Exception('Illegal opcode {ast.elem}')
            return blen+4
        elif termtype=="number":
            if ast.elem < 0 or ast.elem > 255:
                raise Exception('Illegal number {ast.elem}')
            return blen
        elif termtype=="variable":
            return blen
        elif termtype=="register":
            if ast.elem not in LEGArch.OPCODE_MAP:
                raise Exception('Illegal opcode {ast.elem}')
            return blen



## All registered architectures below

ihasm_arch={}
ihasm_arch["LEG"]=LEGArch("LEG")

## the AST of the IHASM assembler blocks

class IhasmTree:
    def __init__(self, termType, elem, children=None, label=None, comment=None, loc=None):
        self.source_location = loc
        self.comment = comment
        self.contents = elem
        self.termType = termType 
        self.children = children
        self.label = label

    def __repr__(self):
        if self.label is not None:
            return f'@{self.label}[{self.termType}]:[{self.contents}]'
        elif self.children is not None:
            return f'[{self.termType}]:[{self.contents}]({self.children})'
        else:
            return f'[{self.termType}]:[{self.contents}]'


ihasm_pragmas = {}

## Parser elements below

ParserElement.enable_packrat()

# Start off with the building blocks
# an Identifier is simply an alphanumeric word.
IDENTIFIER=Word(alphas, alphanums)
OPCODE=Word(alphas)

NUMBER = Regex(r'(0[bx])?[0-9a-f]+')
@NUMBER.setParseAction
def parseNumbers(s, loc, tok):
    return IhasmTree("number", int(tok[0][0], 16))

VARIABLE = Group(Literal('$')+Word(alphanums))
@VARIABLE.setParseAction
def parseRegister(s, loc, tok):
    return IhasmTree("variable", tok[0][1])

REGISTER = Group(Literal('%')+Word(alphanums))
@REGISTER.setParseAction
def parseRegister(s, loc, tok):
    return IhasmTree("register", tok[0][1])

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
@PRAGMA.setParseAction
def globalSettings(loc, pragma_terminal):
    global ihasm_pragmas
    key = pragma_terminal[0]["pragma_identifier"]
    val = pragma_terminal[0]["pragma_value"]
    print(f'DEBUG: setting pragma {key} to {val}')
    ihasm_pragmas[key]=val
    return [] #maybe Suppresses the token?

# Comments start with a semicolon, always extend to end of line. 
COMMENT_START = Literal(";")
COMMENT_LINE = Suppress(COMMENT_START) + Group(SkipTo(LineEnd())("comment")) + LDLIM
@COMMENT_LINE.setParseAction
def rememberComments(loc, token):
    return []
    # TODO: Parse comments correctly instead of just throwing them away 
    # return IhasmTree("comment",[],comment=token[0]["comment"],loc=loc)

# Bundled comments into EOL to get comments on any line for free.
EOL = COMMENT_LINE | LDLIM

# Data lines start with the literal .data and continue with a string of hexadecimal words
DATA_START = Literal(".data")
DATA_LINE = Suppress(DATA_START) + Group(SkipTo(EOL)("data")) + EOL
@DATA_LINE.setParseAction
def dataToken(s, loc, token):
    dataString = token[0]['data'].strip()
    dataString = "".join(dataString.split(" +"))
    try:
        dataOctets = [int(dataString[x:x+2],16) for x in range(0,len(dataString), 2)]
        return IhasmTree("data",dataOctets,loc=loc)
    except ValueError as ex:
        raise ParseException(s, loc, str(ex), self)

# Labels need to be a legal identifier
LABEL_START = Literal(".label")
LABEL_LINE = Suppress(LABEL_START) + Group(IDENTIFIER("label")) + EOL
@LABEL_LINE.setParseAction
def labelHandler(s, loc, tok):
    return IhasmTree("label",None,label=tok[0]['label'])

# Ascii lines need to have a quoted string in it
ASCII_START = Literal(".ascii")
ASCII_LINE = Suppress(ASCII_START) + Group(QuotedString("\"")("text")) + EOL
@ASCII_LINE.setParseAction
def parseAsciiIntoTree(loc, tokens):
    return IhasmTree("text",[ord(x) for x in tokens[0]["text"]], loc=loc)

# Code lines:
# a code line is in the form OPCODE EXPR1,EXPR2,EXPR3... EOL as above
CODE_LINE = Group(OPCODE("opcode") + Opt(EXPRESSIONS)("args")) + EOL
@CODE_LINE.setParseAction
def instr_handle(s, loc, tok):
    return IhasmTree("instr",tok[0]['opcode'], children=tok[0][1:])

IHASM_FILE = StringStart() + OneOrMore(PRAGMA | COMMENT_LINE | DATA_LINE | LABEL_LINE | ASCII_LINE | CODE_LINE) + StringEnd()
@IHASM_FILE.setParseAction
def ihasm_root_create(s, loc, tok):
    return IhasmTree("asm", None, children=tok)

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
            ihasm_ast = IHASM_FILE.parseString(input_line)
            print(f'Parses as: {repr(ihasm_ast)}')
            print()
        except ParseException as err:
            print(err.explain())    

def parse_file(args):
    ihasm_ast = None
    pp = pprint.PrettyPrinter(indent=2)
    try:
        ihasm_ast = IHASM_FILE.parseFile(args.source_file)
        print("File parses as:")
        pp.pprint(ihasm_ast)
    except ParseException as err:
        print(err.explain())
        exit(1)

def assemble_file(args):
    global ihasm_pragmas, ihasm_arch
    ihasm_ast = None
    pp = pprint.PrettyPrinter(indent=2)
    try:
        ihasm_ast = IHASM_FILE.parseFile(args.source_file)
        print("File parses as:")
        pp.pprint(ihasm_ast[0])
    except ParseException as err:
        print(err.explain())
        exit(1)
    if "arch" not in ihasm_pragmas:
        print("Architecture not set, please specify with pragma #arch")
        exit(1)
    elif ihasm_pragmas["arch"] not in ihasm_arch:
        print(f'Architecture {ihasm_pragmas["arch"]} not registered')
        exit(1)
    try:
        code_binary = ihasm_arch[ihasm_pragmas["arch"]].build(args.object_file,ihasm_pragmas)
    except Exception as ex:
        print(f'error with the code generation: {ex}')
        exit(1)

    args.object_file.write(code_binary)

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

    asmp = subp.add_parser(name='assemble', description='assemble a file and exits')
    asmp.add_argument('source_file', type=ap.FileType('r'), help='The source .ihasm file to parse')
    asmp.add_argument('object_file', type=ap.FileType('wb'), help='The destination .out file to create')
    asmp.set_defaults(func=assemble_file)

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
