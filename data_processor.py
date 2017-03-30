# -*- coding: utf-8 -*-
import copy
import csv
import datetime
import math
import sys

from operator import itemgetter, attrgetter

# This class is responsable to compute all the data.
# Uses custom_simple_line_chart, to pass correct data
#
# labels : are strings of the http requests
# target : is kind of data to compute (throughput, latency, ...)


# 
# Uses custom_simple_line_chart, to pass correct data
#

class generic_dataset:
  def __init__(self):
    self.data = []
    self.max_avg_value = 0
    self.min_avg_value = 99999999999999
    self.max_value = 0
    self.min_value = 99999999999999
  
  def __max__(self,values):
    value = values[0]
    for i in range(1,len(values)):
      try:
        if float(value) < float(values[i]): value = values[i]
      except ValueError, e:
        if value < values[i]: value = values[i]
    return value

 
  def __my_range__(self,parts,values):
    end = len(values)
    if end < parts: return values
    step = float(end) / parts
    index = 0
    result = []
    while index < end:
      result.append(values[int(index)])
      index += step
    return result

  def append_value(self,avg_value, value):
    try:
      av = float(avg_value)
      v = float(value)
    except ValueError, e:
      av = avg_value
      v = value
    if av > self.max_avg_value: self.max_avg_value = av
    if av < self.min_avg_value: self.min_avg_value = av
    if v > self.max_value: self.max_value = v
    if v < self.min_value: self.min_value = v
    self.data.append(avg_value)

  def get_avg_max(self, parts = None):
    if not parts: return self.max_avg_value
    return self.__max__(self.parts(parts))
  
  def get_avg_min(self): return self.min_avg_value
 
  def get_max(self): return self.max_value
  
  def get_min(self): return self.min_value
 
  def get_last(self): return self.data[len(self.data)-1]

  # is used for calculate new set of values based on different range (0..max_value)
  # used for transform threads dataset to fit in already created range of values.
  def normalize(self, factor, parts = None):
    values = [ value * factor for value in self.data ]
    if parts == None:
      return values
    return self.__my_range__(parts,values)  
 
  def parts(self, parts):
    return self.__my_range__(parts,self.data)

  def get_values(self): return self.data

class data_processor:

  def __init__(self, filename):
    self.labels = {}
    self.detailed_labels = []
    self.data_items = {}
    self.data_items['throughput'] = generic_dataset()
    self.data_items['latency'] = generic_dataset()
    self.data_items['threads'] = generic_dataset()
    self.data_items['minutes'] = generic_dataset()
    self.data_items['std_dev'] = generic_dataset()
    self.data_items['error_rate'] = generic_dataset()
    self.data_items['error_count'] = generic_dataset()
    self.data_items['bytes_sec'] = generic_dataset()
    self.data_items['elapsed'] = generic_dataset()
    self.data_items['samples'] = generic_dataset()
    self.data_tree = {}

    self.file_name = filename
    self.timestamp = '1970-01-01 00:00:00'
    spam_reader = csv.reader(open(self.file_name, 'rb'), delimiter='\t', quotechar='|')
    # Skip labels (first) line
    spam_reader.next()
    # Read the whole thing and put it in a list. 
    # TODO: Improve this!

    # split by labels
    self.labels['summary'] = []
    for row in spam_reader:
      self.labels['summary'].append(row)
      self.__append_by_request__(row)

    # computing the data
    for label,label_rows in self.labels.iteritems():
      self.__compute_data_set__(label,label_rows)

#    for label in self.data_tree:
#      for item in self.get_items(label):
#        print label, item
#        print "MIN_AVG:"+str(self.data_tree[label][item].min_avg_value)
#        print "MAX_AVG:"+str(self.data_tree[label][item].max_avg_value)
#        print "MIN:"+str(self.data_tree[label][item].min_value)
#        print "MAX:"+str(self.data_tree[label][item].max_value)
#        print self.data_tree[label][item].data


  def __append_by_request__(self, row):
    if row[2] not in self.labels:
      self.detailed_labels.append(row[2])
      self.labels[row[2]] = [row]
    else:
      self.labels[row[2]].append(row)

  def __compute_data_set__(self, label, data_set):
    req_date = None
    failure = 'false'
    total_bytes = total_elapsed = total_latency = total_square = total_failure = 0
    samples = first_time = 0
    
    if not label in self.data_tree : self.data_tree[label] = copy.deepcopy(self.data_items)
    for index in range(0,len(data_set)):
      row = data_set[index]
      req_time,elapsed = int(row[0]),int(row[1])
      failure, curr_bytes = row[7], int(row[8])
      latency,threads = int(row[9]),int(row[10])
      total_latency += latency
      total_elapsed += elapsed
      total_bytes += curr_bytes
      total_square += math.pow(int(elapsed), 2)

      if ( failure == 'false' ): total_failure += 1
      samples = index+1
      if index == 0:
        first_time = req_time
        req_date = datetime.datetime.fromtimestamp(float(req_time) / 1000)
        minutes = req_date.strftime("%H:%M:%S")
        self.timestamp = req_date.strftime("%Y-%m-%d %H:%M:%S")

      delta_time = req_time - first_time
      minutes = round(float (delta_time) / 1000 / 60, 1)
      if delta_time == 0: delta_time = 999999999
      throughput = float( samples ) / delta_time * 1000 * 60 # samplers per minute
      avg_latency = float ( total_latency ) / samples # milliseconds
      avg_elapsed = float(total_elapsed) / samples # evarage elapsed
      avg_elapsed_sec = float(avg_elapsed) / 1000 # evarage elapsed per second
      std_dev = round(math.sqrt( ( float(total_square) / samples ) - math.pow(avg_elapsed,2)), 2)
      bytes_per_sec = float(total_bytes) / delta_time * 1000
      failure_percentage = float ( total_failure ) / samples * 100
      self.data_tree[label]['samples'].append_value(samples,samples)
      self.data_tree[label]['throughput'].append_value(throughput,throughput)
      self.data_tree[label]['latency'].append_value(avg_latency,latency)
      self.data_tree[label]['minutes'].append_value(minutes,minutes)
      self.data_tree[label]['threads'].append_value(threads,threads)
      self.data_tree[label]['elapsed'].append_value(avg_elapsed,elapsed)
      self.data_tree[label]['std_dev'].append_value(std_dev,std_dev)
      self.data_tree[label]['error_rate'].append_value(failure_percentage,failure_percentage)
      self.data_tree[label]['error_count'].append_value(total_failure,total_failure)
      self.data_tree[label]['bytes_sec'].append_value(bytes_per_sec,curr_bytes)

  def get_labels(self): return self.detailed_labels

  def get_all_labels(self): return self.data_tree.keys()

  def get_items(self,label): return self.data_tree[label].keys()

  def get_max(self,label,item): return self.data_tree[label][item].get_max()
   
  def get_min(self,label,item): return self.data_tree[label][item].get_min()
 
  def get_avg_max(self,label,item,parts = None): return self.data_tree[label][item].get_avg_max(parts)
   
  def get_avg_min(self,label,item): return self.data_tree[label][item].get_avg_min()
   
  def get_last(self,label,item): return self.data_tree[label][item].get_last()
  
  def get_values(self,label,item): return self.data_tree[label][item].data

  def normalize_data(self,label, item, new_max, parts = None):
    return self.data_tree[label][item].normalize(new_max,parts)
    
  # is like range function but supports float steps
  def parts(self, label, item, step): return self.data_tree[label][item].parts(step)

  def get_file_name(self) : return self.file_name
  
  def get_timestamp(self) : return self.timestamp


