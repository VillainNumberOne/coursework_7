import tkinter as tk

class TextLineNumbers(tk.Canvas):
    def __init__(self, font, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None
        self.font = font

    def attach(self, text_widget):
        self.textwidget = text_widget
        
    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum, font=self.font)
            i = self.textwidget.index("%s+1line" % i)

class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        if command == 'get' and (args[0] == 'sel.first' and args[1] == 'sel.last') and not self.tag_ranges('sel'): return
        if command == 'delete' and (args[0] == 'sel.first' and args[1] == 'sel.last') and not self.tag_ranges('sel'): return

        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)

        if command in ('insert', 'delete', 'replace'):
                    self.event_generate("<<Change>>", when="tail")

        return result