import create_charts
import data_processor
import sys
import qed_data_publisher

def main():
  if (len(sys.argv) != 2):
    usage()
    sys.exit(2)
  csv_file = sys.argv[1]

  dp = data_processor.data_processor(csv_file)

#  grapher = create_charts.orbitz_google_charts_wrapper(dp)
#  grapher.compute_urls(download_charts = True)
  #grapher.compute_urls(download_charts = True, opt_labels = ['home_2','sHOP'])

  publisher = qed_data_publisher.data_publisher(dp)
  publisher.setup_brand('ebuk')
  publisher.publish(update = True)
  #publisher.remove_test(103)

#  print grapher.get_url('summary','latency')
#  print
#  print grapher.get_url('summary','throughput')
#  print
#  print grapher.get_url('detailed','latency')
#  print
#  print grapher.get_url('detailed','throughput')
#  print
#  print grapher.get_url('detailed','elapsed')

if __name__ == "__main__":
    main()
