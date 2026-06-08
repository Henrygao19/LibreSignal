"""
All your implementation code for the bank system simulation goes here.
"""
from collections import defaultdict 
import copy
import bisect
class Record:
    def __init__(self):
        self.field = defaultdict(str)
        self.timestamp = {} 
        # self.order = [] # history; turned out to be useless
        self.ttl = {}
        self.ttl_delta = {}
    

    def check_expiry(self, timestamp):
        if timestamp is None: return
        to_delete = []
        for field in self.field.keys():
            if self.ttl.get(field, timestamp + 1)  <= timestamp:
                to_delete.append(field)
        
        for field in to_delete:
            # self.order.append((timestamp, "expired", field, self.field[field]))
            self.ttl.pop(field)
            self.timestamp.pop(field)
            self.field.pop(field)
                
    def set(self, field, value, timestamp= None, ttl= None):
        self.check_expiry(timestamp)
        self.field[field] = value
        if timestamp:
            self.timestamp[field] = timestamp
            # self.order.append((timestamp, "set", field, value, ttl))
        if ttl:
            self.ttl[field] = timestamp + ttl
        elif field in self.ttl:
            self.ttl.pop(field)
        return ""
    
    def get(self, field, timestamp= None):
        self.check_expiry(timestamp)
        return self.field.get(field, "")
    
    def delete(self, field, timestamp= None):
        self.check_expiry(timestamp)
        if field in self.field:
            self.field.pop(field)
            return "true"
        return "false"

    # def scan(self):
    #     pairs = sorted([f'{x}({y})' for x,y in self.field.items()])
    #     return ", ".join(pairs)

    def scan(self, timestamp=None):
        self.check_expiry(timestamp)
        pairs = []
        for x,y in self.field.items():
            pairs.append(f'{x}({y})')
        pairs.sort()
        return ", ".join(pairs)
        
    def prefix(self, pre, timestamp= None):
        self.check_expiry(timestamp)
        filtered = []
        l = len(pre)
        for x,y in self.field.items():
            if len(x) < l: continue
            flag = True
            for i in range(l):
                if pre[i] != x[i]: 
                    flag = False
                    break
            if flag: filtered.append(f'{x}({y})')
        filtered.sort()
        return ", ".join(filtered)
    
class InMemoryDatabase:
    def __init__(self):
        self.record = defaultdict(Record)
        self.backups = []
    
    # ========== Level 1 Operations ==========
    def set(self,key, field, value):
        return self.record[key].set(field, value)
    
    def get(self,key, field):
        return self.record[key].get(field)

    def delete(self,key, field):
        return self.record[key].delete(field)
    
    # ========== Level 2 Operations ==========
    def scan(self, key):
        return self.record[key].scan()

    def scan_by_prefix(self, key, prefix):
        return self.record[key].prefix(prefix)

    # ========== Level 3 Operations ==========
    def set_at(self, key, field, value, timestamp):
        return self.record[key].set(field, value,timestamp=int(timestamp))

    def set_at_with_ttl(self, key, field, value, timestamp, ttl):
        return self.record[key].set(field, value,timestamp=int(timestamp), ttl = int(ttl))

    def delete_at(self, key, field, timestamp):
        return self.record[key].delete(field,timestamp=int(timestamp))

    def get_at(self, key, field, timestamp):
        return self.record[key].get(field,timestamp=int(timestamp))

    def scan_at(self, key, timestamp):
        return self.record[key].scan(timestamp=int(timestamp))

    def scan_by_prefix_at(self, key, prefix, timestamp):
        return self.record[key].prefix(prefix, timestamp=int(timestamp))

    # ========== Level 4 Operations ==========
    def backup(self, timestamp):
        for f in self.record:
            self.record[f].check_expiry(timestamp)
            break

        self.backups.append((timestamp, copy.deepcopy(self.record)))
        count = 0
        for f in self.record:
            if len(self.record[f].field) > 0: count += 1
        return str(count)

    def restore(self, timestamp, timestampToRestore):
        idx = bisect.bisect(self.backups, (timestampToRestore,))
        if idx < len(self.backups) and self.backups[idx][0] == timestampToRestore or idx == 0:
            restore_idx = idx
        else:
            restore_idx = idx - 1

        backup_ts, backup_data = self.backups[restore_idx]
        self.record = copy.deepcopy(backup_data)

        # Fix TTL
        for key in self.record:
            rec = self.record[key]
            new_ttl = {}
            for field, expiry in rec.ttl.items():
                remaining = expiry - backup_ts  
                new_ttl[field] = int(timestamp) + remaining  
            rec.ttl = new_ttl

        for f in self.record:
            self.record[f].check_expiry(int(timestamp))
            break

        return ""