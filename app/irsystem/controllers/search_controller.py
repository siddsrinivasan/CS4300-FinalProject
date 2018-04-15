from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Informd"
net_id = "Evan Pike: dep78, Edward Mei: ezm4, Lucas Van Bramer: ljv32, Siddharth Srinavasan: ss2969, Wes Gurnee: rwg97"

@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('search')
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + query
		data = [("20151005", "Pickles are national holiday"), ("20151005", "Pickles are actually cucumbers"), ("20141204", "Pickles outlawed in Arab Spring")]

		#actual data format: list with tuples ("unique identifier", headline).
		# Need to parse unique identifier and convert it to date. 
		# Need to group all events of the same date together for the timeline card.
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)



