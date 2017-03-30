import create_charts

def main():
  grapher = create_charts.historic_trend_charts()
  
#  grapher.compute_urls(item = 'latency',
#                       labels = ['Search','Home','Re-price'], 
#                       brand = 'ebuk', 
#                       test_type = 'car_search', 
#                       download_charts = True)
#  print grapher.get_url('summary','latency')
  print
  grapher.compute_urls(item = 'throughput',
#                       labels = ['nters'], 
                       labels = ['Re-price'], 
                       brand = 'ebuk', 
                       test_type = 'car_search', 
                       download_charts = True)
  print grapher.get_url('summary','throughput')




  #grapher.compute_urls(test_type = 'ebuk_hotel', download_charts = True)
  #grapher.compute_urls(download_charts = True, opt_labels = ['home_2','sHOP'])

  #publisher = qed_data_publisher.data_publisher(dp)
  #publisher.setup_brand('ebuk')
  #publisher.publish()
  #publisher.remove_test(103)

#  print grapher.get_url('summary','throughput')
#  print
#  print grapher.get_url('detailed','latency')
#  print
#  print grapher.get_url('detailed','throughput')
#  print
#  print grapher.get_url('detailed','elapsed')

if __name__ == "__main__":
    main()
