import unittest

from parser import *

class TestPrologParser(unittest.TestCase):

    def test_atom(self):
        self.assertEqual(atom.parse_strict('a'), "ATOM (ID a)")
        self.assertEqual(atom.parse_strict('a b c'),'ATOM (ID a) (ID b) (ID c)')
        self.assertEqual(atom.parse_strict('a (b c)'),'ATOM (ID a) (ATOM (ID b) (ID c))')
        self.assertEqual(atom.parse_strict('a ((b c))'),'ATOM (ID a) (ATOM (ID b) (ID c))')
        self.assertEqual(atom.parse_strict('a ((b c)) d'),'ATOM (ID a) (ATOM (ID b) (ID c)) (ID d)')
        self.assertEqual(atom.parse_strict('a ((b c))  (d)'),'ATOM (ID a) (ATOM (ID b) (ID c)) (ATOM (ID d))')
        self.assertEqual(atom.parse_strict('a((b c))((d))'),'ATOM (ID a) (ATOM (ID b) (ID c)) (ATOM (ID d))')
        
        self.assertRaises(ParseError, atom.parse_strict, 'a (a')
        self.assertRaises(ParseError, atom.parse_strict, 'X a')
        self.assertRaises(ParseError, atom.parse_strict, '(a)')

    def test_relations(self):
        program = ignore >> relation

        self.assertEqual(program.parse_strict('a.'),'REL (ATOM (ID a))')
        self.assertEqual(program.parse_strict('a b.'),'REL (ATOM (ID a) (ID b))')
        self.assertEqual(program.parse_strict('a:-a.'),'REL (ATOM (ID a)) (ATOM (ID a))')
        self.assertEqual(program.parse_strict('a :-a.'),'REL (ATOM (ID a)) (ATOM (ID a))')
        self.assertEqual(program.parse_strict('a:-a b.'),'REL (ATOM (ID a)) (ATOM (ID a) (ID b))')
        self.assertEqual(program.parse_strict('a b:- (a b)  .'),'REL (ATOM (ID a) (ID b)) (ATOM (ID a) (ID b))')
        self.assertEqual(program.parse_strict('a b:- a;b,c.'),'REL (ATOM (ID a) (ID b)) (DISJ (ATOM (ID a)) (CONJ (ATOM (ID b)) (ATOM (ID c))))')
        self.assertEqual(program.parse_strict('a b:- a;(b,c).'),'REL (ATOM (ID a) (ID b)) (DISJ (ATOM (ID a)) (CONJ (ATOM (ID b)) (ATOM (ID c))))')
        self.assertEqual(program.parse_strict('a b:- (a;b),c.'),
            'REL (ATOM (ID a) (ID b)) (CONJ (DISJ (ATOM (ID a)) (ATOM (ID b))) (ATOM (ID c)))')
        self.assertEqual(program.parse_strict('a b:- a;b;c.'),
            'REL (ATOM (ID a) (ID b)) (DISJ (ATOM (ID a)) (DISJ (ATOM (ID b)) (ATOM (ID c))))')
        self.assertEqual(program.parse_strict('a b:- a,b,c.'),'REL (ATOM (ID a) (ID b)) (CONJ (ATOM (ID a)) (CONJ (ATOM (ID b)) (ATOM (ID c))))')
        self.assertEqual(program.parse_strict('a (b (c))  :- (a b) .'),
            'REL (ATOM (ID a) (ATOM (ID b) (ATOM (ID c)))) (ATOM (ID a) (ID b))')

        self.assertRaises(ParseError, program.parse_strict, 'a : - f')

    def test_typeexpr(self):
        program = ignore >> typeseq
        self.assertEqual(program.parse_strict('a'), 'TYPESEQ (ATOM (ID a))')
        self.assertEqual(program.parse_strict('Y -> X'), 'TYPESEQ (VAR Y) (VAR X)')
        self.assertEqual(program.parse_strict('(Y -> X)'), 'TYPESEQ (TYPESEQ (VAR Y) (VAR X))')
        self.assertEqual(program.parse_strict('((Y -> X))'), 'TYPESEQ (TYPESEQ (VAR Y) (VAR X))')
        self.assertEqual(program.parse_strict('(A -> B) -> C'), 'TYPESEQ (TYPESEQ (VAR A) (VAR B)) (VAR C)')
        self.assertEqual(program.parse_strict('A -> B -> C'), 'TYPESEQ (VAR A) (VAR B) (VAR C)')
        self.assertEqual(program.parse_strict('list (list A) -> list A -> o'),
                                              'TYPESEQ (ATOM (ID list) (ATOM (ID list) (VAR A))) (ATOM (ID list) (VAR A)) (ATOM (ID o))')
        self.assertEqual(program.parse_strict('pair A B -> (A -> C) -> (B -> D) -> pair C D'),
                                              'TYPESEQ (ATOM (ID pair) (VAR A) (VAR B)) (TYPESEQ (VAR A) (VAR C)) (TYPESEQ (VAR B) (VAR D)) (ATOM (ID pair) (VAR C) (VAR D))')


    def test_typedef(self):
        program = ignore >> typedef

        self.assertEqual(program.parse_strict('type a b.'), 'TYPEDEF (ID a) (TYPESEQ (ATOM (ID b)))')
        self.assertEqual(program.parse_strict('type a b -> X.'), 'TYPEDEF (ID a) (TYPESEQ (ATOM (ID b)) (VAR X))')
        self.assertEqual(program.parse_strict('type filter (A -> o) -> list a -> list a -> o.'),
         'TYPEDEF (ID filter) (TYPESEQ (TYPESEQ (VAR A) (ATOM (ID o))) (ATOM (ID list) (ID a)) (ATOM (ID list) (ID a)) (ATOM (ID o)))')
        self.assertEqual(program.parse_strict('type a (((b))).'), 'TYPEDEF (ID a) (TYPESEQ (TYPESEQ (ATOM (ID b))))')
        self.assertEqual(program.parse_strict('type d a -> (((b))).'), 'TYPEDEF (ID d) (TYPESEQ (ATOM (ID a)) (TYPESEQ (ATOM (ID b))))')

        self.assertRaises(SyntaxError, program.parse_strict, 'type type type -> type.')
        self.assertRaises(ParseError, program.parse_strict, 'tupe x o.')
        self.assertRaises(AttributeError, program.parse_strict, 'type z -> x') #WTF


    def test_module(self):
        program = ignore >> module
        self.assertEqual(program.parse_strict(' module    name.'),'MODULE (ID name)')
        self.assertEqual(program.parse_strict('\t\nmodule\n\n  name_123.'),'MODULE (ID name_123)')

        self.assertRaises(SyntaxError, program.parse_strict, 'module module.')
        self.assertRaises(ParseError, program.parse_strict, 'modulo name.')
        self.assertRaises(ParseError, program.parse_strict, 'modulename.')
        self.assertRaises(ParseError, program.parse_strict, 'mod ule name.')
        self.assertRaises(ParseError, program.parse_strict, 'module name!')
        self.assertRaises(ParseError, program.parse_strict, 'module 123name.')
    

    def test_list(self):
        program = ignore >> listsugare

        self.assertEqual(program.parse_strict('[]'), atom.parse_strict('nil'))
        self.assertEqual(program.parse_strict('[a]'), atom.parse_strict('cons ((a)) nil'))
        self.assertEqual(program.parse_strict('[A, B]'), atom.parse_strict('cons A (cons B nil)'))
        self.assertEqual(program.parse_strict('[a (b c), B, C]'), atom.parse_strict('cons (a (b c)) (cons B (cons C nil))'))
        self.assertEqual(program.parse_strict('[a | T]'), atom.parse_strict('cons (((a))) T'))
        self.assertEqual(program.parse_strict('[ [a] | T ]'), atom.parse_strict('cons [a] T'))
        self.assertEqual(program.parse_strict('[ [H | T], a ]'), atom.parse_strict('cons [H | T] (cons ((a)) nil)'))

        self.assertRaises(ParseError, program.parse_strict, '[a | a]')
        self.assertRaises(ParseError, program.parse_strict, '[A,B,]')
        self.assertRaises(ParseError, program.parse_strict, '[A,B')
        self.assertRaises(ParseError, program.parse_strict, '][')

    def test_prog(self):
        program = ignore >> prolog

        self.assertEqual(program.parse_strict('module test.\n\ntype fl hw -> parser -> automata.\n\nex :- f , k.\nrec :- fl.'), 
            'PROG (MODULE (ID test)) (TYPEDEF (ID fl) (TYPESEQ (ATOM (ID hw)) (ATOM (ID parser)) (ATOM (ID automata)))) (REL (ATOM (ID ex)) (CONJ (ATOM (ID f)) (ATOM (ID k)))) (REL (ATOM (ID rec)) (ATOM (ID fl)))') 
    


if __name__ == '__main__':
    unittest.main()