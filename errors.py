import tkinter as tk

def pos2d_to_message(pos2d):
    if pos2d[1] is not None:
        return f"От: строка {pos2d[0][0]}, столбец {pos2d[0][1]}; до: строка {pos2d[1][0]}, столбец {pos2d[1][1]}"
    else:
        return f"От: строка {pos2d[0][0]}, столбец {pos2d[0][1]}"



class CustomSyntaxError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SyntaxErrorExpectedVSGot(Exception):
    def __init__(self, expected, got, pos2d=None) -> None:
        assert isinstance(expected, (str, list, tuple))
        if isinstance(expected, (list, tuple)):
            expected_str = f"({' | '.join(expected)})"
        else:
            expected_str = expected
        if pos2d is not None:
            self.message = CustomSyntaxError(f"Ошибка: Получено: {got}, ожидалось {expected_str}. Положение {pos2d_to_message(pos2d)}")
        else:
            self.message = CustomSyntaxError(f"Ошибка: Получено: {got}, ожидалось {expected_str}")
        self.pos2d = pos2d
        super().__init__(self.message)


class SyntaxErrorMaxBracketsDepth(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TokenErrorUnrecognizedToken(Exception):
    def __init__(self, last_token, unrecognized_token, cut=10) -> None:
        self.token = last_token
        pos2d = self.token.pos2d
        pos2d[1] = None
        if pos2d is not None:
            self.message = f"Ошибка: неопознанная лексема: {unrecognized_token}... Положение {pos2d_to_message(pos2d)}"
        else:
            self.message = f"Ошибка: неопознанная лексема: {unrecognized_token}..."

        self.pos2d = [pos2d[1], None]
        super().__init__(self.message)
