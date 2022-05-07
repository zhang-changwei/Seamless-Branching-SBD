import re
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import xml.etree.ElementTree as ET
from assets import *
from timeutil import *
from sorttracks import TrackSort
from table import Table

class App:

    def __init__(self):
        self.ui = tk.Tk()
        self.ui.title('Scenarist Ctrl Gui')

        self.showBasic()
        self.showButtons()
        self.menu = MenuDisplay(self.ui, parent=self)

        self.videos:list[Video] = []
        self.audios:list[Audio] = []
        self.pgs:list[PG] = []
        self.playLists:list[PlayList] = []
        self.playItems:list[PlayItem] = []
        self.clips:list[Clip] = []

        self.ui.bind('<<CeilClick>>', self.updateInfo)
        self.ui.mainloop()

    def openSBDPRJ(self):
        sbdprjPath = filedialog.askopenfilename(title='Open Sbdprj Project', filetypes=[('sbdprj file', '*.sbdprj')])
        if sbdprjPath:
            self.tree = ET.parse(sbdprjPath)
            self.root = self.tree.getroot()

            self.getXmlNodes()

            # init
            self.videos:list[Video] = []
            self.audios:list[Audio] = []
            self.pgs:list[PG] = []
            self.playLists:list[PlayList] = []
            self.playItems:list[PlayItem] = []
            self.clips:list[Clip] = []
            for i in self.videoInfo:
                self.videos.append(Video(i))
            for i in self.audioInfo:
                self.audios.append(Audio(i))
            for i in self.pgInfo:
                self.pgs.append(PG(i))
            for i in self.clipInfoBlock:
                ci = Clip(i)
                ci.getVideos(self.videos)
                ci.getAudios(self.audios)
                ci.getPGs(self.pgs)
                self.clips.append(ci)
            for i in self.playItemBlock:
                pi = PlayItem(i)
                pi.getClip(self.clips)
                self.playItems.append(pi)
            for i in self.playListBlock:
                pl = PlayList(i)
                pl.getPlayItems(self.playItems)
                self.playLists.append(pl)

            self.updatePlayList()
            # tables
            self.deleteAsset()
            self.showAsset()

            self.unencrypt()

    def getXmlNodes(self):
        # xml nodes
        dbFileInfo = self.root.find('DBFileInfo')
        self.discProjectInfo = self.root.find('DiscProjectInfo')
        netProjectInfo = self.root.find('NetProjectInfo')
        folderBlock = self.root.find('Fold_Block')
        disc = self.root.find('Disc')
        net = self.root.find('Net')

        self.playListBlock = disc.find('PlayList_Block')
        self.playItemBlock = disc.find('PlayItem_Block')
        self.clipInfoBlock = disc.find('ClipInfo_Block')        

        self.videoInfo = disc.find('Asset_Block/VideoInfo')
        self.audioInfo = disc.find('Asset_Block/AudioInfo')
        self.pgInfo    = disc.find('Asset_Block/PGInfo')

        self.layoutBlock = disc.find('Layout_Block')
        self.aacsInfoBlock = disc.find('AACSInfo_Block')

    def showBasic(self):
        gridT = ttk.Frame(self.ui)
        gridT.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.playListVar = tk.StringVar(value='')
        ttk.Label(gridT, text='PlayList').grid(row=0, column=0, padx=5, pady=(5, 2))
        self.playListDropdown = ttk.Combobox(gridT, textvariable=self.playListVar, values=[], state='readonly')
        self.playListDropdown.grid(row=0, column=1, padx=5, pady=(5, 2))
        # ttk.Button(gridT, text='Import PlayItems from BDInfo', command=self.importBDInfo).grid(row=0, column=2, padx=5, pady=(5, 2))

        self.playListDropdown.bind('<<ComboboxSelected>>', self.selectPlayList)

        gridB = ttk.Frame(self.ui)
        gridB.grid(row=1, column=0, padx=5, pady=(0, 5))

        gridB1 = ttk.Frame(gridB)
        gridB1.grid(row=1, column=0, rowspan=3, padx=4, sticky='n')
        self.gridB2 = ttk.Frame(gridB, relief='groove')
        self.gridB2.grid(row=1, column=1, padx=4, sticky='n')
        self.gridB3 = ttk.Frame(gridB, relief='groove')
        self.gridB3.grid(row=3, column=1, padx=4, sticky='n')

        ttk.Label(gridB, text='Asset').grid(row=0, column=0, pady=(0, 2), sticky='n')
        ttk.Label(gridB, text='Audio').grid(row=0, column=1, pady=(0, 2), sticky='n')
        ttk.Label(gridB, text='PG').grid(row=2, column=1, sticky='n')

        self.tableAsset = ttk.Treeview(gridB1, columns=['type', 'name', 'index', 'pos'], displaycolumns=['type', 'name', 'index'], show='headings', height=20)
        self.tableAsset.grid(row=1, column=0, sticky='news')
        scrollY = ttk.Scrollbar(gridB1, orient='vertical', command=self.tableAsset.yview)
        scrollY.grid(row=1, column=1, sticky='ns')
        scrollX = ttk.Scrollbar(gridB1, orient='horizontal', command=self.tableAsset.xview)
        scrollX.grid(row=2, column=0, sticky='we')
        self.tableAsset.config(yscrollcommand=scrollY.set, xscrollcommand=scrollX.set)

        self.tableAsset.heading('type', text='type')
        self.tableAsset.column('type', width=50, stretch=False)
        self.tableAsset.heading('name', text='name', command=lambda x=1: self.sortAsset(x))
        self.tableAsset.column('name', width=200)
        self.tableAsset.heading('index', text='index', command=lambda x=2: self.sortAsset(x))
        self.tableAsset.column('index', width=50, stretch=False)

        self.tableAudio = tk.Canvas(self.gridB2, width=560, height=170, scrollregion=(0, 0, 2000, 670))
        self.tableAudio.pack()
        self.tablePG = tk.Canvas(self.gridB3, width=560, height=170, scrollregion=(0, 0, 2000, 670))
        self.tablePG.pack()

    def showButtons(self):
        # btns
        gridB = ttk.Frame(self.ui)
        gridB.grid(row=3, column=0, padx=5, pady=(0, 5), sticky='we')
        gridB1 = ttk.Labelframe(gridB, text='Asset')
        gridB1.grid(row=0, column=0, padx=4, pady=2, sticky='ns')
        gridB2 = ttk.Labelframe(gridB, text='Misc')
        gridB2.grid(row=0, column=1, padx=4, pady=2, sticky='ns')
        gridB3 = ttk.Labelframe(gridB, text='Synchronization')
        gridB3.grid(row=0, column=2, padx=4, pady=2, sticky='ns')
        gridB4 = ttk.Labelframe(gridB, text='STN')
        gridB4.grid(row=0, column=3, padx=4, pady=2, sticky='ns')
        gridB5 = ttk.Labelframe(gridB, text='Info')
        gridB5.grid(row=0, column=4, padx=4, pady=2, sticky='ns')

        ttk.Button(gridB1, text='Delete Audio Clips', command=self.popAudio) \
            .grid(row=0, column=0, padx=4, pady=2, sticky='we')
        ttk.Button(gridB1, text='Delete PG Clips', command=self.popPG) \
            .grid(row=1, column=0, padx=4, pady=2, sticky='we')
        ttk.Button(gridB1, text='Append Audio Clips', command=self.appendAudio) \
            .grid(row=2, column=0, padx=4, pady=2, sticky='we')
        ttk.Button(gridB1, text='Append PG Clips', command=self.appendPG) \
            .grid(row=3, column=0, padx=4, pady=2, sticky='we')

        ttk.Button(gridB2, text='Set Audio Language Code', command=self.setAudioLanguageCode) \
            .grid(row=0, column=0, padx=4, pady=2, sticky='we')
        ttk.Button(gridB2, text='Set PG Language Code', command=self.setPGLanguageCode) \
            .grid(row=1, column=0, padx=4, pady=2, sticky='we')
        ttk.Button(gridB2, text='Seamless Connection', command=self.setSeamless) \
            .grid(row=3, column=0, padx=4, pady=2, sticky='we')

        ttk.Button(gridB3, text='Sync (for Sliced Audios)', command=self.syncSlicedAudioTimeInfo) \
            .grid(row=0, column=0, padx=4, pady=2, sticky='we')
        ttk.Button(gridB3, text='Sync (for Sliced PGs)', command=self.syncSlicedPGTimeInfo) \
            .grid(row=1, column=0, padx=4, pady=2, sticky='we')
        ttk.Button(gridB3, text='Sync (for Intact Audios)', command=self.syncIntactAudioTimeInfo) \
            .grid(row=2, column=0, padx=4, pady=2, sticky='we')

        ttk.Button(gridB4, text='Hide Audios', command=self.hideAudio) \
            .grid(row=0, column=0, padx=4, pady=2, sticky='we')
        ttk.Button(gridB4, text='Hide PGs', command=self.hidePG) \
            .grid(row=1, column=0, padx=4, pady=2, sticky='we')
        ttk.Button(gridB4, text='Set PID of Audios', command=self.setAudioPID) \
            .grid(row=2, column=0, padx=4, pady=2, sticky='we')
        ttk.Button(gridB4, text='Set PID of PGs', command=self.setPGPID) \
            .grid(row=3, column=0, padx=4, pady=2, sticky='we')

        self.info: dict[str, Union[tk.IntVar, tk.StringVar]] = {
            'Name': tk.StringVar(value=''),
            'Offset': tk.IntVar(value=0),
            'Duration': tk.IntVar(value=0),
            'OffsetFromVideo': tk.IntVar(value=0)
        }
        ttk.Label(gridB5, text='Name').grid(row=0, column=0, padx=2, pady=2, sticky='e')
        ttk.Label(gridB5, text='Offset').grid(row=1, column=0, padx=2, pady=2, sticky='e')
        ttk.Label(gridB5, text='Duration').grid(row=2, column=0, padx=2, pady=2, sticky='e')
        ttk.Label(gridB5, text='OffsetFromVideo').grid(row=3, column=0, padx=2, pady=2, sticky='e')
        ttk.Entry(gridB5, textvariable=self.info['Name'], state='readonly').grid(row=0, column=1, padx=2, pady=2, sticky='we')
        ttk.Entry(gridB5, textvariable=self.info['Offset'], state='readonly').grid(row=1, column=1, padx=2, pady=2, sticky='we')
        ttk.Entry(gridB5, textvariable=self.info['Duration'], state='readonly').grid(row=2, column=1, padx=2, pady=2, sticky='we')
        ttk.Entry(gridB5, textvariable=self.info['OffsetFromVideo'], state='readonly').grid(row=3, column=1, padx=2, pady=2, sticky='we')

    def updatePlayList(self):
        '''init playList Dropdown values'''
        plValues = []
        for playList in self.playLists:
            plValues.append(playList.name)
        self.playListDropdown.config(values=plValues)
    def selectPlayList(self, event=None):
        for playList in self.playLists:
            if playList.name == self.playListVar.get():
                self.playList = playList
                break

        self.numOfClip = len(self.playList.playItems)
        self.magicNums:list[str] = []
        self.audioCount = 0
        self.pgCount = 0
        self.audioData: list[list[str]] = []
        self.pgData: list[list[str]] = []

        for pi in self.playList.playItems:
            # video
            videos = pi.clip.videos
            if len(videos) != 1:
                raise ValueError('The number of video in this playList is not 1.')
            self.fps = videos[0].fps
            # magicNum
            magicNum = pi.clip.magicNum
            if magicNum:
                self.magicNums.append(magicNum)
            else:
                raise ValueError('The clip name format is not correct. \
                                  It should look like these: Clip#0, 00000, etc.')
            # audio
            count = len(pi.clip.audios)
            self.audioCount = max(self.audioCount, count)
            tmp = []
            for i, ai in enumerate(pi.clip.audios):
                tmp.append(ai.languageCode + ',')
            self.audioData.append(tmp)
            # PG
            count = len(pi.clip.pgs)
            self.pgCount = max(self.pgCount, count)
            tmp = []
            for i, si in enumerate(pi.clip.pgs):
                tmp.append(si.languageCode + ',')
            self.pgData.append(tmp)
        # STN
        self.audioOrder:dict[int, list] = {}
        self.pgOrder:dict[int, list] = {}
        self.audioOrderMeta:list[list[str, int, bool]] = []
        self.pgOrderMeta:list[list[str, int, bool]] = []
        for i, pi in enumerate(self.playList.playItems):
            for ai in pi.playItemAudioInfs:
                for j, aj in enumerate(pi.clip.audios):
                    if aj.id == ai.streamid:
                        self.audioData[i][j] = aj.languageCode + ',' + str(ai.PID)
                        break
        for i, pi in enumerate(self.playList.playItems):
            for si in pi.playItemPGInfs:
                for j, sj in enumerate(pi.clip.pgs):
                    if sj.id == si.streamid:
                        self.pgData[i][j] = sj.languageCode + ',' + str(si.PID)
                        break
        # table
        self.tableAudio.destroy()
        self.tablePG.destroy()
        self.tableAudio = Table(self.gridB2, data=self.audioData, columns=self.magicNums)
        self.tablePG = Table(self.gridB3, data=self.pgData, columns=self.magicNums)

    def showAsset(self):
        for i, vi in enumerate(self.videos):
            self.tableAsset.insert('', 'end', values=[vi.type, vi.name, vi.index, i])
        for i, ai in enumerate(self.audios):
            self.tableAsset.insert('', 'end', values=[ai.type, ai.name, ai.index, i])
        for i, si in enumerate(self.pgs):
            self.tableAsset.insert('', 'end', values=[si.type, si.name, si.index, i])
    def deleteAsset(self):
        iids = self.tableAsset.get_children()
        for iid in iids:
            self.tableAsset.delete(iid)
    def sortAsset(self, sx=1):
        '''sx = 1, sort name, sx = 2, sort index'''
        vList = []
        aList = []
        sList = []
        iids = self.tableAsset.get_children()
        for iid in iids:
            values = self.tableAsset.item(iid, option='values')
            if values[0] == 'Video':
                vList.append([iid, values])
            elif values[0] == 'Audio':
                aList.append([iid, values])
            elif values[0] == 'PG':
                sList.append([iid, values])
            self.tableAsset.detach(iid)
        # sort
        vList.sort(key=lambda x: x[1][sx])
        aList.sort(key=lambda x: x[1][sx])
        sList.sort(key=lambda x: x[1][sx])
        # show
        for i in vList:
            self.tableAsset.move(i[0], '', 'end')
        for i in aList:
            self.tableAsset.move(i[0], '', 'end')
        for i in sList:
            self.tableAsset.move(i[0], '', 'end')       

    def setAudioLanguageCode(self):
        lang = input('Please input Language Code: ')
        data = []
        for sel in self.tableAudio.selected:
            self.playList.playItems[sel['col']].clip.audios[sel['row']].languageCode = lang
            data.append(lang + ',' + sel['value'].split(',')[-1])
        self.tableAudio.setValue(data)
    def setPGLanguageCode(self):
        lang = input('Please input Language Code: ')
        data = []
        for sel in self.tablePG.selected:
            self.playList.playItems[sel['col']].clip.pgs[sel['row']].languageCode = lang
            data.append(lang + ',' + sel['value'].split(',')[-1])
        self.tablePG.setValue(data)

    def syncSlicedAudioTimeInfo(self):
        for sel in self.tableAudio.selected:
            pi = self.playList.playItems[sel['col']]
            # unit = pi.clip.audios[sel['row']].unitDuration
            # if unit == 1:
            #     continue_ = input('[Warning] The unit duration of this audio is missing. Continue? [y/n] ')
            #     if continue_.lower() != 'y':
            #         return
            dur = frame2PTS(pi.duration/1875, self.fps, unit=1)
            if dur <= pi.clip.audios[sel['row']].duration:
                pi.clip.clipAudioInfos[sel['row']].duration = dur
            else:
                raise ValueError('The audio clip in clip#{} is not long enough.'.format(pi.clip.magicNum))
    def syncSlicedPGTimeInfo(self):
        for sel in self.tablePG.selected:
            pi = self.playList.playItems[sel['col']]
            pi.clip.clipPGInfos[sel['row']].offsetFromVideo = pi.clip.pgs[sel['row']].start
            if pts2Frame(pi.clip.pgs[sel['row']].duration, self.fps) > (pi.duration)/1875:
                print('[Warning] The PG clip is longer than clip#{} duration'.format(pi.clip.magicNum))
    def syncIntactAudioTimeInfo(self):
        for sel in self.tableAudio.selected:
            pi = self.playList.playItems[sel['col']]
            # unit = pi.clip.audios[sel['row']].unitDuration
            # if unit == 1:
            #     continue_ = input('[Warning] The unit duration of this audio is missing. Continue? [y/n] ')
            #     if continue_.lower() != 'y':
            #         return
            dur = frame2PTS(pi.duration/1875, self.fps, unit=1)
            if dur <= pi.clip.audios[sel['row']].duration:
                pi.clip.clipAudioInfos[sel['row']].duration = dur
            else:
                raise ValueError('The audio clip in clip#{} is not long enough.'.format(pi.clip.magicNum))
            start = frame2PTS(pi.intime/1875, self.fps, unit=1)
            pi.clip.clipAudioInfos[sel['row']].offset = start

    def hideAudio(self):
        data = []
        for sel in self.tableAudio.selected:
            pi = self.playList.playItems[sel['col']]
            audio = pi.clip.audios[sel['row']]
            pi.popAudioInf(audio)
            data.append(sel['value'].split(',')[0] + ',')
        self.tableAudio.setValue(data)
    def hidePG(self):
        data = []
        for sel in self.tablePG.selected:
            pi = self.playList.playItems[sel['col']]
            pg = pi.clip.pgs[sel['row']]
            pi.popPGInf(pg)
            data.append(sel['value'].split(',')[0] + ',')
        self.tablePG.setValue(data)
    def setAudioPID(self):
        pid = input('Please input PID, it should look like these 4608, 0x1200: ')
        if pid.startswith('0x'):
            pid = int(pid, base=16)
        else:
            pid = int(pid)
        data = []
        for sel in self.tableAudio.selected:
            pi = self.playList.playItems[sel['col']]
            audio = pi.clip.audios[sel['row']]
            success = pi.setAudioInf(audio, pid)
            if success:
                data.append(sel['value'].split(',')[0] + ',' + str(pid))
            else:
                data.append(sel['value'])
        self.tableAudio.setValue(data)
    def setPGPID(self):
        pid = input('Please input PID, it should look like these 4608, 0x1200: ')
        if pid.startswith('0x'):
            pid = int(pid, base=16)
        else:
            pid = int(pid)
        data = []
        for sel in self.tablePG.selected:
            pi = self.playList.playItems[sel['col']]
            pg = pi.clip.pgs[sel['row']]
            success = pi.setPGInf(pg, pid)
            if success:
                data.append(sel['value'].split(',')[0] + ',' + str(pid))
            else:
                data.append(sel['value'])
        self.tablePG.setValue(data)

    def popAudio(self):
        for sel in self.tableAudio.selected:
            pi = self.playList.playItems[sel['col']]
            audio = pi.clip.audios[sel['row']]
            pi.clip.popAudio(audio)
            self.tableAudio.tabs[sel['col']].delete(sel['iid'])
    def popPG(self):
        for sel in self.tablePG.selected:
            pi = self.playList.playItems[sel['col']]
            pg = pi.clip.pgs[sel['row']]
            pi.clip.popPG(pg)
            self.tablePG.tabs[sel['col']].delete(sel['iid'])
    def appendAudio(self):
        iids = self.tableAsset.selection()
        assets:list[Audio] = []
        if iids:
            for iid in iids:
                values = self.tableAsset.item(iid, option='values')
                if values[0] != 'Audio':
                    raise TypeError('This is not an audio asset.')
                assets.append(self.audios[int(values[3])])
            self.popup = TopYesNoDisplay(self.ui, title='Sort Tracks')

            self.tableSort = TrackSort(self.popup.gridT, self.magicNums, assets=assets)
            self.tableSort.grid(row=0, column=0, sticky='news')

            scrollY = ttk.Scrollbar(self.popup.gridT, orient='vertical', command=self.tableSort.yview)
            scrollY.grid(row=0, column=1, sticky='ns')
            self.tableSort.config(yscrollcommand=scrollY.set)

            gridB = ttk.Frame(self.popup.gridT)
            gridB.grid(row=1, column=0, columnspan=2, pady=(20, 0))
            ttk.Button(gridB, text='Move Up', command=self.tableSort.moveUp).pack(side='left', padx=(0, 10))
            ttk.Button(gridB, text='Move Down', command=self.tableSort.moveDown).pack(side='right', padx=(10, 0))

            self.ui.bind('<<YesNo>>', self.appendAudioOK)
    def appendAudioOK(self, event):
        if self.popup.clicked == 'Yes':
            audios = self.tableSort.sortedAssets

            if len(audios) != self.numOfClip:
                raise ValueError('Audio clip number is not correct.')
            for i, ai in enumerate(audios):
                if ai:
                    pi = self.playList.playItems[i]
                    success = pi.clip.appendAudio(ai)
                    if success:
                        self.tableAudio.tabs[i].insert('', 'end', values=[ai.languageCode+','])
        self.tableSort.destroy()
        self.popup.destroy()
        self.ui.unbind('<<YesNo>>')
    def appendPG(self):
        iids = self.tableAsset.selection()
        assets:list[PG] = []
        if iids:
            for iid in iids:
                values = self.tableAsset.item(iid, option='values')
                if values[0] != 'PG':
                    raise TypeError('This is not a PG asset.')
                assets.append(self.pgs[int(values[3])])
            self.popup = TopYesNoDisplay(self.ui, title='Sort Tracks')

            self.tableSort = TrackSort(self.popup.gridT, self.magicNums, assets=assets)
            self.tableSort.grid(row=0, column=0, sticky='news')

            scrollY = ttk.Scrollbar(self.popup.gridT, orient='vertical', command=self.tableSort.yview)
            scrollY.grid(row=0, column=1, sticky='ns')
            self.tableSort.config(yscrollcommand=scrollY.set)

            gridB = ttk.Frame(self.popup.gridT)
            gridB.grid(row=1, column=0, columnspan=2, pady=(20, 0))
            ttk.Button(gridB, text='Move Up', command=self.tableSort.moveUp).pack(side='left', padx=(0, 10))
            ttk.Button(gridB, text='Move Down', command=self.tableSort.moveDown).pack(side='right', padx=(10, 0))

            self.ui.bind('<<YesNo>>', self.appendPGOK)
    def appendPGOK(self, event):
        if self.popup.clicked == 'Yes':
            pgs = self.tableSort.sortedAssets

            if len(pgs) != self.numOfClip:
                raise ValueError('PG clip number is not correct.')
            for i, si in enumerate(pgs):
                if si:
                    pi = self.playList.playItems[i]
                    success = pi.clip.appendPG(si)
                    if success:
                        self.tablePG.tabs[i].insert('', 'end', values=[si.languageCode+','])
        self.tableSort.destroy()
        self.popup.destroy()
        self.ui.unbind('<<YesNo>>')

    def updateInfo(self, event=None):
        if event.widget is self.tableAudio.rowHeadTab:
            sel = self.tableAudio.selectedNew
            pi = self.playList.playItems[sel['col']]
            audio = pi.clip.audios[sel['row']]
            clipAudioInfo = pi.clip.clipAudioInfos[sel['row']]
            self.info['Name'].set(audio.name)
            self.info['Offset'].set(clipAudioInfo.offset)
            self.info['Duration'].set(clipAudioInfo.duration)
            self.info['OffsetFromVideo'].set(clipAudioInfo.offsetFromVideo)
        elif event.widget is self.tablePG.rowHeadTab:
            sel = self.tablePG.selectedNew
            pi = self.playList.playItems[sel['col']]
            pg = pi.clip.pgs[sel['row']]
            clipPGInfo = pi.clip.clipPGInfos[sel['row']]
            self.info['Name'].set(pg.name)
            self.info['Offset'].set(clipPGInfo.offset)
            self.info['Duration'].set(clipPGInfo.duration)
            self.info['OffsetFromVideo'].set(clipPGInfo.offsetFromVideo)

    def importBDInfo(self):
        bdinfoPath = filedialog.askopenfilename(title='Open Sbdprj Project', filetypes=[('sbdprj file', '*.sbdprj')])
        if bdinfoPath:
            magicNums = []
            with open(bdinfoPath) as bdinfo:
                for line in bdinfo.readlines():
                    mn = line.strip()[:5]
                    if len(mn) == 5 and mn.isnumeric():
                        magicNums.append(mn)
            if len(magicNums) != len(self.magicNums):
                raise ValueError('Clip number is not correct.')
            for i, mn in enumerate(magicNums):
                for clip in self.clips:
                    if clip.magicNum == mn:
                        # how to deal with PID info in playItem
                        pi = self.playList.playItems[i]
                        pi.clip.delPlayItem(pi)
                        pi.setClip(clip)
                        pi.clip.setPlayItem(pi)
                        break
                else:
                    raise ValueError(f'Cannot find clip related to {mn}.m2ts')
            self.selectPlayList()


    def setSeamless(self):
        trigger = True
        for pi in self.playList.playItems:
            if trigger:
                trigger = False
                pi.connection = '1'
                continue
            pi.connection = '5'
        print('Success!')
    def setBDID(self):
        bdidDict = {} # key: wrong bdid, value: right bdid
        for ci in self.clips:
            if ci.magicNum:
                bdidDict[ci.bdid] = ci.magicNum
                ci.bdid = ci.magicNum
            else:
                print('[Warning] BDID of clip {} cannot be deduced.'.format(ci.node.find('Name').text))
        for content in self.layoutBlock.find('Contents'):
            conM = re.search('(.+)\.(.+)', content.find('Name').text)
            con5, conSuffix = conM.group(1), conM.group(2)
            if (conSuffix=='m2ts' or conSuffix=='clpi') and bdidDict.get(con5)!=None:
                content.find('Name').text = bdidDict[con5]
                content.find('VPFilename').text = re.sub('\d{5}', bdidDict[con5], content.find('VPFilename').text)
        aacsCPSClipList = self.aacsInfoBlock[0].find('InternalAACSInfo/CPSUnitKeyFile/CPSUnitInfoList')[0].find('ClipList')
        for clipID in aacsCPSClipList:
            c5 = '%05d' % int(clipID.text)
            if c5 in bdidDict.keys():
                clipID.text = str(int(bdidDict[c5]))
        print('Success!')

    def unencrypt(self):
        applicationVersion = self.discProjectInfo[0][0]
        applicationVersion.text = '5.6.0.0000'
        

