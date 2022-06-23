from copy import deepcopy
import xml.etree.ElementTree as ET
from typing import Union, Optional
import os
import re
from config import P


class Video:

    FPS = {'1': 23.976, '2': 24, '3': 25, '4': 29.97}

    def __init__(self, node:ET.Element):
        self.node = node
        self.type = 'Video'
        self.id = node.attrib['ID']
        self.name = node.find('Name').text
        self.magicNum = P.medium.magicNum(node.find('FilePath').text)
        self.index = P.medium.index(node.find('FilePath').text)
        self.languageCode = 'und'
        self.fps = self.FPS[node.find('FrameRate').text]

class Audio:

    def __init__(self, node:ET.Element):
        self.node = node
        self.type = 'Audio'
        self.id = node.attrib['ID']
        self.name = node.find('Name').text
        self.magicNum = P.medium.magicNum(node.find('FilePath').text)
        self.index = P.medium.index(node.find('FilePath').text)
        self.duration = int(node.find('Duration').text)
        tmp = node.find('UnitDuration')
        if tmp != None:
            self.unitDuration = int(tmp.text)
        else:
            self.unitDuration = 1

    @property
    def languageCode(self):
        return self.node.find('LanguageCode').text
    @languageCode.setter
    def languageCode(self, value:str):
        self.node.find('LanguageCode').text = value


class PG:

    def __init__(self, node:ET.Element):
        self.node = node
        self.type = 'PG'
        self.id = node.attrib['ID']
        self.name = node.find('Name').text
        self.magicNum = P.medium.magicNumPG(node.find('FilePath').text)
        self.index = P.medium.indexPG(node.find('FilePath').text)
        self.start = int(node.find('StartTime').text)
        self.end = int(node.find('EndTime').text)
        self.duration = self.end - self.start

    @property
    def languageCode(self):
        return self.node.find('LanguageCode').text
    @languageCode.setter
    def languageCode(self, value:str):
        self.node.find('LanguageCode').text = value

class ClipStreamInfo:
    def __init__(self, node:ET.Element):
        self.node = node
        self.streamid = node.find('StreamAssetID').text
    @property
    def offset(self):
        return self.node.find('StreamTimeInfo/Offset').text
    @offset.setter
    def offset(self, value:Union[str, int]):
        self.node.find('StreamTimeInfo/Offset').text = str(int(value))
    @property
    def duration(self):
        return self.node.find('StreamTimeInfo/Duration').text
    @duration.setter
    def duration(self, value:Union[str, int]):
        self.node.find('StreamTimeInfo/Duration').text = str(int(value))
    @property
    def offsetFromVideo(self):
        return self.node.find('StreamTimeInfo/OffsetFromVideo').text
    @offsetFromVideo.setter
    def offsetFromVideo(self, value:Union[str, int]):
        self.node.find('StreamTimeInfo/OffsetFromVideo').text = str(int(value))

