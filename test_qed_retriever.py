from  qed_data_retriever import pts_retriever

ptsr = pts_retriever()

#ptsr.set_filter_by_expr('(.(>latency,1)(<latency,30))')
#ptsr.set_filter_by_expr('(=latency,1.33453)')
#ptsr.set_filter_by_expr('(=name,ctix_car_search_reprice)')
ptsr.set_filter_by_expr('(.(%name,ebuk_hotel_guest_review)(+(=start,2010-11-11T00:00:00Z)(>start,2010-11-11T00:00:00Z))(+(=start,2010-11-12T23:59:59Z)(<start,2010-11-12T23:59:59Z)))')

print ptsr.select_sql()
#print ptsr.get_values(columns = ['id','latency','error-rate','start'])
#print ptsr.get_values(columns = ['id','latency','error-rate','start'], sort_by = 'latency')
#print ptsr.get_values(columns = ['id','latency','error-rate','start'], sort_by = 'error-rate')
#print ptsr.get_values(columns = ['id','latency','error-rate','start'], sort_by = 'start')
#ptsr.set_filter_by_expr('(=name,ebuk_hotel)')
#print ptsr.get_values(sort_by = 'start')

