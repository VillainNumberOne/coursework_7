import re
from errors import TokenErrorUnrecognizedToken
from tokens import *
from utils import *

class Tokenizer:
    def __init__(self, code_string):
        self._code_string = code_string
        self._pos = 0

    def next_token_exists(self):
        return self._pos < len(self._code_string)

    def tokenize(self):
        self.tokens = [Token("skip", T_BOF, "", [0, 0])]
        try:
            while self.next_token_exists():
                token = self.next_token()
                if token is not None:
                    self.tokens.append(token)

            self.tokens.append(Token("special", T_EOF, "", pos=[self._pos, self._pos + 1]))
            return self.tokens, None
        except TokenErrorUnrecognizedToken as e:
            return self.tokens, e

    def next_token(self):
        current_string = self._code_string[self._pos:]

        for pattern in PATTERNS + SKIP_PATTERNS:
            match = re.match(pattern.re, current_string)
            if match:
                value = match.group(0)
                token_pos = [self._pos, self._pos + len(value)]
                self._pos = token_pos[1]
                return Token(pattern.type, pattern.token, value, pos=token_pos)
        
        unrecognized_token = repr(re.match(R'^.+s*|(\n)', current_string).group(0))
        convert_pos(self.tokens)
        raise TokenErrorUnrecognizedToken(self.tokens[-1], unrecognized_token)
        # raise Exception(f"Unrecognized token: {unrecognized_token} on {self._pos}")
        