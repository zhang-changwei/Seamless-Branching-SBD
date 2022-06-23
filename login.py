import hashlib
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
gui = __import__('Seamless-Branching-SBD')

class LoginPage:

    keyList = [
        '41dacd539d1b070cabb7b3f4f149a3e20df968e693599ae9b02aeede993862b2',
        'f54a54159e0edc184bc49032a881b0cf1f1b84ff2dd0d175ec38d652aa9c4d4c'
    ]

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Login')
        self.passwordVar = tk.StringVar(value='')

        gridT = ttk.Frame(self.root)
        gridT.pack(fill='x', padx=20, pady=(30, 10))

        ttk.Label(gridT, text='Password').pack(side='left', padx=(0, 10))
        ttk.Entry(gridT, textvariable=self.passwordVar).pack(side='right', padx=(5, 5))
        ttk.Button(self.root, text='Confirm', command=self.login).pack(pady=(10, 30))

        self.root.mainloop()

    def login(self):
        sha = hashlib.sha256()
        sha.update(self.passwordVar.get().encode('utf_8'))
        sha.update('SBSBD'.encode('utf_8'))
        # print(sha.hexdigest())
        if sha.hexdigest() in self.keyList:
            self.root.destroy()
            gui.App()
        else:
            messagebox.showwarning('Seamless Branching Login', 'Wrong password!')

if __name__ == '__main__':
    LoginPage()