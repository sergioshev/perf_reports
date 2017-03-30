
import re

class filter_exception(Exception):
  pass

class AbstractClassException(filter_exception):
  pass

class abstract_filter(object):

  def __init__(self):
    if type(self) == abstract_filter:
      raise AbstractClassException('This is an abstract class')
  
  def eval(self, the_hash):
    raise AbstractClassException('This is an abstract class')


class comp_filter(abstract_filter):

  def __is_num__(self,value):
    try:
      float(value)
    except ValueError, e:
      return False
    return True

  def __init__(self, column = None, value = None):
    if type(self) == comp_filter:
      raise AbstractClassException('This is an abstract class')
    self.column = column
    self.value = value

  def set_operands(self, op1, op2):
    self.column = op1
    self.value = op2
  
  def set_column(self, column):
    self.column = column
  
  def set_value(self, value):
    self.value = value
  

class gt_filter(comp_filter):
  
  def eval(self, the_hash):
    if not self.column or not self.value : return False
    if not self.column in the_hash: return False
    try:
      if self.__is_num__(the_hash[self.column]) and self.__is_num__(self.value):
        result =  float(the_hash[self.column]) > float(self.value)
      else:
        result =  the_hash[self.column] > self.value
    except IndexError, e:
      return False
    return result

  def __repr__(self):
    return '(>'+str(self.column)+','+str(self.value)+')'
  
  def sql(self):
    return str(self.column)+'>\''+str(self.value)+'\''
    
class lt_filter(comp_filter):
  
  def eval(self, the_hash):
    if not self.column or not self.value : return False
    if not self.column in the_hash: return False
    try:
      if self.__is_num__(the_hash[self.column]) and self.__is_num__(self.value):
        result =  float(the_hash[self.column]) < float(self.value)
      else:
        result =  the_hash[self.column] < self.value
    except IndexError, e:
      return False
    return result

  def __repr__(self):
    return '(<'+str(self.column)+','+str(self.value)+')'

  def sql(self):
    return str(self.column)+'<\''+str(self.value)+'\''


class eq_filter(comp_filter):

  def eval(self, the_hash):
    if not self.column or not self.value : return False
    if not self.column in the_hash: return False
    try:
      if self.__is_num__(the_hash[self.column]) and self.__is_num__(self.value):
        result =  float(the_hash[self.column]) == float(self.value)
      else:
        result =  the_hash[self.column] == self.value
    except IndexError, e:
      return False
    return result

  def __repr__(self):
    return '(='+str(self.column)+','+str(self.value)+')'

  def sql(self):
    return str(self.column)+'=\''+str(self.value)+'\''




class in_filter(comp_filter):

  def eval(self, the_hash):
    if not self.column or not self.value : return False
    if not self.column in the_hash: return False
    try:
      needly = str(self.value)
      data_str = str(the_hash[self.column]) 
      if data_str.lower().find(needly.lower()) > -1:
        return True
    except NameError, e:
      return False
    return False

  def __repr__(self):
    return '(%'+str(self.column)+','+str(self.value)+')'

  def sql(self):
    return str(self.column)+' like \'%'+str(self.value)+'%\''


class logical_filter(abstract_filter):
  
  def __init__(self, op1 = None , op2 = None):
    if type(self) == logical_filter: 
      raise AbstractClassException('This is an abstract class')
    self.op1 = op1
    self.op2 = op2
  def set_operands(self, op1, op2):
    self.op1 = op1
    self.op2 = op2

class or_filter(logical_filter):

  def eval(self, the_hash):
    return self.op1.eval(the_hash) or self.op2.eval(the_hash)

  def __repr__(self):
    return '(+'+repr(self.op1)+repr(self.op2)+')'

  def sql(self):
    return '('+self.op1.sql()+' or '+self.op2.sql()+')'

  
class and_filter(logical_filter):

  def eval(self, the_hash):
    return self.op1.eval(the_hash) and self.op2.eval(the_hash)

  def __repr__(self):
    return '(.'+repr(self.op1)+repr(self.op2)+')'

  def sql(self):
    return '('+self.op1.sql()+' and '+self.op2.sql()+')'



