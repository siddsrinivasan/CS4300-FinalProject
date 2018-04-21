from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models import search as search
from app.irsystem.models import search_prot1 as search_prot1

project_name = "Informd"
net_id = "Evan Pike: dep78, Edward Mei: ezm4, Lucas Van Bramer: ljv32, Siddharth Srinavasan: ss2969, Wes Gurnee: rwg97"

@irsystem.route('/', methods=['GET'])
def search_current():
	query = request.args.get('search')
	if not query:
		b = []
		output_message = ''
	else:
		res= search.return_docs(query)

		b= []
		for each_result in res:
			date= str(each_result[0][:4]) + '/' + str(each_result[0][4:6]) + '/' + str(each_result[0][6:8])
			headline=['a']
			headline[0]= each_result[1]
			b.append((date, headline))

		output_message = "Your search (new): " + query

		# actual data format: list with tuples ("unique identifier", headline).
		# Need to parse unique identifier and convert it to date.
		# Need to group all events of the same date together for the timeline card.
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=b)


@irsystem.route('/prototype1/', methods=['GET'])
def search_prot1_controller():
	query = request.args.get('search')
	if not query:
		b = []
		output_message = ''
	else:
		res= search_prot1.return_docs(query)

		b= []
		for each_result in res:
			date= str(each_result[0][:4]) + '/' + str(each_result[0][4:6]) + '/' + str(each_result[0][6:8])
			headline=['a']
			headline[0]= each_result[1]
			b.append((date, headline))

		output_message = "Your search: " + query

		# actual data format: list with tuples ("unique identifier", headline).
		# Need to parse unique identifier and convert it to date.
		# Need to group all events of the same date together for the timeline card.
	return render_template('search_prot1.html', name=project_name, netid=net_id, output_message=output_message, data=b)