class Clip:

    def __init__(self, node:ET.Element):
        self.node = node
        self.id = node.attrib['ID']
        self.magicNum = P.medium.magicNumClip(node.find('Name').text)
        self.playItems:list = [] # playList ID: playItem
        self.videos:list[Video] = []
        self.audios:list[Audio] = []
        self.pgs:list[PG] = []
        if not self.hasRefPlayItem:
            self.loopStreamFormatter('RefPlayItemInfoList', 5, 5, 4)
        if not self.hasVideo:
            self.loopStreamFormatter('Loop_VideoStream', 6, 5, 4)
        if not self.hasAudio:
            self.loopStreamFormatter('LoopPrimaryAudioStream', 7, 5, 4)
        if not self.hasPG:
            self.loopStreamFormatter('LoopPGStream', 8, 5, 4)
        self.clipVideoInfos:list[ClipStreamInfo] = []
        self.clipAudioInfos:list[ClipStreamInfo] = []
        self.clipPGInfos:list[ClipStreamInfo] = []

    @property
    def bdid(self):
        return '%05d' % int(self.node.attrib['BDID'])
    @bdid.setter
    def bdid(self, value:str):
        self.node.attrib['BDID'] = str(int(value))

    @property
    def hasRefPlayItem(self):
        tmp = self.node.find('RefPlayItemInfoList')
        if tmp != None:
            return True
        else:
            return False
    @property
    def hasVideo(self):
        tmp = self.node.find('Loop_VideoStream')
        if tmp != None:
            return True
        else:
            return False
    @property
    def hasAudio(self):
        tmp = self.node.find('LoopPrimaryAudioStream')
        if tmp != None:
            return True
        else:
            return False
    @property
    def hasPG(self):
        tmp = self.node.find('LoopPGStream')
        if tmp != None:
            return True
        else:
            return False

    def loopStreamFormatter(self, tag='LoopPrimaryAudioStream', pos=7, text=5, tail=4):
        node = ET.Element(tag)
        node.text = '\n' + '  ' * text
        node.tail = '\n' + '  ' * tail
        self.node.insert(pos, node)
    def clipStreamInfoFormatter(self, asset:Union[Audio, PG], text=6, tail=5):
        dic = {
            'Audio': {'ClipStreamType': '1', 
                      'StreamObjectType': '4',
                      'Offset': '0',
                      'Duration': str(asset.duration),
                      'OffsetFromVideo': '0'},
            'PG':    {'ClipStreamType': '2', 
                      'StreamObjectType': '5',
                      'Offset': '0',
                      'Duration': str(asset.duration),
                      'OffsetFromVideo': '0'}
        }
        def formatter(tag, content, tail=6):
            n = ET.Element(tag)
            n.text = content
            n.tail = '\n' + '  ' * tail
            return n
        node = ET.Element('ClipStreamInfo')
        node.text = '\n' + '  ' * text
        node.tail = '\n' + '  ' * tail
        n1 = formatter('ParentObjectID', self.id, 6)
        n2 = formatter('ClipStreamType', dic[asset.type]['ClipStreamType'], 6)
        n3 = formatter('StreamAssetID', asset.id, 6)
        n4 = formatter('StreamObjectType', dic[asset.type]['StreamObjectType'], 6)
        sti = formatter('StreamTimeInfo', '\n' + '  ' * 7, 5)
        node.extend([n1, n2, n3, n4, sti])
        n5 = formatter('Offset', dic[asset.type]['Offset'], 7)
        n6 = formatter('Duration', dic[asset.type]['Duration'], 7)
        n7 = formatter('OffsetFromVideo', dic[asset.type]['OffsetFromVideo'], 6)
        sti.extend([n5, n6, n7])
        return node
    def refPlayItemInfoFormatter(self, playItem):
        def formatter(tag, content, tail=6):
            n = ET.Element(tag)
            n.text = content
            n.tail = '\n' + '  ' * tail
            return n
        node = ET.Element('RefPlayItemInfo')
        node.text = '\n' + '  ' * 6
        node.tail = '\n' + '  ' * 4
        n1 = formatter('PlayListID', playItem.playListid, 6)
        n2 = formatter('PlayItemID', playItem.id, 6)
        n3 = formatter('AngleID', '0', 5) # it should always be 0. At least seems so.
        node.extend([n1, n2, n3])
        return node

    def getVideos(self, videos:list[Video]):
        videoNode = self.node.find('Loop_VideoStream')
        for i in videoNode:
            self.clipVideoInfos.append(ClipStreamInfo(i)) 
            for vi in videos:
                if vi.id == i.find('StreamAssetID').text:
                    self.videos.append(vi)
                    break
    def getAudios(self, audios:list[Audio]):
        audioNode = self.node.find('LoopPrimaryAudioStream')
        for i in audioNode: 
            self.clipAudioInfos.append(ClipStreamInfo(i)) 
            for ai in audios:
                if ai.id == i.find('StreamAssetID').text:
                    self.audios.append(ai)
                    break
    def getPGs(self, pgs:list[PG]):
        pgNode = self.node.find('LoopPGStream')
        for i in pgNode: 
            self.clipPGInfos.append(ClipStreamInfo(i)) 
            for si in pgs:
                if si.id == i.find('StreamAssetID').text:
                    self.pgs.append(si)
                    break

    # unused
    def setPlayItem(self, playItem):
        for pl, pi in self.playItems:
            if pi is playItem:
                return
        node = self.refPlayItemInfoFormatter(playItem)
        self.node.find('RefPlayItemInfoList').append(node)
        self.playItems.append([playItem.playListid, playItem])
    def delPlayItem(self, playItem):
        for i, (pl, pi) in enumerate(self.playItems):
            if pi is playItem:
                self.playItems.pop(i)
                break
        for node in self.node.find('RefPlayItemInfoList'):
            if (node.find('PlayListID').text == playItem.playListid 
                and node.find('PlayItemID').text == playItem.id):
                self.node.find('RefPlayItemInfoList').remove(node)
                break

    def popAudio(self, audio:Audio):
        ind = -1
        for i, ai in enumerate(self.audios):
            if ai is audio:
                ind = i
        if ind >= 0:
            self.node.find('LoopPrimaryAudioStream').remove(self.clipAudioInfos[ind].node)
            self.clipAudioInfos.pop(ind)
            self.audios.pop(ind)
            # ref in playItem
            for pl, pi in self.playItems:
                pi.popAudioInf(audio)
    def popPG(self, pg:PG):
        ind = -1
        for i, si in enumerate(self.pgs):
            if si is pg:
                ind = i
        if ind >= 0:
            self.node.find('LoopPGStream').remove(self.clipPGInfos[ind].node)
            self.clipPGInfos.pop(ind)
            self.pgs.pop(ind)
            # ref in playItem
            for pl, pi in self.playItems:
                pi.popPGInf(pg)
    def appendAudio(self, audio:Audio):
        if audio in self.audios:
            return
        else:
            self.audios.append(audio)
            node = self.clipStreamInfoFormatter(audio)
            self.node.find('LoopPrimaryAudioStream').append(node)
            self.clipAudioInfos.append(ClipStreamInfo(node))
            return True
    def appendPG(self, pg:PG):
        if pg in self.pgs:
            return
        else:
            self.pgs.append(pg)
            node = self.clipStreamInfoFormatter(pg)
            self.node.find('LoopPGStream').append(node)
            self.clipPGInfos.append(ClipStreamInfo(node))
            return True

    def beautify(self):
        i = self.node.find('RefPlayItemInfoList')
        if len(i) == 0:
            self.node.remove(i)
        i = self.node.find('Loop_VideoStream')
        if len(i) == 0:
            self.node.remove(i)
        i = self.node.find('LoopPrimaryAudioStream')
        if len(i) == 0:
            self.node.remove(i)
        i = self.node.find('LoopPGStream')
        if len(i) == 0:
            self.node.remove(i)
        count = len(self.node)
        for i, n in enumerate(self.node):
            if i != count - 1:
                n.tail = '\n' + '  ' * 4
            else:
                n.tail = '\n' + '  ' * 3


