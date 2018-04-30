from . import *
import sys
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models import search as search
from app.irsystem.models import search_prot1 as search_prot1
from app.irsystem.models import search_prot2 as search_prot2
import json
import os
import pickle


# Change this parameter if the file path is different

BASE = "app/irsystem/controllers"
auto_complete_list= pickle.load(open(os.path.join(BASE, 'autocomplete_bigram_vocab.pickle'), 'rb'))

reload(sys)
sys.setdefaultencoding('utf8')
project_name = "Informd"
net_id = "Edward Mei: ezm4, Evan Pike: dep78, Lucas Van Bramer: ljv32, Sidd Srinivasan: ss2969, Wes Gurnee: rwg97"
# searching_message = None 

@irsystem.route('/', methods=['GET'])
def search_current():
	query = request.args.get('search')
	sort_order = request.args.get('sort_order')
	precision_recall_percent = request.args.get('precision_recall')
	date_range = request.args.get('date_range')
	try:
		precision_recall_percent = int(precision_recall_percent)
	except:
		pass

	try:
		date_range = int(date_range)
	except:
		pass

	if not query:
		b = []
		c = []
		array_json = []
		output_message = ''
	else:
		change_month = {"01": "January", "02" :"February", "03" : "March", "04" : "April",
		 "05": "May", "06": "June", "07": "July", "08":"August", "09":"September", "10":"October",
		 "11":"November", "12": "December"}
		res= search.complete_search(query)

		b= []
		c = []
		array_json = []
		
		for each_result in res:
			length_card = len(each_result)
			reddit_score = "NA"
			reddit_score_int = 0
			coherence_score = each_result[-1]
			url = "nope"
			#account for no reddit score
			if length_card > 3:
				reddit_score = str(each_result[2])
				reddit_score_int = int(each_result[2])
				url = str(each_result[4])
			year = each_result[0][:4]
			day  = each_result[0][6:8]
			month = each_result[0][4:6]
			date=  change_month[str(month)] + ' ' + str(int(day)) + ', ' + str(year)
			date_int = int(year) + round(int(month)/12.0, 2) + round(int(day)/32.0, 2) *.01
			headline=['a']
			headline[0]= each_result[1]

			b.append((date, headline, date_int, reddit_score, url, reddit_score_int, coherence_score))


		# remove docs outside the date range
		b_prime = []
		for doc in b:
			if not (doc[2] < date_range):
				b_prime.append(doc)

		b = b_prime
		# change the number of documents returned based on user input P/R 
		# default score of 100 to return all returned documents.
		if (precision_recall_percent < 100.0):
			num_docs = len(b)		# need to check this 
			num_docs_returned = max(int((num_docs * (precision_recall_percent / 100.0))), 2)

			b = b[:num_docs_returned] 

		if sort_order == "option1":
			b = sorted(b, key=lambda x: x[2], reverse = True)
		elif sort_order =="option2":
			b = sorted(b, key=lambda x: x[2])
		elif sort_order == "option3": # since the docs are returned in order, do nothing.
			# b = sorted(b, key=lambda x: x[5], reverse = True)
			c = sorted(b, key=lambda x: x[2], reverse = True)

		output_message = "Your search: " + query
		searching_message = ""

		# actual data format: list with tuples ("unique identifier", headline).
		# Need to parse unique identifier and convert it to date.
		# Need to group all events of the same date together for the timeline card.
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=b, json = array_json, relevance_data=c,
	 auto_complete = auto_complete_list)


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


@irsystem.route('/prototype2/', methods=['GET'])
def search_prot2_controller():
	query = request.args.get('search')
	if not query:
		b = []
		output_message = ''
	else:
		change_month = {"01": "January", "02" :"February", "03" : "March", "04" : "April",
		 "05": "May", "06": "June", "07": "July", "08":"August", "09":"September", "10":"October",
		 "11":"November", "12": "December"}
		res= search_prot2.complete_search(query)

		b= []
		for each_result in res:
			length_card = len(each_result)
			reddit_score = "N/A"
			url = "nope"
			#account for no reddit score
			if length_card > 2:
				reddit_score = str(each_result[2])
				url = str(each_result[4])
			year = each_result[0][:4]
			day  = each_result[0][6:8]
			month = each_result[0][4:6]
			date=  change_month[str(month)] + ' ' + str(int(day)) + ', ' + str(year)
			date_int = int(year) + int(month) * .01 + int(day) *.0001
			headline=['a']
			headline[0]= each_result[1]

			b.append((date, headline, date_int, reddit_score, url))

		b = sorted(b, key=lambda x: x[2], reverse = True)

		output_message = "Your search: " + query

		# actual data format: list with tuples ("unique identifier", headline).
		# Need to parse unique identifier and convert it to date.
		# Need to group all events of the same date together for the timeline card.
	return render_template('search_prot2.html', name=project_name, netid=net_id, output_message=output_message, data=b)
