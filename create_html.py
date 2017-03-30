import csv
import sys
import math
import datetime
import create_charts
import data_processor
import qed_data_publisher

from operator import itemgetter


def usage():
  print('Usage: python create_html.py <csv-filename> <report-template-name> <chart-template-name> <save-to-DB-boolean> [<labels-for-graph>]')
  print('Converts a CSV file with JMeter report data into html tables and saves the information on the DB.')


def create_html(csv_file, r_template, c_report, dump_to_db, labels):
  global report_tamplate, chart_report, graphs_labels
  report_tamplate = r_template 
  chart_report = c_report
  graphs_labels = labels
  set_variables(csv_file)
  dp = data_processor.data_processor(csv_file)
  if dump_to_db:
    db_publisher = qed_data_publisher.data_publisher(dp)
    db_publisher.setup_brand(brand_name)
    db_publisher.setup_test_name(brand_name + '_' + test_name)
    db_publisher.publish()
  create_report_page(csv_file, dp)


def main():
  if (len(sys.argv) < 4):
    usage()
    sys.exit(2)

  csv_file = sys.argv[1]
  r_template = sys.argv[2]
  c_report = sys.argv[3]
  save_to_db = sys.argv[4]
  g_labels = []
  if (len(sys.argv) > 5):
    g_labels = sys.argv[5].split(',')
  create_html(csv_file, r_template, c_report,save_to_db.lower() == 'true', g_labels)

def set_variables(csv_file):
  global report_path, charts_path, test_name, brand_name, page_title
  split_file = csv_file.split('/') 
  report_path = split_file[0] + '/' + split_file[1] 
  charts_path = 'charts' 
  brand_name = split_file[1]
  # The name of the test is the csv file name except the extension (.csv)
  test_name = split_file[2][:-4].replace(brand_name + '_','').replace('_hudson_report','')
  # The test name but with spaces instead of "_" and letter in upper case
  split_test_name = test_name.replace('_', ' ').upper()
  page_title = split_test_name + ' - ' + str(datetime.datetime.now())


def create_report_page(csv_file, dp):
  # Open html file for writing
  html_file = csv_file[:-4] + '.html'
  file_writer = open(html_file, 'w')
  # Get the html filled with the data needed
  filled_html = get_html_filled(csv_file, dp)
  file_writer.write(filled_html)
  file_writer.close()


def get_html_filled(csv_file, dp):
  grapher = create_charts.orbitz_google_charts_wrapper(dp)
  grapher.compute_urls(brand_name, test_name, graphs_labels)
  # Get template html file
  template_html = open(report_tamplate, 'r')
  template_html_reader = template_html.read() 
  # Insert the data needed on the template
  template_html_reader = template_html_reader.replace('#PAGE_TITLE#', page_title)
  template_html_reader = template_html_reader.replace('#PAGE_DATA_PATH#', brand_name + '_report_page_data')
  # Get summary table data
  summary_table_data = get_summary_table_data(dp)  
  template_html_reader = template_html_reader.replace('#SUMMARY_RESULTS_TABLE#', summary_table_data)
  # Get summary graphs
  summary_graphs = get_html_graphs(grapher,'summary')
  template_html_reader = template_html_reader.replace('#SUMMARY_GRAPHS#', ''.join(summary_graphs))
  # Get page detailed table data
  page_detailed_data = get_page_detailed_data(dp)  
  template_html_reader = template_html_reader.replace('#PAGE_DETAILED_RESULTS_TABLE#', page_detailed_data)
  # Get page detailed graphs
  detailed_graphs = get_detailed_html_graphs(grapher, 'detailed')
  template_html_reader = template_html_reader.replace('#DETAILED_GRAPHS#', ''.join(detailed_graphs))
  return template_html_reader


def get_summary_table_data(dp):
  # Calculate summary table data
  results_list=[]
  results_list.append(calculate_row_information(dp,'summary'))
  # Merge information and html tags
  return get_table_rows(results_list, dp)


def get_page_detailed_data(dp):
  pages_info = []
  for label in dp.get_labels():
    pages_info.append(process_page_info(dp, label))
  return get_table_rows(pages_info, dp)


