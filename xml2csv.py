import csv
import sys
import jtl_parser

def usage():
  print('Usage: python xml2csv.py <filename>')
  print('Converts JMeter XML jtl log file into csv format.')

if (len(sys.argv) != 2):
  usage()
  sys.exit(2)

jtl = sys.argv[1]
jtlp = jtl_parser.jtl_parser(jtl)
jtlp.generate_csv()
