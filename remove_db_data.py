import sys
import qed_data_publisher


def usage():
  print('Usage: python remove_db_data.py <list-of-pts_ids-from-summary-table> (SEPARATED BY ",")')
  print('Erases all the rows with the pts_ids indicated from the summary table, and the linked rows from the detailed table.')


def main():
  if (len(sys.argv) < 2):
    usage()
    sys.exit(2)

  pts_ids = sys.argv[1].split(',')
  qp = qed_data_publisher.data_publisher(None)
  for _id in pts_ids: # because id is python function
    qp.remove_test(_id)

if __name__ == "__main__":
    main()

