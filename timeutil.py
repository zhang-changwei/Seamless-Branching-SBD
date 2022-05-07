from math import floor

def frame2Ms(frame, fps):
    if fps==23.976: fps = 24000/1001
    elif fps==29.97: fps = 30000/1001
    return frame*1000/fps
def ms2Frame(ms, fps):
    if fps==23.976: fps = 24000/1001
    elif fps==29.97: fps = 30000/1001
    return ms/(1000/fps)

def frame2PTS(frame, fps, unit=1):
    '''i don't know unit time of PG.'''
    audioPTS = frame2Ms(frame, fps)*90
    audioframe = floor(audioPTS / unit) # unit always = 1?
    return audioframe * unit

def pts2Frame(pts, fps):
    '''only for validation, pretty useless'''
    frame = ms2Frame(pts/90, fps)
    return round(frame)