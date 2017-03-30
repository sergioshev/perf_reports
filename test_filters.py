import filters


#the_hash = { 'c1' : 5 , 'c2' : 10 , 'c3' : -10 }
the_hash = { 'c1' : '5' , 'c2' : '11' , 'c3' : '-10' , 'c4': 'abcdf' }
print the_hash
#f = filters.bool_filter()

andf = filters.and_filter()
eqf1 = filters.eq_filter('c1',5)
eqf2 = filters.eq_filter('c2',11)

andf.set_operands(eqf1,eqf2)

orf = filters.or_filter(eqf1,eqf2)

notf = filters.not_filter(orf)

inf = filters.in_filter('c4','cf')

print inf.eval(the_hash)
print repr(inf)

print repr(andf)
print andf.eval(the_hash)
print repr(orf)
print orf.eval(the_hash)
print repr(notf)
print notf.eval(the_hash)



f = filters.or_filter(inf,andf)
print repr(f)
print f.eval(the_hash)

print f.sql()