class not_filter(logical_filter):

  def eval(self, the_hash):
    return not self.op1.eval(the_hash)

  def __repr__(self):
    return '(~'+repr(self.op1)+')'

  def set_operands(self, op):
    self.op1 = op

  def sql(self):
    return '('+' NOT '+self.op1.sql()+')'


class filter_factory:

  def produce(self,filter_type):
    my_filter = None
    if filter_type == '+' : my_filter = or_filter()
    if filter_type == '.' : my_filter = and_filter()
    if filter_type == '~' : my_filter = not_filter()
    if filter_type == '<' : my_filter = lt_filter()
    if filter_type == '>' : my_filter = gt_filter()
    if filter_type == '=' : my_filter = eq_filter()
    if filter_type == '%' : my_filter = in_filter()
    return my_filter


# FILTER EXPRESSIONS PARSER

# BNF
# atom ::= [a-z,0-9,-]
# literal ::= atom | (atom)*
# logop ::= + | .
# negop ::= ~
# cmpop ::= > | < | = | %
# cmpexp ::= (cmpop literal,literal)
# expr ::= cmpexp | (negop expr) | (logop expr expr [expr]*) 

# examples: 
#  expr1 : (+(<d,e)(>c,4)) 
#  meaning of expr1: (d<e) or (c>4)
#   
#             1  2 3    21  2  3    2  3    210   1  2 3    21  2    10  1    0
#
#  expr2 : (+ (. (~(<a,1))  (+ (=a,5)  (=b,8)))   (. (~(=c,9))  (<d,e))  (>t,4) )
#  meaning of expr2: (not(a<1) and ( a=5 or b=8 )) or ( not (c=9) and d<e ) or (t<4)

class FilterParserException(Exception):
  pass


class filter_parser:
  #literals = 'abcdefghijklmnopqrstuvwxyz0123456789-'
  def _debug_(self, *params):
    if self.debug:
     for elem in list(params):
       print str(elem)
  
  def __check_values__(self, *values):
    for elem in list(values):
      if not elem: raise FilterParserException("Invalid operands")

  def __get_operands__(self,expr):
    params = []
    param = ''
    cont = 0
    if expr.find('(') < 0 : return expr.split(',')
    for i in range(0,len(expr)):
      elem = expr[i]
      param += elem
      if elem == '(': cont +=1
      if elem == ')': cont -=1
      if cont == 0:
        params.append(param)
        param = ''
    if cont > 0 : raise FilterParserException("Problems in grouping detected. Missing parenthesis: "+str(cont))
    return params


  def parse(self,expr):
    expr = expr.replace(' ','')
    self._debug_('Expression:',expr)
    m = re.match('\(([+\.~<>=%])(.*)\)$',expr)
    if not m : raise FilterParserException("Can't parse function nor operands")
    func = m.group(1)
    func_params = self.__get_operands__(m.group(2))
    self._debug_('Parsed function',func,'function params',func_params)
    if not func or not func_params: raise FilterParserException("Missing function or function operands")
    if func in '<>=%' :
      try:
        op1 = func_params[0]
        op2 = func_params[1]
      except IndexError, e:
        raise FilterParserException("Wrong number of operands for "+str(func)+" function")
      self.__check_values__(op1,op2)
      my_filter = self.ffactory.produce(func)
      my_filter.set_operands(op1,op2)
      return my_filter
    else:
      if func in '+.':
        func_filter = self.ffactory.produce(func)
        op1 = self.parse(func_params[0])
        if not func_params[1:] : raise FilterParserException('Missing second operand')
        for func_param in func_params[1:]:
          self.__check_values__(func_param)
          op2 = self.parse(func_param)
          func_filter.set_operands(op1,op2)
          op1 = func_filter
          func_filter = self.ffactory.produce(func)
        return op1
      else:
        if func in '~':
          func_filter = self.ffactory.produce(func)
          try:
            op = func_params[0]
          except IndexError, e:
            raise FilterParserException("Wrong number of operands for "+str(func)+" function")
          self.__check_values__(op)
          func_param_filter = self.parse(op)
          func_filter.set_operands(func_param_filter)
          return func_filter
        else:
          raise FilterParserException('Unknown function'+str(func))

  def __init__(self,debug = False):
    self.ffactory = filter_factory()
    self.debug = debug
















