from django.shortcuts import render
from django.http import HttpResponse
from django.utils.encoding import smart_str
import os
import sqlite3
import csv

from django.shortcuts import render_to_response, HttpResponse
from django.template import RequestContext



# Nomi database
stackoverflow = 'stackoverflow.db'
italian = 'italian.stackexchange.dump.db'
academia = 'academia.dump.db'
db_directory = '/mnt/workingdir/emotions-online-qa/site_SE/databases/db/'

# Query
posts_tags_query = "SELECT Id, Tags, PostTypeId FROM Posts"
answers_query = "SELECT Id, Body, CreationDate FROM Posts WHERE PostTypeId = 2"
answers_query_id = 1
questions_query = "SELECT Id, Body, CreationDate FROM Posts WHERE PostTypeId = 1"
simple_query = "SELECT Id, Body, CreationDate FROM Posts WHERE Id = 4"
most_recent_post_date = "SELECT MAX(CreationDate) FROM Posts ORDER BY CreationDate DESC"
first_post_date = "SELECT MIN(CreationDate) FROM Posts ORDER BY CreationDate DESC"
number_of_users = "SELECT COUNT(Id) from Users"
quest_accepted = "SELECT COUNT(Id) FROM Posts WHERE PostTypeId = 1 AND AcceptedAnswerId IS NOT NULL"
quest_resp_no_accepted = "SELECT COUNT(Id) FROM Posts WHERE PostTypeId = 1 AND AnswerCount > 0 AND AcceptedAnswerId IS NULL"
quest_no_answ = "SELECT COUNT(Id) FROM Posts WHERE PostTypeId = 1 AND AnswerCount = 0"
logit_regr_data = "select PostId, UserQuest as UserId, Reputation, N_Answers, N_Questions, CreationDate, Title, Body, Tags, AcceptedAnswerId from (select count(Users_Answ.Id) as N_Answers, Users_Answ.Id as UserAnsw from Posts Answers, Users Users_Answ where Answers.PostTypeId = 2 and Answers.OwnerUserId = Users_Answ.Id group by (Users_Answ.Id)), (select count(Users_Quest.Id)as N_Questions, Users_Quest.Id as UserQuest, Users_Quest.Reputation as Reputation from Posts Questions, Users Users_Quest where Questions.PostTypeId = 1 and		Questions.OwnerUserId = Users_Quest.Id group by (Users_Quest.Id)), (select Id as PostId, Title, Body, Tags, CreationDate, OwnerUserId, AcceptedAnswerId from Posts where Posts.PostTypeId = 1) where UserQuest = UserAnsw and OwnerUserId = UserQuest"


all_queries = [{'id':'1','title':"List of all answers with id, body and creation date", 'quer':answers_query}, 
		{'id':'2','title':"List of all questions with id, body and creation date", 'quer':questions_query}, 
		{'id':'3','title':"Post with id 4 with body and creation date", 'quer':simple_query}, 
		{'id':'4','title':"List of all posts with id, tags and the type", 'quer':posts_tags_query}, 
		{'id':'5','title':"Date of the most recent post", 'quer':most_recent_post_date}, 
		{'id':'6','title':"Date of the first post", 'quer':first_post_date}, 
		{'id':'7','title':"Number of all users", 'quer':number_of_users}, 
		{'id':'8','title':"Number of questions with an 'accepted' answer", 'quer':quest_accepted}, 
		{'id':'9','title':"Number of questions with at least one answer but with no 'accepted' answer", 'quer':quest_resp_no_accepted}, 
		{'id':'10','title':"Number of questions with no answer", 'quer':quest_no_answ},
		{'id':'11','title':"Data for the logistic regression", 'quer':logit_regr_data}]


dbs = [{'title':"Stackoverflow",'dir':stackoverflow},
	{'title':"Italian",'dir':italian},
	{'title':"Academia",'dir':academia}]


# Create your views here.

def databases(request):
	#curr_dir = os.getcwd()
	#dbs = os.listdir(curr_dir + '/' + db_directory)
	#dbs = os.listdir(db_directory)
	page_title = "Choose a database"
	return render(request, 'index.html', {'page_title': page_title, 'dbs': dbs})

def queries(request, db_title):
	page_title = "Query List"
	return render(request, 'queries.html', {'page_title': page_title, 'all_queries': all_queries, 'db_title': db_title})

def get_query(query_id):
	for q_elem in all_queries:
		if q_elem['id'] == query_id:
			query = q_elem['quer']
	return query

def get_db_dir(db_title):
	for db_elem in dbs:
		if db_elem['title'] == db_title:
			db = db_elem['dir']
	return db

def process_csv(request, db_title, query_id):
	query = get_query(query_id)
	db = get_db_dir(db_title)
	result_set = execute_query(db, query)
	resp_csv = download_csv(request, result_set)
	return resp_csv
	
def process_vis(request, db_title, query_id):
	query = get_query(query_id)
	db = get_db_dir(db_title)
	page_title = "Result set"
	result_set = execute_query(db, query)
	desc = result_set.description
	fields = []
	for d in desc:
		fields = fields + [d[0]]

	return render(request, 'results.html', {'page_title': page_title, 'result_set': result_set, 'fields': fields})

def execute_query(db, query):
	path_to_db = db_directory + db
	conn = sqlite3.connect(path_to_db)
	c = conn.cursor()
	result_set = c.execute(query)
	
	return result_set

def download_csv(request, result_set):
	resp = HttpResponse(content_type='text/csv')
	resp['Content-Disposition'] = 'attachment; filename="result-set.csv"'
	
	writer = csv.writer(resp)
	
	desc = result_set.description # Prende i campi della tabella
	fields = []
	for d in desc:
		fields = fields + [d[0]]

	writer.writerow(fields)

	for row in result_set: # Prende i record della tabella
		row_to_write = []
		for c in row:
			row_to_write = row_to_write + [smart_str(c)]
		writer.writerow(row_to_write)

	return resp



#Alec Larsen - University of the Witwatersrand, South Africa, 2012 import shlex, subprocess

def RateSentiment(sentiString):
    #open a subprocess using shlex to get the command line string into the correct args list format
    p = subprocess.Popen(shlex.split("java -jar SentiStrength.jar stdin sentidata C:/SentStrength_Data/"),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    #communicate via stdin the string to be rated. Note that all spaces are replaced with +
    stdout_text, stderr_text = p.communicate(sentiString.replace(" ","+"))
    #remove the tab spacing between the positive and negative ratings. e.g. 1    -5 -> 1-5
    stdout_text = stdout_text.rstrip().replace("\t","")
    return stdout_text
