from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Informd"
net_id = "Evan Pike: dep78, Edward Mei: ezm4, Lucas Van Bramer: ljv32, Siddharth Srinavasan: ss2969, Wes Gurnee: rwg97"

@irsystem.route('/', methods=['GET'])


# def parseId(idstring):
# 	return idstring[:8]


# def dateDict(data):
# 	for element in data:
# 		date = parseId(element[0])
# 		element = (date, element[1])

# 	dict1 = {}

# 	for element in data:

# 		date = element[0]
# 		if date in dict1:
# 			dict1[date].append(element[1])
# 		else:
# 			dict1[date] = [element[1]]

# 	sorted_list = []

# 	for key1 in dict1:

# 		temp_list = []
# 		for article in dict1[key1]:

# 			temp_list.append(article)

# 		sorted_list.append((key1, temp_list))


# 	return sorted_list
def search():
	query = request.args.get('search')
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + query
		first8 = "20151006"

		year = first8[:4]
		month = first8[4:6]
		date = first8[6:]

		y = (month + "/" + date + "/" + year )

		data = [(y, ["Pickles pickles pickles pickle pickles. Pickles","2","3","4","5"]), ("06/05/2018", ["1","2","3","4","5"]), ("01/10/2019", ["1","2","3","4","5"])]


		#actual data format: list with tuples ("unique identifier", headline).
		# Need to parse unique identifier and convert it to date.
		# Need to group all events of the same date together for the timeline card.
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)