class MenuDisplay(tk.Menu):

    def __init__(self, master=None, parent:App=None):
        def version():
            messagebox.showinfo('Version', 'Current Version: v0.0.1')
        def about():
            messagebox.showinfo('About', 'Version: v0.0.1\nAuthor: chaaaaang\nCopyright (c): 2022 chaaaaang')

        self.parent = parent
        super().__init__(master, tearoff=False)
        master.config(menu=self)

        self.fileMenu = tk.Menu(master=self, tearoff=False)
        self.optionMenu = tk.Menu(master=self, tearoff=False)
        self.helpMenu = tk.Menu(master=self, tearoff=False)
        self.add_cascade(label='File', menu=self.fileMenu)
        self.add_cascade(label='Option', menu=self.optionMenu)
        self.add_cascade(label='Help', menu=self.helpMenu)

        self.fileMenu.add_command(label='Open', command=self.open)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label='Save', command=self.save)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label='Close', command=self.close)

        self.optionMenu.add_command(label='Set BDID', command=self.setBDID)

        self.helpMenu.add_command(label='Version', command=version)
        self.helpMenu.add_command(label='About', command=about)

    def open(self):
        self.parent.openSBDPRJ()

    def save(self):
        outputPath = filedialog.asksaveasfilename(title='Save Sbdprj Project', filetypes=[('sbdprj file', '*.sbdprj')])
        if outputPath:
            if not outputPath.endswith('.sbdprj'):
                outputPath += '.sbdprj'
            # beautify
            for clip in self.parent.clips:
                clip.beautify()
            for pi in self.parent.playItems:
                pi.beautify()
            self.parent.tree.write(outputPath, encoding='utf-8', xml_declaration=True)

    def close(self):
        self.parent.ui.destroy()

    def setBDID(self):
        self.parent.setBDID()

