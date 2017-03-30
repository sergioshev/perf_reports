# -*- coding: utf-8 -*-
import copy
import csv
import datetime
import os
import re
import sys

from data_processor import data_processor
from data_processor import generic_dataset
from operator import itemgetter, attrgetter
from qed_data_retriever import pts_retriever
from qed_data_retriever import ptd_retriever
from lib.pygooglechart.pygooglechart import Axis
from lib.pygooglechart.pygooglechart import Chart
from lib.pygooglechart.pygooglechart import LabelAxis
from lib.pygooglechart.pygooglechart import PieChart3D
from lib.pygooglechart.pygooglechart import RangeAxis
from lib.pygooglechart.pygooglechart import SimpleLineChart
# This one is used for reading teh properties file with the threshold data
from ConfigParser import ConfigParser

#
# class to compound customized line charts
#
class custom_simple_line_chart(SimpleLineChart):

  def __init__(self, width, height, my_y_range, my_y2_range ,title=None, x_axis_parts = 1, y_axis_parts = 1 ):
    SimpleLineChart.__init__(self, width, height, title, y_range=[0,my_y_range])
    self.my_y_range = my_y_range
    self.my_y2_range = my_y2_range
    self.x_axis_parts = x_axis_parts
    self.y_axis_parts = y_axis_parts
    self.axis_ids = {}
    self.legends = []
    self.y_axis_step = float (self.my_y_range) / self.y_axis_parts
    self.y2_axis_step = float (self.my_y2_range) / self.y_axis_parts


  def set_up_chart(self, y_axis_label, r_axis_label, b_axis_label, palette, bottom_labels):
    self.axis_ids['y_axis_range'] = self.set_axis_range(Axis.LEFT, 0, self.my_y_range, self.y_axis_step)
    self.axis_ids['y_axis_label'] = self.set_axis_labels(Axis.LEFT, [y_axis_label] )
    self.set_axis_positions(self.axis_ids['y_axis_label'],[50])
    self.axis_ids['bottom_labels'] = self.set_axis_labels(Axis.BOTTOM, bottom_labels) # axis id 4
    self.axis_ids['bottom_label'] = self.set_axis_labels(Axis.BOTTOM, [b_axis_label])
    self.set_axis_positions(self.axis_ids['bottom_label'],[50])

    self.axis_ids['y_threads_range'] = self.set_axis_range(Axis.RIGHT, 0, self.my_y2_range, self.y2_axis_step)
    self.axis_ids['r_axis_label'] = self.set_axis_labels(Axis.RIGHT, [r_axis_label])
    self.set_axis_positions(self.axis_ids['r_axis_label'], [50])
    self.set_grid(self.x_axis_parts , float ( 100 ) / self.my_y_range * self.y_axis_step , 1 , 2 )
    self.set_legend(self.legends)
    self.set_colours(palette)

  def add_data_set(self,data,data_legend):
    self.add_data(data)
    self.legends.append(data_legend)
  


class historic_trend_line_chart(custom_simple_line_chart):

  def __init__(self, width, height, my_y_range ,title=None, x_axis_parts = 1, y_axis_parts = 1):
    custom_simple_line_chart.__init__(self, width, height, my_y_range, my_y_range, title, x_axis_parts, y_axis_parts)

  def set_up_chart(self, y_axis_label, b_axis_label, palette, bottom_labels):
    custom_simple_line_chart.set_up_chart(self, y_axis_label, y_axis_label, b_axis_label,palette, bottom_labels)


