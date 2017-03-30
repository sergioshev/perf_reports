import csv
import re
from lib.elementtree import ElementTree as element_tree

class sorted_windowed_buffer:
  def __init__(self, values = [], lenght = 200):
    self.values = values
    self.lenght = lenght
    self.full = False


  def __binary_search_index__(self, value, start, end):
    if start >= end : return start
    middle =  start + (end - start ) / 2
    if value == self.values[middle]: return middle
    if value < self.values[middle]: 
      return self.__binary_search_index__(value, start, middle-1)
    else:
      return self.__binary_search_index__(value, middle+1, end)


  def insert(self, value):
    index = self.__binary_search_index__(value, 0, len(self.values)-1)
    if len(self.values) > 0 and self.values[index] == value: return
    if len(self.values) > 0 and self.values[index] < value: index+= 1
    p1 = self.values[0:index]
    p2 = self.values[index:]
    self.values = []
    self.values.extend(p1)
    self.values.append(value)
    self.values.extend(p2)


  def is_full(self):
    return len(self.values) > self.lenght


  def pop_fallen(self):
    if not self.is_full(): return []
    last_fallen = len(self.values) - self.lenght
    fallen = self.values[0:last_fallen]
    within = self.values[last_fallen:]
    self.values = []
    self.values.extend(within)
    return fallen


class jtl_parser:

  def __init__(self,filename):
    self.filename = filename
    self.csv_filename = self.filename[:-4]+'.csv'
  
  def get_jtl_filename(self): return self.filename
  
  def get_csv_filename(self): return self.csv_filename
    

  def generate_csv(self):
    jtl = self.filename
    spamWriter = csv.writer(open(self.csv_filename, 'wb'), delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamWriter.writerow(['timeStamp', 'elapsed', 'label', 'responseCode', 'responseMessage', 'threadName', 'dataType', 'success', 'bytes', 'latency', '#thread'])
    
    my_hash = {}
    hash_keys = sorted_windowed_buffer(lenght = 1000)
    
    context = element_tree.iterparse(jtl)
    context = iter(context)
    event, root = context.next()
    
    for event, elem in element_tree.iterparse(jtl):
      if event == "end" and elem.tag == "httpSample":
        attrs = elem.attrib
        if re.search('http', attrs["lb"]):
          root.clear()
          continue   
        timestamp = int(attrs["ts"])+int(attrs["t"])
        hash_value = {}
        hash_value['timestamp'] = str(timestamp)
        hash_value['elapsed'] = attrs["t"]
        hash_value['latency'] = attrs["lt"]
        hash_value['success'] = attrs["s"]
        hash_value['response_code'] = attrs["rc"]
        hash_value['response_msg'] = attrs["rm"]
        hash_value['request_thread_group'] = attrs["tn"]
        hash_value['label'] = attrs["lb"]
        hash_value['data_type'] = attrs["dt"]
        hash_value['bytes'] = attrs["by"]
        hash_value['active_threads'] = attrs["ng"]
        try:
          my_hash[timestamp].append(hash_value)
        except KeyError:
          my_hash[timestamp]=[]
          my_hash[timestamp].append(hash_value)
        hash_keys.insert(timestamp)
        root.clear()
        if hash_keys.is_full():
          fallen_keys = hash_keys.pop_fallen()
          for key in fallen_keys:
            for values in my_hash[key]:
              spamWriter.writerow([values['timestamp'],
                                   values['elapsed'],
                                   values['label'], 
                                   values['response_code'],
                                   values['response_msg'],
                                   values['request_thread_group'],
                                   values['data_type'],
                                   values['success'],
                                   values['bytes'],
                                   values['latency'],
                                   values['active_threads']])
            my_hash.pop(key) 
    for key in hash_keys.values:
      for values in my_hash[key]:
        spamWriter.writerow([values['timestamp'],
                             values['elapsed'],
                             values['label'],
                             values['response_code'],
                             values['response_msg'],
                             values['request_thread_group'],
                             values['data_type'],
                             values['success'],
                             values['bytes'],
                             values['latency'],
                             values['active_threads']])
      my_hash.pop(key)