class TopUniversalDisplay(tk.Toplevel):

    def __init__(self, master=None, title='TopLevel', parent=None):
        super().__init__(master)
        self.parent = parent
        self.title(title)
        self.middle_display()

    def middle_display(self):
        def del_win(): 
            pass
        self.protocol('WM_DELETE_WINDOW', del_win)
        self.attributes('-toolwindow', 1) # 无最大化，最小化
        self.attributes('-topmost', 1) # 窗口置顶其它窗体之上
        self.transient(self.master) # 窗口只置顶master之上
        self.resizable(False, False) # 不可调节窗体大小
        self.grab_set() # 转化模式，不关闭弹窗就不能进行别的操作

class TopYesNoDisplay(TopUniversalDisplay):
    
    def __init__(self, master=None, title='TopLevel', parent=None):
        super().__init__(master, title, parent)

        self.gridT = ttk.Frame(self)
        self.gridT.pack(fill='x', padx=20, pady=(30, 10))
        gridB = ttk.Frame(self)
        gridB.pack(pady=(10, 30))
        self.yesBtn = ttk.Button(gridB, text='OK', command=self.clickYes)
        self.noBtn = ttk.Button(gridB, text='Cancel', command=self.clickNo)
        self.yesBtn.pack(side='left', padx=(0, 10))
        self.noBtn.pack(side='right', padx=(10, 0))

    def clickYes(self):
        self.clicked = 'Yes'
        self.master.event_generate('<<YesNo>>')

    def clickNo(self):
        self.clicked = 'No'
        self.master.event_generate('<<YesNo>>')

        
if __name__ == '__main__':
    App()