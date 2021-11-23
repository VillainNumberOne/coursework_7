import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from code_input import *
from tokenizer import Tokenizer
from text_colors import TOKEN_TYPE_COLORS, ERROR_COLOR
from code_parser import *
import codecs
from utils import convert_pos, pos2d_to_str

class Window(tk.Frame):
    def __init__(self):

        self.font = ("Monaco", 12)
        self.window = tk.Tk()
        self.window.title("Code")
        self.window.configure(bg='white')
        self.window.geometry("1180x600")
        self.window.resizable(0, 0)

        self.menu()
        self.code_input_field()
        self.run_result_field()
        self.bnf()

        self.window.bind("<Control-r>", self.run_translator)


    def menu(self):
        menu = tk.Menu(self.window)
        self.window.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff = 0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="  Open  ", command=self.open_file)
        file_menu.add_command(label="  Close  ", command=self.close_file)

        run_menu = tk.Menu(menu, tearoff = 0)
        menu.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="  Run  ", command=self.on_btn_run)

    def code_input_field(self):

        self.text = CustomText(self.window, width=59, font=self.font, selectbackground="#a8ccff")
        self.vsb = tk.Scrollbar(self.window, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.text.tag_configure("bigfont", font=("Helvetica", "24", "bold"))
        self.linenumbers = TextLineNumbers(self.font, self.window, width=30)
        self.linenumbers.attach(self.text)

        self.linenumbers.grid(column=0, row=0, sticky="nsw")
        self.text.grid(column=1, row=0)
        self.vsb.grid(column=2, row=0, sticky="nse")

        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<KeyRelease>", self._on_text_modified)
        self.text.bind("<Configure>", self._on_change)

        for key in TOKEN_TYPE_COLORS:
            if TOKEN_TYPE_COLORS[key] is not None:
                self.text.tag_config(key, background=TOKEN_TYPE_COLORS[key][0], foreground=TOKEN_TYPE_COLORS[key][1])

        self.text.tag_config("error", background=ERROR_COLOR[0], foreground=ERROR_COLOR[1])

        # with codecs.open("code_example1.txt", "r", "utf-8") as f:
        #     self.text.insert(tk.END, f.read())

    def bnf(self):
        self.bnf = tk.Text(self.window, width = 65)
        self.bnf.grid(column=4, row=0, sticky="NE")
        with codecs.open("bnf.txt", "r", "utf-8") as f:
            self.bnf.insert(tk.END, f.read())


    def _on_text_modified(self, event):
        code_string = self.text.get("1.0", tk.END)
        tokens, tokenizer_error = Tokenizer(code_string).tokenize()

        if tokenizer_error is None:
            convert_pos(tokens)
            for t in tokens:
                pos2d = pos2d_to_str(t.pos2d)
                if t.type in TOKEN_TYPE_COLORS:
                    if TOKEN_TYPE_COLORS[t.type] is not None:
                        self.text.tag_add(t.type, pos2d[0], pos2d[1])
                else:
                    self.text.tag_add("default", pos2d[0], pos2d[1])
        

    def _on_change(self, event):
        self.linenumbers.redraw()

    def run_result_field(self):
        self.result_field = tk.Text(self.window, font=self.font)
        self.result_field.grid(column=0, row=1, columnspan=5, sticky="we")
    
    def open_file(self):
        pass

    def close_file(self):
        pass

    def run_translator(self, *args):
        self.result_field.delete("1.0", tk.END)
        code_string = self.text.get("1.0", tk.END)
        tokens, tokenizer_error = Tokenizer(code_string).tokenize()
        if tokenizer_error is not None:
            # code_string = self.text.get("1.0", tk.END)
            # pos2d = tokenizer_error.pos2d
            # self.text.tag_add("error", pos2d[0], pos2d[1])
            self.result_field.insert(tk.END, tokenizer_error.message)
        else:
            convert_pos(tokens)
            P = Parser(tokens)
            root_node, parser_error = P.ast()
            if parser_error is not None:
                pos2d = pos2d_to_str(parser_error.pos2d)
                self.text.tag_add("error", pos2d[0], pos2d[1])
                self.result_field.insert(tk.END, str(parser_error))
            else:
                cursor_pos = self.text.index(tk.INSERT)
                self.text.delete("1.0", tk.END)
                self.text.insert(tk.END, code_string[:-1])
                self.text.mark_set("insert", cursor_pos)
                
                _, message = root_node.expression.compute()
                self.result_field.insert(tk.END, message)

                with open("s.json", "w") as f:
                    f.write(root_node.to_json())
        

    def on_btn_run(self):
        self.run_translator()
            

    def mainloop(self):
        self.window.mainloop()
  
def main():
    window = Window()
    window.mainloop()

if __name__ == "__main__":
    main()