class charts_commons:
  # Charts common data
  CHART_POINTS = 200
  CHART_HEIGHT = 300
  CHART_WIDTH  = 525
  X_AXIS_PARTS = 10
  Y_AXIS_PARTS = 15

  PIE_CHART_HEIGHT = 250
  PIE_CHART_WIDTH  = 700


  GREEN = '00FF00'
  BLUE = '0000FF'
  BLACK = '000000'

  COL1 = "CD5C5C"
  COL2 = "8B0000"
  COL3 = "FFB6C1"
  COL4 = "FF1493"
  COL5 = "FF4500"
  COL6 = "FF8C00"
  COL7 = "FFFF00"
  COL8 = "BDB76B"
  COL9 = "DDA0DD"
  COL10 = "8A2BE2"
  COL11 = "800080"
  COL12 = "4B0082"
  COL13 = "483D8B"
  COL14 = "ADFF2F"
  COL15 = "32CD32"
  COL16 = "90EE90"
  COL17 = "00FF7F"
  COL18 = "008B8B"
  COL19 = "00FFFF"
  COL20 = "4682B4"
  COL21 = "191970"
  COL22 = "A52A2A"
  COL23 = "808080"
  COL24 = "2F4F4F"


  INC_FACTOR = 1.2

  PALETTE = [BLUE,BLACK,COL1,COL2,COL3,
             COL4,COL5,COL6,COL7,COL8,COL9,
             COL10,COL11,COL12,COL13,COL14,
             COL15,COL16,COL17,COL18,COL19,
             COL20,COL21,COL22,COL23,COL24]

  def __init__(self):

    self.chart_item_labels = {'throughput' : 'tpm',
                              'latency': 'ms',
                              'elapsed' : 'ms',
                              'threads' : '#threads',
                              'minutes' : 'mins'}

    self.url = {'url' : '',
                'url_bits' : {}}

    self.data_items = {'throughput' : copy.deepcopy(self.url),
                       'latency' : copy.deepcopy(self.url),
                       'threads' : copy.deepcopy(self.url),
                       'minutes' : copy.deepcopy(self.url),
                       'elapsed' : copy.deepcopy(self.url)}

    self.urls = {'summary' : copy.deepcopy(self.data_items),
                 'detailed' : copy.deepcopy(self.data_items)}


  def __make_hash__(self, array):
    url = '&'.join(array)
    array = url.split('&')
    result = {}
    for item in array:
      m = re.search('^([^=]+)=(.*)$', item)
      value = m.group(2)
      # TODO: HARCODED improve this
      value = value.replace("%7c", "|")
      value = value.replace("%7C", "|")
      value = value.replace("%3A", ":")
      value = value.replace("%23", "#")
      # END TODO
      result[m.group(1)] = value
    return result

  # used for reserve upper area based in incremantal factor INC_FACTOR (120%)
  def __normalize_max__(self,max_value):
    delta = 0
    if round(float(max_value) * self.INC_FACTOR) < max_value: delta = 1
    return round(max_value * self.INC_FACTOR) + delta


  def get_url(self, label, item):
    return self.urls[label][item]['url']

  def get_url_array(self, label, item):
    return self.urls[label][item]['url_bits']



