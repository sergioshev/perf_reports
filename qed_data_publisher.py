# -*- coding: utf-8 -*-
from datetime import datetime
import qed_data_retriever
import urllib, urllib2

class data_publisher:

  def __init__(self, dp, qed_server = 'http://qed.duncllc.com' ):
    self.dp = dp
    self.qed_server = qed_server
    self.brand = None
    if dp : self.test_name = dp.get_file_name()
  
  def __get_brand_id__(self, brand):
    brandr = qed_data_retriever.brand_retriever()
    brandr.set_filter_by_expr('(=name,'+str(brand)+')')
    result = brandr.get_values(columns = ['name','id'])
    if not result : return False
    return result[0]['id']

  def __get_pts_id__(self):
    ptsr = qed_data_retriever.pts_retriever()
    timestamp = self.dp.get_timestamp()
    date, time = timestamp[:10],timestamp[11:]
    timestamp = date+'T'+time+'Z'
    ptsr.set_filter_by_expr('(.(=name,'+self.test_name+')(=start,'+timestamp+'))')
    result = ptsr.get_values(columns = ['id'])
    if not result : return False
    return result[0]['id']

  def __publish_summary__(self, update = False):
    pts_id = self.__get_pts_id__()
    if not update and not pts_id == False: return False
    if update and not pts_id == False:
      self.remove_test(pts_id)
    brand_id = self.__get_brand_id__(self.brand)
    if brand_id == False: return False
    dp = self.dp
    url = self.qed_server+"/perf_test_summaries"
    params = {
      "perf_test_summary[name]" : self.test_name,
      "perf_test_summary[start]" : dp.get_timestamp(),
      "perf_test_summary[throughput]" : dp.get_last('summary','throughput'),
      "perf_test_summary[latency]" : dp.get_last('summary','latency'),
      "perf_test_summary[elapsed]" : dp.get_last('summary','elapsed'),
      "perf_test_summary[min_elapsed_time]" :  dp.get_min('summary','elapsed'),
      "perf_test_summary[max_elapsed_time]" :  dp.get_max('summary','elapsed'),
      "perf_test_summary[error_rate]" : dp.get_last('summary','error_rate'),
      "perf_test_summary[std_elapsed_dev]" : dp.get_last('summary','std_dev'),
      "perf_test_summary[brand_id]" : brand_id
    }
    data = urllib.urlencode(params)
    request = urllib2.Request(url, data)
    try:
      response = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
      print ("%s %s" % (e.code, e.msg))
      return False
    return response.geturl()


  def __publish_detailed__(self, pts_id):
    url = self.qed_server+"/perf_test_details"
    dp = self.dp
    flag = False
    for label in dp.get_labels():
      params = {                         
        "perf_test_detail[pts_id]" : pts_id,
        "perf_test_detail[label]" : label,
        "perf_test_detail[throughput]" : dp.get_last(label,'throughput'),
        "perf_test_detail[latency]" : dp.get_last(label,'latency'),
        "perf_test_detail[elapsed]" : dp.get_last(label,'elapsed'),
        "perf_test_detail[max_elapsed_time]" : dp.get_max(label,'elapsed'),
        "perf_test_detail[min_elapsed_time]" : dp.get_min(label,'elapsed'),
        "perf_test_detail[error_rate]" : dp.get_last(label,'error_rate'),
        "perf_test_detail[std_elapsed_dev]" : dp.get_last(label,'std_dev')
      }
      data = urllib.urlencode(params)
      request = urllib2.Request(url, data)
      try:
        response = urllib2.urlopen(request)
      except urllib2.HTTPError, e:
        flag = True
        print ("%s : %s %s" % (label, e.code, e.msg))
    return not flag

  def setup_test_name(self, test_name):
    self.test_name = test_name

  def setup_brand(self,brand):
    self.brand = brand

  def publish (self, update = False):
    response  = self.__publish_summary__(update)
    if not response:
      print "There were some problem publishing summary report to the QED"
      return False
    # little hack to parse pts_id value
    # "http://qed.duncllc.com/perf_test_summaries/12" 12 is the pts_id
    try:
      pts_id = response.split('/')[-1:][0]
    except IndexError, e:
      print "Can't parse pts_id from URL : "+response
      return False
    if not self.__publish_detailed__(pts_id): return False
    return True

  def __remove__(self,url):
    params = {
      "_method" : 'delete'
    }
    data = urllib.urlencode(params)
    request = urllib2.Request(url, data)
    try:
      response = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
      print ("%s %s" % (e.code, e.msg))

    
  def remove_test(self,pts_id):
    url = self.qed_server+"/perf_test_summaries/"+str(pts_id)
    self.__remove__(url)
    retriever = qed_data_retriever.ptd_retriever()
    retriever.set_filter_by_expr('(=pts-id,'+str(pts_id)+')')
    result = retriever.get_values(columns = ['pts-id','id'])
    if result:
      url = self.qed_server+"/perf_test_details/"
      for row in result:
        self.__remove__(url+str(row['id']))



