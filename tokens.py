#########################################
# Tokens
# Words
T_BEGIN = '"Начало"'
T_FIRST = '"Первое"'
T_SECOND = '"Второе"'
T_EOSECOND = '"Конец второго"'
T_THIRD = '"Третье"'
T_COMBINED = '"Сочетаемое"'
# Values
T_REAL = '"вещ. знач"'
T_INT = '"цел. знач"'
T_ID = '"переменная"'
# Operators
T_PLUS = '"+"'
T_MINUS =' "-"'
T_MUL = '"*"'
T_DIV = '"/"'
T_COMMA = '","'
T_LBR = '"["'
T_RBR = '"]"'
T_EQ = '"="'
T_AND = '"||"'
T_OR = '"&&"'
T_NOT = '"!"'
T_COLON = '":"'
# Skip
TS_SPACE = '"пробел"'
TS_NEW_LINE = '"новая строка"'
TS_TAB = '"табуляция"'
# Other
T_BOF = '"начало документа"'
T_EOF = '"конец документа"'
T_MARK = '"метка"'
T_TEMP_EXPR = "EXPRESSION"
#########################################


class Pattern(object):
    def __init__(self, re, type, token) -> None:
        super().__init__()
        self.re = re
        self.type = type
        self.token = token

SKIP_PATTERNS = [
    Pattern(R"^\n+", "skip", TS_NEW_LINE),
    Pattern(R"^ ", "skip", TS_SPACE),
    Pattern(R"^\t+", "skip", TS_TAB)
]

# TODO fix errors with marks, variables, integers and real values 
PATTERNS = [
#########################################
# Other
    # Pattern(R"^\d+:", "mark", T_MARK),
    Pattern(R'^EXPR', "temp", T_TEMP_EXPR),
#########################################
# Words
    Pattern(R'^"Начало"', "word", T_BEGIN),
    Pattern(R'^"Первое"', "word", T_FIRST),
    Pattern(R'^"Второе"', "word", T_SECOND),
    Pattern(R'^"Конец второго"', "word", T_EOSECOND),
    Pattern(R'^"Третье"', "word", T_THIRD),
    Pattern(R'^"Сочетаемое"', "word", T_COMBINED),
#########################################
# Operands
    Pattern(R"^\d+\.\d+", "operand", T_REAL),
    Pattern(R"^\d+", "operand", T_INT),
    Pattern(R"^[a-zA-Zа-яА-ЯеЁ](\d+|[a-zA-Zа-яА-ЯеЁ]+)*", "id", T_ID),
#########################################
# Operators
    # {"re": R"^(\+|\-|\*|\/|\|\||&&|\[|\]|=|,)", "type": "operator"},
    Pattern(R'^\+', "operator", T_PLUS),
    Pattern(R'^\-', "operator", T_MINUS),
    Pattern(R'^\*', "operator", T_MUL),
    Pattern(R'^\/', "operator", T_DIV),
    Pattern(R'^\=', "operator", T_EQ),
    Pattern(R'^\,', "operator", T_COMMA),
    Pattern(R'^\[', "operator", T_LBR),
    Pattern(R'^\]', "operator", T_RBR),
    Pattern(R'^\|\|', "operator", T_OR),
    Pattern(R'^&&', "operator", T_AND),
    Pattern(R'^!', "operator", T_NOT),
    Pattern(R'^:', "operator", T_COLON),
]


class Token(object):
    def __init__(self, type, token, value, pos=None):
        self.type = type
        self.token = token
        self.value = value
        self.pos = pos
        self.pos2d = None

    def __repr__(self) -> str:
        return str(self.value)

    def compute(self):
        if self.token in (T_INT, T_REAL):
            return eval(self.value)
        elif self.token == T_ID:
            return None
        else:
            raise Exception(f"compute() is not supported for {self.token}")
