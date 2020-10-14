from parser import *
from parsec import *

if __name__ == '__main__':
    try:
        print(program.parse_strict('type kek a ->'))
    except ParseError as ex:
        print("Syntax error:", ex.loc())
    #print(program.parse_strict('type kek a -> (b a -> (d -> c) -> o) -> c.'))