class historic_trend_charts(charts_commons):

  def __init__(self):

    charts_commons.__init__(self)
    self.ptsr = pts_retriever()
    self.ptdr = ptd_retriever()
    self.summary_data = None
    self.detailed_data = {}
    self.test_type = ''
    self.from_date = None
    self.to_date = None
    self.labels = []
    #self.mapings = {}
    # Create an object to read the properties file with the threshold information
    self.thresholds = ConfigParser()
    self.thresholds.read("threshold_info.properties")


  def __get_test_data__(self, test, columns = ['latency']):
    from_date, to_date = self.from_date,self.to_date
    if from_date > to_date: # inverted
      from_date, to_date = self.to_date, self.from_date # swap if inverted
    filter_expr = '(=name,'+str(test)+')'
    if from_date and to_date:
      from_date += 'T00:00:00Z'
      to_date += 'T23:59:59Z'
      from_flt_expr = '(+(=start,'+from_date+')(>start,'+from_date+'))' # start >= from_date
      to_flt_expr = '(+(=start,'+to_date+')(<start,'+to_date+'))' # start <= to_date
      filter_expr = '(.'+filter_expr+from_flt_expr+to_flt_expr+')'
    self.ptsr.set_filter_by_expr(filter_expr)
    if not 'id' in columns: columns += ['id']
    if not 'start' in columns: columns += ['start']
    data = self.ptsr.get_values(columns, sort_by = 'start')
    if not data or len(data)<2 : return None
    self.summary_data = {}
    for column in columns:
      self.summary_data[column] = generic_dataset()
    for row in data:
      for column in columns:
        self.summary_data[column].append_value(row[column],0)
    return True


  def __get_detailed_test_data__(self, columns = ['latency'], labels = []):
    if not self.summary_data: return None
    labels_flt = ''
    if labels:
      for label in labels:
        labels_flt += '(%label,'+label+')'
      if labels_flt and len(labels)>1 : labels_flt = '(+'+labels_flt+')'
    for pts_id in self.summary_data['id'].get_values():
      ptd_flt = '(%pts-id,'+pts_id+')'
      if labels_flt: ptd_flt = '(.'+ptd_flt+labels_flt+')'
      self.ptdr.set_filter_by_expr(ptd_flt)
      data = self.ptdr.get_values(columns + ['label'])
      for row in data:
        label = row['label']
        if not label in self.labels:
          self.detailed_data[label] = {}
          self.labels.append(label)
        for column in columns: 
          if not column in self.detailed_data[label].keys():
            self.detailed_data[label][column] = generic_dataset()
          self.detailed_data[label][column].append_value(row[column],0)
    return True


  def __setup_summary_line_chart__(self, item , download = False, max_th = None, min_th = None):
    palette = []
    data_sets = {}
    data_sets['Summary'] = self.summary_data[item]
    for label in self.labels:
      data_sets[label] = self.detailed_data[label][item]
    max_y_range = 1
    labels = self.labels
    if len(self.detailed_data)>1: labels.insert(0, 'Summary')
    for label in labels:
      curr_y_range = float(data_sets[label].get_avg_max(self.CHART_POINTS))
      if curr_y_range > max_y_range : max_y_range = curr_y_range
    max_y_range = self.__normalize_max__(max_y_range)
    chart = historic_trend_line_chart(self.CHART_WIDTH, self.CHART_HEIGHT,
                                  max_y_range,
                                  x_axis_parts = self.X_AXIS_PARTS,
                                  y_axis_parts = self.Y_AXIS_PARTS)
    if max_th and min_th:
      chart.add_data_set([max_th,max_th],'Max threshold')
      chart.add_data_set([min_th,min_th],'Min threshold')
      for i in 0,1:
        chart.set_line_style(i,2,7,2)
        palette.append(self.BLACK)
    index = 0
    if len(labels)>len(self.PALETTE):
      self.urls['summary'][item]['url'] = ''
      self.urls['summary'][item]['url_bits'] = {}
      return
    for label in labels:
      chart.add_data_set([ float(value) for value in data_sets[label].parts(self.CHART_POINTS)] ,label)
      palette.append(self.PALETTE[index])
      index += 1
    dates = [ value[:10] for value in self.summary_data['start'].parts(float((self.X_AXIS_PARTS + 1 )) / 2)]
    chart.set_up_chart(self.chart_item_labels[item],
                       'dates', palette, dates)
    chart.set_legend_position('b|l')
    self.urls['summary'][item]['url'] = chart.get_url()
    self.urls['summary'][item]['url_bits'] = self.__make_hash__(chart.get_url_bits())
    if download : chart.download('images/' + self.test_type + '_' + item + '_graph.png','POST')

  # from date format: YYYY-MM-DD
  def set_from_date(self,from_date): self.from_date = from_date
  
  def set_to_date(self,to_date): self.to_date = to_date
 

  def compute_urls(self, brand = None, test_type = None, item = 'latency', labels = [], download_charts = False):
    if (brand == None or test_type == None):
    	thr_min_th = thr_max_th = lat_min_th = lat_max_th = 0
    else:
      try:
        thr_min_th = int(self.thresholds.get(brand, test_type + "_throughput_min"))
        thr_max_th = int(self.thresholds.get(brand, test_type + "_throughput_max"))
        lat_min_th = float(self.thresholds.get(brand, test_type + "_latency_min"))
        lat_max_th = float(self.thresholds.get(brand, test_type + "_latency_max"))
      except NameError:
        thr_min_th = thr_max_th = lat_min_th = lat_max_th = None
    self.test_type = brand + '_' + test_type
    self.labels = []
    if self.__get_test_data__(self.test_type,[item]) and self.__get_detailed_test_data__([item],labels):
      self.__setup_summary_line_chart__(item, download = download_charts, max_th = lat_max_th, min_th = lat_min_th)
    

  def get_chart_height(self, target):
    return self.CHART_HEIGHT


  def get_chart_width(self, target):
    return self.CHART_WIDTH


