
import sys
import create_charts



def usage():
  print('Usage: python create_qed_dashboard.py <type-of-graph> <dashboard-template> <brand-name> <list-of-test-types>')
  print('Creates an HTML report for a brand and all the types of tests indicated, for the performance dashboard.')


def main():
  if (len(sys.argv) < 4):
    usage()
    sys.exit(2)

  global report_template, graph_measure, chart_template, brand_name, test_types_list
  graph_measure = sys.argv[1]
  report_template = sys.argv[2]
  brand_name = sys.argv[3]
  test_types_list = sys.argv[4].split(',')
  create_report_page()


def create_report_page():
  # Open htmls file for writing
  file_writer_dash = open('external/' + brand_name + '_qed_dashboard.html', 'w')
  file_writer_page = open('external/' + brand_name + '_qed_page.html', 'w')
  # Get the htmls filled with the data needed
  filled_html_dash = get_html_filled(3)
  filled_html_page = get_html_filled(2)
  file_writer_dash.write(filled_html_dash)
  file_writer_page.write(filled_html_page)
  file_writer_dash.close()
  file_writer_page.close()
  

def get_html_filled(graphs_per_line):
  # Get template html file
  template_html = open(report_template, 'r')
  template_html_reader = template_html.read() 
  # Get summary table data
  # summary_table_data = get_summary_table_data(dp)  
  # template_html_reader = template_html_reader.replace('#SUMMARY_RESULTS_TABLE#', summary_table_data)
  # Get summary graphs
  summary_graphs = get_html_graphs(graphs_per_line)
  template_html_reader = template_html_reader.replace('#SUMMARY_GRAPHS#', ''.join(summary_graphs))
  return template_html_reader


def get_summary_table_data(dp):
  # Calculate summary table data
  results_list=[]
  results_list.append(calculate_row_information(dp,'summary'))
  # Merge information and html tags
  return get_table_rows(results_list, dp)


def get_html_graphs(graphs_per_line):
  graphs = []
  num_of_graphs = 0
  graphs.append('\t\t\t\t\t<tr><h2>' + graph_measure.replace(graph_measure[0], graph_measure[0].upper(), 1) + ' Charts</h2></tr>\n')
  graphs.append('\t\t\t\t<tr /><tr /><tr />\n\t\t\t\t<tr>\n')
  for test_type in test_types_list:
    if num_of_graphs == graphs_per_line:
      graphs.append('\t\t\t\t</tr>\n')
      graphs.append('\t\t\t\t<tr>\n')
      num_of_graphs = 0
    grapher = create_charts.historic_trend_charts()
    grapher.compute_urls(brand_name, test_type, 'latency', ['home','search','price','request'], True)
    url_graph = grapher.get_url_array('summary', graph_measure)
    if len(url_graph) > 0:
      graphs.append(get_tagged_graph(test_type))
      num_of_graphs = num_of_graphs + 1
  graphs.append('\t\t\t\t</tr>\n')
  return graphs


def get_tagged_graph(test_type):
  frame_graph = '\t\t\t\t\t<td align="center">\n\t\t\t\t\t\t<h2>' + test_type.replace('_' + graph_measure + '_graph', '').replace('_', ' ').replace('search', '').replace('reprice', '').replace('dynamic packaging', '').replace(test_type[0], test_type[0].upper(), 1) + ' chart</h2>\n'
  graph_file = 'images/' + brand_name + '_' + test_type + '_' + graph_measure + '_graph.png'
  frame_graph += '\t\t\t\t\t\t<img src="' + graph_file + '" frameborder="0"></img>\n'
  frame_graph += '\t\t\t\t\t</td>\n'
  return frame_graph


if __name__ == "__main__":
    main()
