import filters
from datetime import datetime
from lib.elementtree import ElementTree
from operator import itemgetter
import urllib, urllib2

class qed_retriever:

  #def __init__(self,table = '', qed_server = 'http://qed.duncllc.com' ):
  def __init__(self,table = '', qed_server = 'qed.duncllc.com' ):
    self.qed_server = qed_server
    self.url = self.qed_server+'/'+table
    self.row_tag = ''
    self.my_filter = None
    self.columns = []
    self.table = table
  
  def __get_element__(self):
    url = urllib.urlopen(self.url)
    try:
      content = ''.join(url.read())
    except urllib2.HTTPError, e:
      print ("%s %s" % (e.code, e.msg))
      return None
    element = ElementTree.fromstring(content)
    return element

  def __generate_tuples__(self,rows,column):
    index = 0
    tuples = []
    for row in rows:
      try:
        value = float(row[column])
      except ValueError, e:
        value = row[column]
      tuples.append((value,index))
      index += 1
    return tuples
    

  def set_filter(self, the_filter):
    if isinstance(the_filter,filters.abstract_filter):
      self.my_filter = the_filter

  def set_filter_by_expr(self, expr):
    fp = filters.filter_parser()
    self.my_filter = fp.parse(expr)

  def select_sql(self):
    if self.my_filter: where = 'where '+self.my_filter.sql()
    return 'select '+','.join(self.columns)+' from '+self.table+' '+where+';'
    

  def get_values(self, columns = [], sort_by = None):
    if not columns: columns = self.columns
    element = self.__get_element__()
    if not element: return []
    childs = element.findall(self.row_tag)
    if not childs: return []
    rows = []
    for child in childs:
      values_hash = {}
      eval_hash = {}
      for column in self.columns:
        if column in columns:
          values_hash[column] = child.findtext(column) 
        eval_hash[column] = child.findtext(column)
      if self.my_filter:
        if self.my_filter.eval(eval_hash):
          rows.append(values_hash)
      else:
        rows.append(values_hash)
    if sort_by in columns:
      sorted_by = []
      for column, index in sorted(self.__generate_tuples__(rows,sort_by), key=itemgetter(0)):
        sorted_by.append(rows[index])
      return sorted_by
    return rows
  
  def get_columns(self): return self.columns
    
    
class brand_retriever(qed_retriever):
  
  def __init__(self):
    qed_retriever.__init__(self,table = 'brands.xml')
    self.row_tag = 'brand'
    self.columns = ['id','name']

class pts_retriever(qed_retriever):
  
  def __init__(self):
    qed_retriever.__init__(self,table = 'perf_test_summaries.xml')
    self.row_tag = 'perf-test-summary'
    self.columns = ['brand-id','elapsed','error-rate','id',
               'latency','max-elapsed-time','min-elapsed-time',
               'name','start','std-elapsed-dev','throughput']

class ptd_retriever(qed_retriever):
  
  def __init__(self):
    qed_retriever.__init__(self,table = 'perf_test_details.xml')
    self.row_tag = 'perf-test-detail'
    self.columns = ['elapsed','error-rate','id','label','latency',
                    'max-elapsed-time','min-elapsed-time','pts-id',
                    'std-elapsed-dev','throughput']


