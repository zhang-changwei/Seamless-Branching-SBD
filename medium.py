import os
import re

class Medium:

    def __init__(self, type_='BluRay'):
        self.type_ = type_

    # for assets
    def magicNum(self, x:str):
        '''FilePath'''
        tmp = os.path.split(x)[1]
        mn = tmp[:5]
        if mn.isnumeric():
            return mn
    def index(self, x:str):
        '''FilePath'''
        tmp = os.path.split(x)[1]
        mn = tmp[:5]
        ind = x.split('.')[0][-2:]
        if mn.isnumeric() and ind.isnumeric():
            return int(ind)
    def magicNumPG(self, x:str):
        '''FilePath'''
        if 'slice' in x and 'clip' in x:
            mn = x.split('.')[-2][-5:]
            return mn
        tmp = os.path.split(x)[1]
        mn = tmp[:5]
        if mn.isnumeric():
            return mn
    def indexPG(self, x:str):
        '''FilePath'''
        if 'slice' in x and 'clip' in x:
            return
        try:
            tmp = os.path.split(x)[1]
            mn = tmp[:5]
            ind = x.split('.')[0].split('_')[2]
            if mn.isnumeric() and ind.isnumeric():
                return int(ind)
        except:
            pass
    def magicNumClip(self, x:str):
        '''Name'''
        mn = x[:5]
        if mn.isnumeric():
            return mn
        match = re.search('Clip#(\d+)', x, flags=re.I)
        if match:
            mn = '%05d' % int(match.group(1))
            return mn

class BluRay(Medium):

    def __init__(self):
        super().__init__('BluRay')

class UHDBluRay(Medium):

    def __init__(self):
        super().__init__('UHD BluRay')
