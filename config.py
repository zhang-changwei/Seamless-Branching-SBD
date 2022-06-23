from medium import BluRay, UHDBluRay
import json
from typing import Union
import os

class Config:

    def __init__(self):
        if os.path.exists('./config.json'):
            self.fromjson()
        else:
            self.medium = BluRay()
            self.ui = {
                'TrackSort': {'MaxRow': 16},
                'Asset': {'MaxRow': 20},
                'Table': {'CellWidth': 63,
                          'Width': 560,
                          'Height': 170}
            }

    def fromjson(self):
        with open('./config.json') as f:
            conf = json.load(f)
            self.medium:Union[BluRay, UHDBluRay] = conf['medium'] == 'BluRay' and BluRay() or UHDBluRay()
            self.ui = conf['ui']

    def tojson(self):
        conf = {
            'medium': self.medium.type_, 
            'ui': self.ui
        }
        with open('./config.json', 'w') as f:
            json.dump(conf, f, indent=4)

P = Config()