#
# labels : are strings of the http requests
# item : is kind of data to compute (throughput, latency, ...)

# 
# Uses custom_simple_line_chart, to pass correct data
#

class orbitz_google_charts_wrapper(charts_commons):

  def __init__(self, data_proc):

    charts_commons.__init__(self)

    self.dp = data_proc
    # Create an object to read the properties file with the threshold information
    self.thresholds = ConfigParser()
    self.thresholds.read("report_creation/threshold_info.properties")

  def __setup_detailed_pie_chart__(self, item, labels = None ,download = False):
    chart = PieChart3D(self.PIE_CHART_WIDTH,self.PIE_CHART_HEIGHT)
    pie_data = []
    pie_labels =[]
    if not labels: labels = self.dp.get_labels()
    for label in labels:
      pie_data.append(self.dp.get_last(label,item))
      pie_labels.append(label)
    chart.add_data(pie_data)
    chart.set_pie_labels([str(round(value,3))+self.chart_item_labels[item] for value in pie_data])
    chart.set_legend(pie_labels)
    chart.set_colours(self.PALETTE)
    self.urls['detailed'][item]['url'] = chart.get_url()
    self.urls['detailed'][item]['url_bits'] = self.__make_hash__(chart.get_url_bits())
    if download : chart.download(self.dp.get_file_name() + '.pie' + '.detailed.' + item + '.png')


  # used for compound detailed line chart
  def __setup_detailed_line_chart__(self, item, labels = None, download = False):
    max_labels_value = 0
    if not labels: labels = self.dp.get_labels()
    for label in labels: # calculating max value among all labels
      label_max = self.dp.get_avg_max(label,item,self.CHART_POINTS)
      if max_labels_value < label_max:
        max_labels_value = label_max
    max_y_range = self.__normalize_max__(max_labels_value) # reserve 20% for upper area
    max_y2_range = self.__normalize_max__(self.dp.get_avg_max('summary','threads'))
    if max_y_range == 0 : max_y_range = 1
    if max_y2_range == 0 : max_y2_range = 1
    factor = float(max_y_range) / max_y2_range
    chart = custom_simple_line_chart(self.CHART_WIDTH,
                                     self.CHART_HEIGHT,
                                     max_y_range, max_y2_range, 
                                     x_axis_parts = self.X_AXIS_PARTS,
                                     y_axis_parts = self.Y_AXIS_PARTS)
    index = 0
    palette = []
    if len(labels) > len(self.PALETTE):
      self.urls['detailed'][item]['url'] = ''
      self.urls['detailed'][item]['url_bits'] = {}
      return
    for label in labels:
      chart.add_data_set(self.dp.parts(label,item,self.CHART_POINTS),label)
      palette.append(self.PALETTE[index])
      index += 1
    normalized_threads = self.dp.normalize_data('summary','threads',factor,self.CHART_POINTS)
    chart.add_data_set(normalized_threads,'#Threads')
    palette.append(self.GREEN)
    chart.set_up_chart(self.chart_item_labels[item],
                       self.chart_item_labels['threads'],
                       self.chart_item_labels['minutes'],
                       palette,
                       self.dp.parts('summary','minutes',self.X_AXIS_PARTS + 1))
    chart.set_legend_position('b|l')
    self.urls['detailed'][item]['url'] = chart.get_url()
    self.urls['detailed'][item]['url_bits'] = self.__make_hash__(chart.get_url_bits())
    if download :chart.download(self.dp.get_file_name() + '.line' + '.detailed.' +item + '.png','POST')

  # used fo create summary line chart
  def __setup_summary_line_chart__(self, item, download = False, max_th = None, min_th = None):
    palette = []
    max_y_range = self.__normalize_max__(self.dp.get_avg_max('summary',item,self.CHART_POINTS)) 
    # reserve 20% for upper area
    max_y2_range = self.__normalize_max__(self.dp.get_avg_max('summary','threads'))
    if max_y_range == 0 : max_y_range = 1
    if max_y2_range == 0: max_y2_range = 1
    factor = float(max_y_range) / max_y2_range
    chart = custom_simple_line_chart(self.CHART_WIDTH, self.CHART_HEIGHT,
                                  max_y_range, max_y2_range,
                                  x_axis_parts = self.X_AXIS_PARTS,
                                  y_axis_parts = self.Y_AXIS_PARTS)
    if max_th and min_th:
      chart.add_data_set([max_th,max_th],'Max threshold')
      chart.add_data_set([min_th,min_th],'Min threshold')
      for i in 0,1:
        chart.set_line_style(i,2,7,2)
        palette.append(self.BLACK)
    chart.add_data_set(self.dp.parts('summary',item,self.CHART_POINTS),'Summary')
    palette.append(self.PALETTE[0])
    normalized_threads = self.dp.normalize_data('summary','threads',factor,self.CHART_POINTS)
    chart.add_data_set(normalized_threads,'#Threads')
    palette.append(self.GREEN)
    chart.set_up_chart(self.chart_item_labels[item],
                       self.chart_item_labels['threads'],
                       self.chart_item_labels['minutes'],
                       palette,
                       self.dp.parts('summary','minutes',self.X_AXIS_PARTS + 1)) 
    chart.set_legend_position('b|l')
    self.urls['summary'][item]['url'] = chart.get_url()
    self.urls['summary'][item]['url_bits'] = self.__make_hash__(chart.get_url_bits())
    if download : chart.download(self.dp.get_file_name() + '.summary.' + item + '.png','POST')
   
  def __matched_labels__(self, labels):
    matched_labels = {}
    matched = {}
    index = 0
    for label in self.dp.get_labels():
      for searched_label in labels:
        if label.lower().find(searched_label.lower()) > -1:
          if not matched.get(label):
            matched[label] = True
            matched_labels[index] = label
            index += 1
    if not len(matched_labels): return None
    result = []
    for index in sorted(matched_labels.keys()): result.append(matched_labels[index])
    return result
    
    
  def compute_urls(self, brand=None, test_type=None, opt_labels=[], download_charts=False):
    if (brand == None or test_type == None):
	thr_min_th = thr_max_th = lat_min_th = lat_max_th = 0
    else:
	thr_min_th = int(self.thresholds.get(brand, test_type + "_throughput_min"))
	thr_max_th = int(self.thresholds.get(brand, test_type + "_throughput_max"))
	lat_min_th = float(self.thresholds.get(brand, test_type + "_latency_min"))
	lat_max_th = float(self.thresholds.get(brand, test_type + "_latency_max"))
    opt_labels = self.__matched_labels__(opt_labels)
    self.__setup_summary_line_chart__('throughput', download = download_charts , max_th =  thr_max_th, min_th = thr_min_th)
    self.__setup_summary_line_chart__('latency', download =  download_charts, max_th = lat_max_th, min_th = lat_min_th)
    self.__setup_detailed_line_chart__('throughput', download = download_charts, labels = opt_labels )
    self.__setup_detailed_line_chart__('latency', download = download_charts, labels = opt_labels )
    self.__setup_detailed_pie_chart__('elapsed', download = download_charts, labels = opt_labels )

	
  def get_chart_height(self, target):
    if target == 'elapsed':
      return self.PIE_CHART_HEIGHT
    return self.CHART_HEIGHT

  def get_chart_width(self, target):
    if target == 'elapsed':
      return self.PIE_CHART_WIDTH
    return self.CHART_WIDTH
