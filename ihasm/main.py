#!/usr/bin/python

import pyparsing as pp

VERSION="0.0"

PARSER_LANG="""
#arch SBNO 
TODO:    ; this is a comment in a mature assembler
TODO:    section commands like .data test1
TODO:    binary data lines like  0x 01 10 FE F6 00 a5 a5 a5
TODO:    ascii data lines like "hi there"
TODO:    code lines like SBN a, b
TODO:    inline expressions and pre-calculated values
"""

PRAGMA_START=pp.Literal("#")
PRAGMA_IDENTIFIER=pp.Word(pp.alphas)("pragma_identifier")
PRAGMA_VALUE=pp.Word(pp.alphas)("pragma_value")

PRAGMA=pp.Combine(PRAGMA_START+PRAGMA_IDENTIFIER)+PRAGMA_VALUE

COMMENT_START = pp.Literal(";")
COMMENT_LINE = COMMENT_START + pp.Group(pp.SkipTo(pp.LineEnd()))("comment") + pp.LineEnd()

IHASM_LINE = pp.OneOrMore(PRAGMA | COMMENT_LINE)

def main():
    print(f"ihasm version {VERSION}")
    demo()

def demo():
    for input_line in [
            "#arch SBNO",
            "; this is just a comment",
            ".code not_implemented_yet",
            ]:
        ihasm_ast = IHASM_LINE.parse_string(input_line)
        print(repr(ihasm_ast))

if __name__ == "__main__":
    main()
