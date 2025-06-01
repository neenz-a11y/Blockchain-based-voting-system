from datetime import time
import hashlib
import json
from datetime import datetime

class blockchain():
    def __init__(self,gen=False):
        if gen:
            self.blocks = []
        else:
            with open("blockChainDatabase.json",'r') as f:
                self.blocks = json.load(f)
        self.__secret = ''
        self.__difficulty = 4 
        i = 0
        while True:
            _hash = hashlib.sha256(str( str(i)).encode('utf-8')).hexdigest()
            if(_hash[:self.__difficulty] == '0'*self.__difficulty):
                self.__secret = _hash
                break
            i+=1
    def create_block(self, voterid= "not mentioned", party= "not mentioned" , date= "not mentioned", tim="not mentioned"):
        now = datetime.now()
        #print(now.date())
        block = {
            'index': len(self.blocks), 
            "voterid": voterid, 
            "party": party, 
            "date": str(now.date()), 
            "time": str(now.time()),
            'timestamp': str(time())
        }
        if(block['index'] == 0):
            block['previous_hash'] = self.__secret # for genesis block
        else:
            block['previous_hash'] = self.blocks[-1]['hash']
        i = 0
        while True:
            block['nonce'] = i
            _hash = hashlib.sha256(str(block).encode('utf-8')).hexdigest()
            if(_hash[:self.__difficulty] == '0'*self.__difficulty):
                block['hash'] = _hash
                break
            i+=1
        # with open("blockChainDatabase.json",'r') as f:
        #     self.blocks = json.load(f)
        self.blocks.append(block)
        with open("blockChainDatabase.json",'w') as f:
            json.dump(self.blocks,f)
        
    def validate_blockchain(self):
        valid = True
        n = len(self.blocks)-1
        i = 0
        while(i<n):
            if(self.blocks[i]['hash'] != self.blocks[i+1]['previous_hash']):
                valid = False
                break
            i+=1
        if valid: return True
        else: return False
    def show_blockchain(self):
        with open("blockChainDatabase.json",'r') as f:
            self.blocks = json.load(f)
        return self.blocks
    def check_blockchain(self):
        # with open("blockChainDatabase.json",'r') as f:
        #     self.blocks = json.load(f)
        return self.blocks

