from typing import List
import sys

from parser import *

def CLI(cmd):
    program = ignore >> prolog
    if cmd == "--atom":
        program = ignore >> atom
    elif cmd == "--typeexpr":
        program = ignore >> typeseq
    elif cmd == "--typedef":
        program = ignore >> typedef
    elif cmd == "--module":
        program = ignore >> module
    elif cmd == "--relation":
        program = ignore >> relation
    elif cmd == "--list":
        program = ignore >> listsugare
    elif cmd != "--prog":
        print("Unknown command")
        return None
    return program


def main(args_str: List[str]):
    program = ignore >> prolog
    fileindx = 0
    if len(args_str) > 1:
        program = CLI(args_str[0])
        fileindx = 1

    if program == None:
        return

    with open(args_str[fileindx], 'r') as inputFile:
        data = inputFile.read()
    
    with open(args_str[fileindx] + '.out', 'w') as outputFile:
        #sys.stdout = outputFile
        try:
            print(program.parse_strict(data))
        except ParseError as ex:
            line, pos = ex.loc().split(':')
            print(f"Syntax error: line {line}")
        except SyntaxError as ex:
            print(ex.args[0])


if __name__ == '__main__':
    main(sys.argv[1:])