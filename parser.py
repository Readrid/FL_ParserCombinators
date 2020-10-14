import re

from parsec import *

whitespace = regex(r'\s+', re.MULTILINE)
tabs       = regex(r'\t+', re.MULTILINE)
ignore     = many(whitespace ^ tabs)

reserved = {
    'module' : 'MODULE',
    'type'   : 'TYPE',
}

lexeme = lambda p: p << ignore
def checkReserved(p):
    if reserved.get(p) != None:
        raise SyntaxError(f"SyntaxError: expected ID but '{p}' found")
    return p
                         

ID        = lexeme(regex(r'[a-z_][a-zA-Z_0-9]*')).parsecmap(checkReserved)
MODULE    = lexeme(string('module'))
TYPE      = lexeme(string('type'))
VAR       = lexeme(regex(r'[A-Z][a-zA-Z_0-9]*'))
LPAREN    = lexeme(string('('))
RPAREN    = lexeme(string(')'))
DOT       = lexeme(string('.'))
DISJ      = lexeme(string(';'))
CONJ      = lexeme(string(','))
CORKSCREW = lexeme(string(':-'))
ARROW     = lexeme(string('->'))
LBR       = lexeme(string('['))
RBR       = lexeme(string(']'))
LBAR      = lexeme(string('|'))

@generate
def prolog():
    module_declaration = yield module
    types     = yield many(typedef)
    relations = yield many(relation)
    showTypes = ') ('.join(types)
    showRel   = ') ('.join(relations)
    if showRel == showTypes == '':
        return  f"PROG ({module_declaration})"
    if showRel == '':
        return f"PROG ({module_declaration}) ({') ('.join(types)})"
    if showTypes == '':
        return f"PROG ({module_declaration}) ({') ('.join(relations)})"
    return f"PROG ({module_declaration}) ({') ('.join(types)}) ({') ('.join(relations)})"
 
@generate
def showID():
    ident = yield ID
    return f'ID {ident}'

@generate
def showVAR():
    var = yield VAR
    return f'VAR {var}'

@generate
def brace_disj():
    yield LPAREN
    ex = yield disjunction
    yield RPAREN
    return ex

@generate
def conj():
    v = yield term
    yield CONJ
    c = yield conjuction
    return f'CONJ ({v}) ({c})'

@generate
def disj():
    c = yield conjuction
    yield DISJ
    d = yield disjunction
    return f'DISJ ({c}) ({d})'

@generate
def relbody():
    head = yield atom

    yield CORKSCREW
    dis = yield disjunction
    yield DOT
    
    return f'REL ({head}) ({dis})'

@generate
def shortrel():
    head = yield atom
    yield DOT
    return f'REL ({head})'

@generate
def module():
    yield MODULE
    strID = yield showID
    yield DOT
    return f'MODULE ({strID})'

@generate
def braceTypeelem():
    yield LPAREN
    ex = yield typeseq
    yield RPAREN
    return ex

@generate
def typedef():
    yield TYPE
    typename = yield showID
    seq = yield typeseq
    yield DOT
    return f'TYPEDEF ({typename}) ({seq})'

@generate
def typeseq():
    seq = yield sepBy1(typeelem, ARROW)
    typeseqStr = 'TYPESEQ (' + ') ('.join(seq) + ')'
    return typeseqStr

def foldr(l, length):
    if len(l) == 0:
        return ''
    if len(l) == 1:
        return f'ATOM (ID cons) (ATOM ({l[0]}) (ATOM (ID nil))' + ')'*length
    return f'ATOM (ID cons) ({l[0]} (' + foldr(l[1:], length)

@generate
def listelems():
    l = yield sepBy(listsugare ^ atom ^ VAR, CONJ)
    return foldr(l, len(l))

@generate
def listsimple():
    yield LBR
    elems = yield listelems
    yield RBR
    return elems

@generate
def listHT():
    yield LBR
    head = yield (listsugare ^ atom ^ VAR)
    yield LBAR
    tail = yield showVAR
    yield RBR
    return f'ATOM (ID cons) (ATOM ({head}) ({tail}))'

@generate
def listSeq():
    l = yield listsugare
    seq = yield atomseq
    return f'ATOMSEQ ({l}) ({seq})'

@generate
def atomscope():
    yield LPAREN
    ex = yield atom
    yield RPAREN
    return ex 

@generate
def atom():
    ident = yield showID
    atoms = yield many(atomscope ^ listsugare ^ showID ^ showVAR)
    if len(atoms) == 0:
        return f'ATOM ({ident})'
    return f"ATOM ({ident}) ({') ('.join(atoms)})"

listsugare = listHT ^ listsimple

term        = brace_disj ^ atom
conjuction  = conj ^ term
disjunction = disj ^ conjuction

relation = shortrel ^ relbody

typeelem = braceTypeelem ^ atom ^ VAR