class PlayItemStreamInf:
    def __init__(self, node:ET.Element):
        self.node = node
        self.streamid = node.find('StreamObjectID').text
    @property
    def PID(self):
        pid = self.node.find('StreamEntry/Type1/RefToStreamPIDofMainClip').text
        return int(pid)
    @PID.setter
    def PID(self, value:int):
        self.node.find('StreamEntry/Type1/RefToStreamPIDofMainClip').text = str(value)

class PlayItem:

    def __init__(self, node:ET.Element):
        self.node = node
        self.id = node.attrib['ID']
        self.playListid = node.find('ParentObjectID')
        self.clip:Optional[Clip] = None
        n = node.find('STN_table_Block/Loop_PrimaryAudioStream')
        if len(n) == 0:
            n.text = '\n' + '  ' * 6
        n = node.find('STN_table_Block/Loop_PG_textSTStream')
        if len(n) == 0:
            n.text = '\n' + '  ' * 6
        n = node.find('STN_table_SS_Block/Loop_PG_textSTStream')
        if len(n) == 0:
            n.text = '\n' + '  ' * 6
        self.playItemAudioInfs:list[PlayItemStreamInf] = []
        self.playItemPGInfs:list[PlayItemStreamInf] = []
        self.pgSSEntries:list[PlayItemStreamInf] = []
        for i in node.find('STN_table_Block/Loop_PrimaryAudioStream'):
            self.playItemAudioInfs.append(PlayItemStreamInf(i))
        for i in node.find('STN_table_Block/Loop_PG_textSTStream'):
            self.playItemPGInfs.append(PlayItemStreamInf(i))
        for i in node.find('STN_table_SS_Block/Loop_PG_textSTStream'):
            self.pgSSEntries.append(PlayItemStreamInf(i))

    @property
    def intime(self):
        return int(self.node.find('IN_time').text)
    @intime.setter
    def intime(self, value:int):
        self.node.find('IN_time').text = str(value)
    @property
    def outtime(self):
        return int(self.node.find('OUT_time').text)
    @outtime.setter
    def outtime(self, value:int):
        self.node.find('OUT_time').text = str(value)
    @property
    def duration(self):
        return self.outtime - self.intime

    @property
    def connection(self):
        return self.node.find('connection_condition').text
    @connection.setter
    def connection(self, value:str):
        self.node.find('connection_condition').text = value

    def playItemStreamInfFormatter(self, asset:Union[Audio, PG], pid:int, text=7, tail=6):
        dic = {
            'Audio': {'StreamObjectType': '4'},
            'PG':    {'StreamObjectType': '5'}
        }
        def formatter(tag, content, tail=7):
            n = ET.Element(tag)
            n.text = content
            n.tail = '\n' + '  ' * tail
            return n
        node = ET.Element('PlayItemStreamInf')
        node.text = '\n' + '  ' * text
        node.tail = '\n' + '  ' * tail
        n1 = formatter('ParentObjectID', self.id, 7)
        n2 = formatter('StreamParentClipID', self.clip.id, 7)
        n3 = formatter('StreamObjectType', dic[asset.type]['StreamObjectType'], 7)
        n4 = formatter('StreamObjectID', asset.id, 7)
        se = formatter('StreamEntry', '\n' + '  ' * 8, 6)
        node.extend([n1, n2, n3, n4, se])
        n5 = formatter('StreamEntryType', '1', 8)
        t1 = formatter('Type1', '\n' + '  ' * 9, 7)
        n7 = formatter('RefToStreamPIDofMainClip', str(pid), 8)
        se.extend([n5, t1])
        t1.append(n7)
        return node
        
    def getClip(self, clips:list[Clip]):
        for c in clips:
            if c.id == self.node.find('clip_info_id_ref').text:
                self.clip = c
                c.playItems.append([self.playListid, self])
                break
    # unused
    def setClip(self, clip:Clip):
        self.node.find('clip_info_id_ref').text = clip.id
        self.clip = clip

    def popAudioInf(self, audio:Audio):
        ind = -1
        for i, audioInf in enumerate(self.playItemAudioInfs):
            if audioInf.streamid == audio.id:
                ind = i
        if ind >= 0:
            self.node.find('STN_table_Block/Loop_PrimaryAudioStream').remove(self.playItemAudioInfs[ind].node)
            self.playItemAudioInfs.pop(ind)
    def popPGInf(self, pg:PG):
        ind = -1
        for i, pgInf in enumerate(self.playItemPGInfs):
            if pgInf.streamid == pg.id:
                ind = i
        if ind >= 0:
            self.node.find('STN_table_Block/Loop_PG_textSTStream').remove(self.playItemPGInfs[ind].node)
            self.playItemPGInfs.pop(ind)
        ind = -1
        for i, pgInf in enumerate(self.pgSSEntries):
            if pgInf.streamid == pg.id:
                ind = i
        if ind >= 0:
            self.node.find('STN_table_SS_Block/Loop_PG_textSTStream').remove(self.pgSSEntries[ind].node)
            self.pgSSEntries.pop(ind)
    def setAudioInf(self, audio:Audio, PID:int):
        pos = 0
        for audioInf in self.playItemAudioInfs:
            if audioInf.streamid == audio.id:
                return
            elif audioInf.PID <= PID:
                pos += 1
        node = self.playItemStreamInfFormatter(audio, PID)
        self.node.find('STN_table_Block/Loop_PrimaryAudioStream').insert(pos, node)
        self.playItemAudioInfs.insert(pos, PlayItemStreamInf(node))
        return True
    def setPGInf(self, pg:PG, PID:int):
        pos1 = 0
        for pgInf in self.playItemPGInfs:
            if pgInf.streamid == pg.id:
                return
            elif pgInf.PID <= PID:
                pos1 += 1
        pos2 = 0
        for pgInf in self.pgSSEntries:
            if pgInf.PID <= PID:
                pos2 += 1
        node1 = self.playItemStreamInfFormatter(pg, PID)
        node2 = deepcopy(node1)
        self.node.find('STN_table_Block/Loop_PG_textSTStream').insert(pos1, node1)
        self.node.find('STN_table_SS_Block/Loop_PG_textSTStream').insert(pos2, node2)
        self.playItemPGInfs.insert(pos1, PlayItemStreamInf(node1))
        self.pgSSEntries.insert(pos2, PlayItemStreamInf(node2))
        return True

    def beautify(self):
        n = self.node.find('STN_table_Block/Loop_PrimaryAudioStream')
        if len(n) == 0:
            n.text = ''
        n = self.node.find('STN_table_Block/Loop_PG_textSTStream')
        if len(n) == 0:
            n.text = ''
        n = self.node.find('STN_table_SS_Block/Loop_PG_textSTStream')
        if len(n) == 0:
            n.text = ''

class PlayList:

    def __init__(self, node:ET.Element):
        self.node = node
        self.id = node.attrib['ID']
        self.name= node.find('Name').text
        self.playItems:list[PlayItem] = []

    def getPlayItems(self, playItems:list[PlayItem]):
        for i in self.node.iter('PlayItem_id_ref'): 
            for pi in playItems:
                if pi.id == i.text:
                    self.playItems.append(pi)
                    break

        