def process_page_info(dp, current_label):
  partial_result = calculate_row_information(dp, current_label)	# calculate the information for 1 page
  page_info = [current_label]
  page_info.extend(partial_result)  
  return page_info


def calculate_row_information(dp, label):
  # Variables used to store information from the csv file
  result = []
  result.extend([str(dp.get_last(label,'samples')),
                 str(round(dp.get_last(label,'elapsed'),2))+' ms',
                 str(dp.get_min(label,'elapsed'))+' ms',
                 str(dp.get_max(label,'elapsed'))+' ms',
                 str(round(dp.get_last(label,'std_dev'),2)),
                 str(round(dp.get_last(label,'error_rate'),2))+'%',
                 str(round(dp.get_last(label,'throughput'),2))+' tpm',
                 str(round(float(dp.get_last(label,'bytes_sec')) / 1024, 2))])
  return result


def get_table_rows(rows_list, dp):
  table_rows = ''
  for row in rows_list:
    failed = ''
    # If the failure percent column is not 0.0% then paint that line in red color
    if (row[5] != '0.0%') and (row[6] != '0.0%'):
      failed = ' class="Failure"'
    table_rows = table_rows + '\t\t\t<tr valign="top"' + failed + '>\n'
    for col in row:
      table_rows = table_rows + '\t\t\t\t<td>' + col + '</td>\n'					
    table_rows = table_rows + '\t\t\t</tr>\n'
  return table_rows 


def get_detailed_html_graphs(grapher, graph_type):
  graphs = get_html_graphs(grapher, graph_type)
  graphs.append('\t\t\t\t<tr /><tr /><tr />\n\t\t\t\t<tr>\n')
  graphs.append(get_tagged_graph(grapher, graph_type, 'elapsed')) 
  graphs.append('\t\t\t\t</tr>\n') 
  return graphs


def get_html_graphs(grapher, graph_type):
  graphs = []
  graphs.append('\t\t\t\t<tr /><tr /><tr />\n\t\t\t\t<tr>\n')
  graphs.append(get_tagged_graph(grapher, graph_type, 'throughput'))
  graphs.append(get_tagged_graph(grapher, graph_type, 'latency'))
  graphs.append('\t\t\t\t</tr>\n')
  return graphs


def get_tagged_graph(grapher, graph_type, graph_measure):
  url_graph = grapher.get_url_array(graph_type, graph_measure)
  center_graph = ''
  if graph_measure == 'elapsed':
    center_graph = ' colspan="2"'
  frame_graph = '\t\t\t\t\t<td align="center"' + center_graph + '>\n'
  frame_graph += '\t\t\t\t\t\t<h2>' + graph_measure.replace(graph_measure[0], graph_measure[0].upper(), 1) + ' Chart</h2>\n'
  graph_file = charts_path + '/' + test_name + '_' + graph_type + '_' + graph_measure + '_graph.html'
  frame_graph += '\t\t\t\t\t\t<iframe src="' + graph_file + '" width="' + str(grapher.get_chart_width(graph_measure)+35) + '" height="' + str(grapher.get_chart_height(graph_measure)+30) + '" frameborder="0"></iframe>\n'
  frame_graph += '\t\t\t\t\t</td>\n'
  create_html_graph(url_graph, graph_file)
  return frame_graph
 
  
def create_html_graph(url_graph, graph_file):
  # Open html file for writing the chart parameters
  html_file = report_path + '/' + graph_file
  file_writer = open(html_file, 'w')
  # Get post graph template html file
  template_html = open(chart_report, 'r')
  template_html_reader = template_html.read()
  chart_params = '' 
  for key, value in url_graph.iteritems():
    chart_params += '\t\t\t<input type=\'hidden\' name=\'' + key + '\' value=\'' + value + '\'/>\n'
  # Insert the data needed on the template
  template_html_reader = template_html_reader.replace('#CHART_PARAMS#', chart_params)
  file_writer.write(template_html_reader)
  file_writer.close()


if __name__ == "__main__":
    main()
