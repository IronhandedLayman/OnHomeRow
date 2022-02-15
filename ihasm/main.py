#!/usr/bin/python

VERSION="0.0"

PARSER_LANG="""
TODO:    pragmas like #arch SBNO 
TODO:    comments like // This is based on the SBN architecture indicated on the page
TODO:    section commands like .data test1
TODO:    binary data lines like  0x 01 10 FE F6 00 a5 a5 a5
TODO:    ascii data lines like "hi there"
TODO:    code lines like SBN a, b
TODO:    inline expressions and pre-calculated values
"""

def main():
    print(f"ihasm version {VERSION}")

if __name__ == "__main__":
    main()
