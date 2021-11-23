from tokenizer import *
from tokens import *

def convert2serialize(obj):
    if isinstance(obj, dict):
        return { k: convert2serialize(v) for k, v in obj.items() }
    elif hasattr(obj, "_ast"):
        return convert2serialize(obj._ast())
    elif not isinstance(obj, str) and hasattr(obj, "__iter__"):
        return [ convert2serialize(v) for v in obj ]
    elif hasattr(obj, "__dict__"):
        return {
            k: convert2serialize(v)
            for k, v in obj.__dict__.items()
            if not callable(v) and not k.startswith('_')
        }
    else:
        return obj

def convert_pos(tokens: list, first_row=1, first_col=0):
    row_counter = 0
    col_counter = 0
    for t in tokens:
        row = row_counter + first_row
        col1 = col_counter + first_col
        col2 = col1 + len(t.value)
        t.pos2d = [[row, col1], [row, col2]]

        col_counter += len(t.value)
        if t.token == TS_NEW_LINE:
            row_counter += 1
            col_counter = 0

def pos2d_to_str(pos2d):
    return [f"{pos2d[0][0]}.{pos2d[0][1]}", f"{pos2d[1][0]}.{pos2d[1][1]}"]

