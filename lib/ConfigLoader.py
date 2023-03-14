import json
class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = json.load(open(config_file))

    __call__ = lambda self,key: self.config[key]
