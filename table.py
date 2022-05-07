import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

class Table:

    def __init__(self, 
                master:tk.Misc,
                data:list[list],
                columns:list[str],
                width:int = 540, # 5 col
                height:int = 170, 
                stretch:bool=False):
        '''data:[[col1], [col2]]'''
        self.rowCount = max(list(map(len, data)))
        self.colCount = len(columns)
        self.selected:list[dict] = []
        self.selectedNew:dict = {}

        def wheelX(event):
            a= int(-(event.delta)/60)
            self.canvas.xview_scroll(a, 'units')

        maxwidth = 63 * (1 + self.colCount)
        self.canvas = tk.Canvas(master, width=width, height=height, scrollregion=(0, 0, maxwidth, 670))

        self.middle = ttk.Frame(self.canvas)
        self.middle.pack(side='left', fill='both')

        vbar = ttk.Scrollbar(master, orient='vertical')
        vbar.grid(row=0, column=1, padx=(0, 2), pady=2, sticky='ns')
        vbar.configure(command=self.canvas.yview)
        hbar = ttk.Scrollbar(master, orient='horizontal')
        hbar.grid(row=1, column=0, padx=2, pady=(0, 2), sticky='ew')
        hbar.configure(command=self.canvas.xview)

        self.canvas.config(yscrollcommand=vbar.set)
        self.canvas.config(xscrollcommand=hbar.set)
        self.canvas.create_window(0, 0, window=self.middle, anchor='nw')  #create_window
        self.canvas.grid(row=0, column=0, padx=(2, 0), pady=(2, 0), sticky='news')
        self.canvas.bind('<MouseWheel>', wheelX)

        # Row Head
        self.rowHeadTab = ttk.Treeview(self.middle, columns=['#'], height=32, selectmode='browse', show='headings')
        self.rowHeadTab.pack(side='left', fill='y', anchor='n', padx=(0, 3))
        self.rowHeadTab.heading('#', text='#', command=self.selectAllClear)
        self.rowHeadTab.column('#', width=22, stretch=stretch, anchor='center')
        for i in range(32):
            self.rowHeadTab.insert('', 'end', values=[i])
        self.rowHeadTab.bind('<<TreeviewSelect>>', self.selectRowHead)
        # Tab
        self.tabs:list[ttk.Treeview] = []
        for i, col in enumerate(columns):
            colTab = ttk.Treeview(self.middle, columns=['col'], height=32, selectmode='browse', show='headings')
            colTab.pack(side='left', fill='y', anchor='n')
            colTab.heading('col', text=col, command=lambda x=i: self.selectColumnClear(x))
            colTab.column('col', width=60, stretch=stretch)
            for x in data[i]:
                colTab.insert('', index='end', values=[x])
            self.tabs.append(colTab)
            colTab.bind('<<TreeviewSelect>>', lambda e, x=i: self.select(e, x))

    def destroy(self):
        for coltab in self.tabs:
            coltab.destroy()
        self.rowHeadTab.destroy()
        self.canvas.destroy()

    def selectRowHead(self, event):
        iids = self.rowHeadTab.selection()
        if iids:
            iid = iids[0]
            ind = self.rowHeadTab.index(iid)
            for coltab in self.tabs:
                iids = coltab.get_children()
                if len(iids) > ind:
                    coltab.selection_set(iids[ind])
                else:
                    tmp = coltab.selection()
                    coltab.selection_remove(tmp)
    def select(self, event=None, colInd=None):
        self.selected:list[dict] = []
        for col, coltab in enumerate(self.tabs):
            iids = coltab.selection()
            for iid in iids:
                row = coltab.index(iid)
                value = coltab.item(iid, 'values')[0]
                self.selected.append({'row': row, 'col': col, 'iid': iid, 'value': value})
        if event:
            iids = event.widget.selection()
            if iids:
                iid = iids[0]
                row = event.widget.index(iid)
                value = event.widget.item(iid, 'values')[0]
                self.selectedNew = {'row': row, 'col': colInd, 'iid': iid, 'value': value}
                self.rowHeadTab.event_generate('<<CeilClick>>')
    def selectAllClear(self):
        for coltab in self.tabs:
            tmp = coltab.selection()
            coltab.selection_remove(tmp)
        tmp = self.rowHeadTab.selection()
        self.rowHeadTab.selection_remove(tmp)
    def selectColumnClear(self, x):
        coltab = self.tabs[x]
        tmp = coltab.selection()
        coltab.selection_remove(tmp)

    def setValue(self, data:list):
        if len(data) != len(self.selected):
            raise ValueError('The input data length is not correct.')
        for value in data:
            for sel in self.selected:
                self.tabs[sel['col']].item(sel['iid'], values=[value])
        self.selectAllClear()


if __name__ == '__main__':
    app = tk.Tk()
    tab = Table(app, [['a','b','c'],['x','y','z'],['eng,4011']], ['1','2','3'])
    app.mainloop()