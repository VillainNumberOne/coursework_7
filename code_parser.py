from re import A
from typing import Iterable, List
from tokenizer import *
from nodes import *
from errors import CustomSyntaxError, SyntaxErrorExpectedVSGot, SyntaxErrorMaxBracketsDepth

class Parser():
    def __init__(self, tokens: List, max_brackets_depth=-1) -> None:
        assert max_brackets_depth >= -1
        self.tokens = tokens
        self.max_brackets_depth = max_brackets_depth
        self.reset()

    def reset(self):
        self._pos = 0
        self._current = self.tokens[self._pos]

    # TODO refactor next and prev
    def next(self, n=1):
        assert n >= 1, f"{n} < 1"
        self._pos += n
        if self._pos < len(self.tokens):
            self._current = self.tokens[self._pos]
            if self._current.type == "skip":
                return self.next()
        else:
            self._current = None
        return self._current

    def prev(self, n=1):
        assert n >= 1, f"{n} < 1"
        self._pos -= n
        if self._pos > 0:
            self._current = self.tokens[self._pos]
            if self._current.type == "skip":
                return self.prev()
        else:
            self._current = None
        return self._current
    
    def ast(self):
        self.reset()
        try:
            tree = self.program()
        except (SyntaxErrorExpectedVSGot, SyntaxErrorMaxBracketsDepth) as e:
            return None, e
        else:
            return tree, None
    
    # Chain Segment ######################################
    def chain_segment_element(self, n_elements=0) -> NodeChainSegmentElement:
        if self._current.token == T_INT:
            element = self._current
            self.next()
            n_elements += 1
            # check if there is a colon #########
            if self._current.token == T_COLON:
                if n_elements > 1:
                    self.prev()
                    return None
                else:
                    raise SyntaxErrorExpectedVSGot(T_INT, self._current.token, pos2d=self._current.pos2d)
            #####################################
            next_element = self.chain_segment_element(n_elements)
            return NodeChainSegmentElement(element, next_element)
        elif n_elements:
            return None
        raise SyntaxErrorExpectedVSGot(T_INT, self._current.token, pos2d=self._current.pos2d)
            
    def chain_segment(self) -> NodeChainSegment:
        if self._current.token == T_COMBINED:
            self.next()
            chain_segment_element = self.chain_segment_element()
            return NodeChainSegment(chain_segment_element)
        raise SyntaxErrorExpectedVSGot(T_COMBINED, self._current.token, pos2d=self._current.pos2d)

    # Named Set ##########################################
    # TODO refactor with chain_segment_element
    def first_set_element(self, al_one=False) -> NodeFirstSetElement:
        expected = (T_FIRST, T_SECOND, T_THIRD, T_COMBINED)
        if self._current.token == T_INT:
            element = self._current
            self.next()
            next_element = self.first_set_element(True)
            return NodeFirstSetElement(element, next_element)
        elif al_one and self._current.token in expected:
            return None
        # elif self._current.token in expected:
        raise SyntaxErrorExpectedVSGot((T_INT,) + expected , self._current.token, pos2d=self._current.pos2d)

    def second_set_element(self, al_one=False) -> NodeSecondSetElement:
        if self._current.token == T_REAL:
            element = self._current
            self.next()
            if self._current.token == T_COMMA:
                separator = self._current
                self.next()
                next_element = self.second_set_element(True)
                if next_element is not None:
                    return NodeSecondSetElement(element, separator, next_element)
                else:
                    raise SyntaxErrorExpectedVSGot(T_REAL, self._current.token, pos2d=self._current.pos2d)
            else:
                return NodeSecondSetElement(element, None, None)
        elif al_one:
            return None
        raise SyntaxErrorExpectedVSGot(T_REAL, self._current.token, pos2d=self._current.pos2d)

    # TODO refactor with other collection-like garbage
    def third_set_element(self, al_one=False) -> NodeSecondSetElement:
        if self._current.token == T_ID:
            element = self._current
            self.next()
            if self._current.token == T_COMMA:
                separator = self._current
                self.next()
                next_element = self.third_set_element(True)
                if next_element is not None:
                    return NodeSecondSetElement(element, separator, next_element)
                else:
                    raise SyntaxErrorExpectedVSGot(T_ID, self._current.token, pos2d=self._current.pos2d)    
            else:
                return NodeThirdSetElement(element, None, None)
        elif al_one:
            return None
        raise SyntaxErrorExpectedVSGot(T_ID, self._current.token, pos2d=self._current.pos2d)
            
    # TODO Refactor
    def named_set(self, al_one=False) -> NodeNamedSet:
        if self._current.token == T_FIRST:
            self.next()
            set_element = self.first_set_element()
            next_named_set = self.named_set(True)
            return NodeNamedSet(set_element, next_named_set)
        elif self._current.token == T_SECOND:
            self.next()
            set_element = self.second_set_element()
            if self._current.token == T_EOSECOND:
                self.next()
                next_named_set = self.named_set(True)
                return NodeNamedSet(set_element, next_named_set)
            else:
                raise SyntaxErrorExpectedVSGot(T_EOSECOND, self._current.token, pos2d=self._current.pos2d)
        elif self._current.token == T_THIRD:
            self.next()
            set_element = self.third_set_element()
            next_named_set = self.named_set(True)
            return NodeNamedSet(set_element, next_named_set)
        elif al_one:
            return None
        raise SyntaxErrorExpectedVSGot([T_FIRST, T_SECOND, T_THIRD], self._current.token, pos2d=self._current.pos2d)
    
    # Operation #########################################
    # TODO refactor other functions in this style:
    def term(self):
        expected_values = (T_REAL, T_INT, T_ID)
        expected_unary_operators = (T_NOT,)
        
        if self._current.token in expected_values:
            term = self._current
            self.next()
            return term
        elif self._current.token in expected_unary_operators:
            operator = self._current
            self.next()
            term = self.term()
            return NodeUnaryOperator(operator, term)
        elif self._current.token == T_LBR:
            if self.max_brackets_depth != -1:
                self.brackets_depth += 1
                if self.brackets_depth > self.max_brackets_depth:
                    raise SyntaxErrorMaxBracketsDepth("Max depth reached")
            self.next()
            term = self.expression(exit=(T_RBR, T_EOF))
            if self._current.token == T_RBR:
                self.next()
                return term
            raise SyntaxErrorExpectedVSGot(T_RBR, self._current.token, pos2d=self._current.pos2d)
        
        raise SyntaxErrorExpectedVSGot(expected_values + expected_unary_operators, self._current.token, pos2d=self._current.pos2d)

    def binary_expressions(self, expected: tuple, term_function, exit_token: tuple, term_function_kwargs={}):
        left = term_function(**term_function_kwargs)
        if self._current.token in expected:
            operator = self._current
            self.next()
            right = self.binary_expressions(expected, term_function, exit_token, term_function_kwargs)
            return NodeBinaryOperator(left, operator, right)
        elif self._current.token in exit_token:
            return left
        raise SyntaxErrorExpectedVSGot(expected + exit_token, self._current.token, pos2d=self._current.pos2d)

    def expression(self, exit=(T_EOF,)):  
        # additive 
        expression = self.binary_expressions(
            expected=(T_PLUS, T_MINUS), 
            # multiplicative
            term_function=self.binary_expressions,
            exit_token=exit,
            term_function_kwargs={
                "expected": (T_MUL, T_DIV),
                # logical
                "term_function": self.binary_expressions,
                "exit_token": (T_PLUS, T_MINUS) + exit,
                "term_function_kwargs": {
                    "expected": (T_AND, T_OR),
                    # unary
                    "term_function": self.term,
                    "exit_token": (T_PLUS, T_MINUS, T_MUL, T_DIV) + exit
                }
            }
        )
        # logical additive
        # expression = self.binary_expressions(
        #     expected=(T_OR,), 
        #     # logical multiplicative
        #     term_function=self.binary_expressions,
        #     exit_token=exit,
        #     term_function_kwargs={
        #         "expected": (T_AND,),
        #         # additive
        #         "term_function": self.binary_expressions,
        #         "exit_token": (T_OR,) + exit,
        #         "term_function_kwargs": {
        #             "expected": (T_PLUS, T_MINUS),
        #             # multiplicative
        #             "term_function": self.binary_expressions,
        #             "exit_token": (T_AND, T_OR,) + exit,
        #             "term_function_kwargs": {
        #                 "expected": (T_MUL, T_DIV),
        #                 "term_function": self.term,
        #                 "exit_token": (T_MUL, T_DIV, T_PLUS, T_MINUS, T_AND, T_OR,) + exit,
        #             }
        #         }
        #     }
        # )
        return NodeExpression(expression)


    def mark(self):
        if self._current.token == T_INT:
            mark = self._current
            self.next()
            colon = self._current
            self.next()
            return NodeMark(mark, colon)
        # Everything else should be already checked in chain_segment_element()
        return None

    def open_operation(self):
        if self._current.token == T_ID:
            variable = self._current
            self.next()
            if self._current.token == T_EQ:
                self.next()
                return variable
            else:
                raise SyntaxErrorExpectedVSGot(T_EQ, self._current.token, pos2d=self._current.pos2d)
        raise SyntaxErrorExpectedVSGot(T_ID, self._current.token, pos2d=self._current.pos2d)

    def operation(self) -> NodeOperation:
        if self._current.token in (T_INT, T_ID):
            mark = self.mark()
            variable = self.open_operation()
            # logical additive
            self.brackets_depth = 0 
            expression = self.expression()
            return NodeOperation(mark, variable, expression)
        raise SyntaxErrorExpectedVSGot([T_MARK, T_ID], self._current.token, pos2d=self._current.pos2d)

    # Program ############################################
    def program(self) -> NodeProgram:
        self.next()
        if self._current.token == T_BEGIN:
            self.next()
            named_set = self.named_set()
            chain_segment = self.chain_segment()
            operation = self.operation()
            return NodeProgram(named_set, chain_segment, operation)
        raise SyntaxErrorExpectedVSGot(T_BEGIN, self._current.token, pos2d=self._current.pos2d)