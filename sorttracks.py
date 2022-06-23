import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from assets import *
from typing import Union
from config import P

class TrackSort(ttk.Treeview):

    def __init__(self, master, magicNums:list[str], assets:Union[list[Audio],list[PG]]):
        self.assets = assets
        super().__init__(master, columns=['clip', 'asset'], 
                        height=min(len(magicNums), P.ui['TrackSort']['MaxRow']), # 16
                        selectmode='browse',
                        show='headings')
        self.heading('clip', text='clip')
        self.heading('asset', text='asset')
        self.column('clip', width=50)
        self.column('asset', width=200)

        data:list[list] = []

        # broadcast
        assetsTMP = assets.copy()
        if len(assetsTMP) == 1:
            for mn in magicNums:
                data.append([mn, assetsTMP[0].name])
        else:
            for mn in magicNums:
                for i, asset in enumerate(assetsTMP):
                    if asset.magicNum == mn:
                        data.append([mn, asset.name])
                        assetsTMP.pop(i)
                        break
                else:
                    data.append([mn, ''])
            while len(assetsTMP) > 0:
                for i, d in enumerate(data):
                    if not d[1]:
                        data[i][1] = assetsTMP[0].name
                        assetsTMP.pop(0)
                        break
                else:
                    break
        # show
        for d in data:
            self.insert('', 'end', values=d)

    @property
    def sortedAssets(self):
        sorted_:Union[list[Audio], list[PG]] = []
        iids = self.get_children()
        for iid in iids:
            value = self.item(iid, option='values')[1]
            if value:
                for asset in self.assets:
                    if asset.name == value:
                        sorted_.append(asset)
            else:
                sorted_.append(None)
        return sorted_

    def destroy(self):
        del self.assets
        return super().destroy()

    def moveUp(self):
        iids = self.selection()
        if iids:
            iid = iids[0]
            previid = self.prev(iid)
            if previid:
                index = self.index(previid)
                self.detach(iid)
                self.move(iid, '', index)
                self.selection_set(iid)
    def moveDown(self):
        iids = self.selection()
        if iids:
            iid = iids[0]
            nextiid = self.next(iid)
            if nextiid:
                index = self.index(nextiid)
                self.detach(iid)
                self.move(iid, '', index)
                self.selection_set(iid)