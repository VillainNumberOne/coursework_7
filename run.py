from tokenizer import Tokenizer
from code_parser import *
import json
from utils import convert_pos

def prepare(code_string):
    return code_string.replace("\n", " ")

def main():
    with open("code_example1.txt", encoding = 'utf-8', mode="r") as f:
        code = f.read()

    tokens, errors = Tokenizer(code).tokenize()
    # print(tokens)
    if errors is not None:
        print(errors)
    else:
        convert_pos(tokens)
        for t in tokens:
            print(t.__dict__)

        P = Parser(tokens)
        root_node, errors = P.ast()
        print(root_node)
        print(errors)
        
        if root_node is not None:
            with open("s.json", "w") as f:
                f.write(root_node.to_json())

if __name__ == '__main__':
    main()