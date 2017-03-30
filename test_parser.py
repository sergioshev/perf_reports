import re
import filters

expr = '(+ (. (~(<a,1)) (+ (=a,5) (=b,8))) (. (~(=c,9)) (<d,e)) (>t,4) )'

print expr
fp = filters.filter_parser(debug = True)
f = fp.parse(expr)
f2 = fp.parse(repr(fp.parse(expr)))
print repr(f)
print repr(f2)

the_hash = { 't' : '3', 'c': 9 , 'd' : 'a' }

print f.eval(the_hash)
