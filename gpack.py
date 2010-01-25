#! /usr/bin/env python

import os
import npyck
from Tkinter import *

def read_pydir(dir):
	
	dir_list = os.listdir(dir)
        for i in dir_list:
            if i.endswith(".py"):
                yield i

class inp_dialog(object):
	
    def __init__(self):

        self._root = Tk()
        self._value = ""
        self._build_installer = IntVar()
        self._build_installer.set(0)

        Label(self._root, text="main-file").pack()

        #self._input = Entry(self._root)
        #self._input.pack(padx = 5)

        # building installer doesn't work
        #Checkbutton(self._root, text = "build installer",
        #            variable = self._build_installer).pack()

        self._list = Listbox(self._root, activestyle = "dotbox")
        self._list.pack()
        self._list.bind("<<ListboxSelect>>", self.__cb_select)
        Button(self._root, text = "build", command=self.__build).pack(pady = 5)

        for i in read_pydir("."):
            self._list.insert('end', i)
        
    def __cb_select(self, event):

        sel = self._list.curselection()
        
    	if len(sel) > 0:
            self._value = self._list.get(sel[0])
            #self._input.delete('0', 'end')
            #self._input.insert('end', self._list.get(sel[0]))

    def __build(self):

        #self._value = self._input.get()

        self._root.destroy()

    def show(self):

        self._root.wait_window(self._root)
        return (self._value, self._build_installer.get())

if __name__ == '__main__':
	
    d = inp_dialog()
    (name, installer) = d.show()
    
    if name:
    	filename = 'pack.sh'
    	f = open(filename, 'w')
    	os.chmod(filename, 0764)
    	npyck.pack(name, read_pydir("."), f)
