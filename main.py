from parser import *
from parsec import *

if __name__ == '__main__':
    data = 'f (cons x nil)' 
    try:
        print(program.parse_strict(data))
    except ParseError as ex:
        line, pos = ex.loc().split(':')
        print(f"Syntax error: line {line}, colon {pos}")
    except SyntaxError as ex:
        print(ex.args[0])
    #print(program.parse_strict('type kek a -> (b a -> (d -> c) -> o) -> c.'))