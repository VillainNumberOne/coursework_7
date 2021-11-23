from tokens import *
from utils import convert2serialize
import json


# Super ##############################################
class Node(object):
    def __init__(self) -> None:
        super().__init__()

    def __repr__(self) -> str:
        return super().__repr__()

    def to_json(self) -> str:
        return json.dumps(convert2serialize(self))


class NodeSpaceSaparatedValues(Node):
    def __init__(self, element, next_element) -> None:
        super().__init__()
        self.element = element
        self.next_element = next_element
    
    def __repr__(self) -> str:
        if self.next_element is not None:
            return f"{self.element} {self.next_element}"
        else:
            return str(self.element)

# TODO Operators shouldn't be included
class NodeSeparatedValues(Node):
    def __init__(self, element, separator, next_element) -> None:
        super().__init__()
        self.element = element
        self.separator = separator
        self.next_element = next_element
    
    def __repr__(self) -> str:
        if self.next_element is not None:
            return f"{self.element} {self.separator} {self.next_element}"
        else:
            return str(self.element)


# Expression #########################################
# Math
class NodeBinaryOperator(Node): # T_MUL, T_DIV, T_PLUS, T_MINUS, T_AND, T_OR
    def __init__(self, left, operator, right) -> None:
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"{self.left} {self.operator} {self.right}"

    def compute(self):
        left = self.left.compute()
        right = self.right.compute()
        
        if left is not None and right is not None:
            if self.operator.token == T_MUL:
                result = left * right
            elif self.operator.token == T_DIV:
                result = left / right
            elif self.operator.token == T_PLUS:
                result = left + right
            elif self.operator.token == T_MINUS:
                result = left - right
            elif self.operator.token == T_AND:
                result = bool(left) and bool(right)
            elif self.operator.token == T_OR:
                result = bool(left) or bool(right)
            return result
        else:
            return None


class NodeUnaryOperator(Node): # T_MINUS, T_NOT
    def __init__(self, operator, term) -> None:
        super().__init__()
        self.operator = operator
        self.term = term

    def __repr__(self) -> str:
        return f"{self.operator}({self.term})"

    def compute(self):
        term = self.term.compute()

        if term is not None:
            if self.operator.token == T_MINUS:
                result = - term
            elif self.operator.token == T_NOT:
                result = not bool(term)
            return result
        else:
            return None


class NodeExpression(Node):
    def __init__(self, expression) -> None:
        super().__init__()
        self.expression = expression

    def __repr__(self) -> str:
        return f"({self.expression})"

    def compute(self):
        return self.expression.compute()


# Other
class NodeMark(Node):
    def __init__(self, mark, colon) -> None:
        super().__init__()
        self.mark = mark
        self.colon = colon

    def __repr__(self):
        return f"{self.mark}{self.colon}"


class NodeOperation(Node):
    def __init__(self, mark: NodeMark, variable, expression=None) -> None:
        super().__init__()
        self.mark = mark
        self.variable = variable
        self.expression = expression
    
    def __repr__(self) -> str:
        return f"{self.mark} {self.variable} = {self.expression}"

    def compute(self):
        result = self.expression.compute()
        if result is not None:
            message = f">> {self.mark} {self.variable} = {result}"
        else:
            message = f">> {self.mark} {self.variable} = {result} (В операции использованы неопределенные переменные)"
        return result, message


# Chain Segment ######################################
class NodeChainSegmentElement(NodeSpaceSaparatedValues):
    def __init__(self, element, next_element) -> None:
        super().__init__(element, next_element)


class NodeChainSegment(Node):
    def __init__(self, element: NodeChainSegmentElement) -> None:
        super().__init__()
        self.element = element
    
    def __repr__(self) -> str:
        return f'"Сочетаемое" {self.element}'


# Named Set ##########################################
# TODO Operators shouldn't be included
class NodeFirstSetElement(NodeSpaceSaparatedValues):
    def __init__(self, element, next_element) -> None:
        super().__init__(element, next_element)


class NodeSecondSetElement(NodeSeparatedValues):
    def __init__(self, element, separator, next_element) -> None:
        super().__init__(element, separator, next_element)


class NodeThirdSetElement(NodeSeparatedValues):
    def __init__(self, element, separator, next_element) -> None:
        super().__init__(element, separator, next_element)


class NodeNamedSet(Node):
    def __init__(self, element, next_named_set) -> None:
        super().__init__()
        assert isinstance(
            element, 
            (
                NodeFirstSetElement, 
                NodeSecondSetElement,
                NodeThirdSetElement
            )
        ), f"Unsupported element type {type(element)} for NamedSet"
        self.element = element
        self.next_named_set = next_named_set
    
    def __repr__(self) -> str:
        if isinstance(self.element, NodeFirstSetElement):
            return f'"Первое" {self.element} {self.next_named_set}'
        elif isinstance(self.element, NodeSecondSetElement):
            return f'"Второе" {self.element} "Конец второго" {self.next_named_set}'
        elif isinstance(self.element, NodeThirdSetElement):
            return f'"Третье" {self.element} {self.next_named_set}'

# Program ############################################
class NodeProgram(Node):
    def __init__(
        self, 
        named_set: NodeNamedSet, 
        chain_segment: NodeChainSegment, 
        expression: NodeOperation
    ) -> None:
        super().__init__()
        self.named_set = named_set
        self.chain_segment = chain_segment
        self.expression = expression
    
    def __repr__(self) -> str:
        return f'"Начало" {self.named_set} {self.chain_segment} {self.expression}'