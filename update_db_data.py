import data_processor
import sys
import qed_data_publisher
import jtl_parser


def main():
  if (len(sys.argv) != 2):
    usage()
    sys.exit(2)
  jtl_file = sys.argv[1]
  
  jtlp = jtl_parser.jtl_parser(jtl_file)
  jtlp.generate_csv()

  csv_file = jtlp.get_csv_filename()
  dp = data_processor.data_processor(csv_file)

  publisher = qed_data_publisher.data_publisher(dp)

  split_file = csv_file.split('/')
  brand_name = split_file[1]
  # The name of the test is the csv file name except the extension (.csv)
  test_name = split_file[2][:-4].replace(brand_name + '_','').replace('_hudson_report','')

  publisher.setup_brand(brand_name)
  publisher.setup_test_name(brand_name + '_' + test_name)


  publisher.publish(update = True)

if __name__ == "__main__":
    main()
