import sqlite3
import csv
import os
import datetime
from badgesDict import badges

def getUsersAnswersAcceptedQuery(user, date):
	return "SELECT Posts.OwnerUserId AS UserId, count(Posts.Id) AS UsersAnswersAccepted FROM Posts INNER JOIN Votes ON Posts.Id = Votes.PostId WHERE Posts.PostTypeId = 2 AND Posts.OwnerUserId = " + user + " AND Votes.CreationDate < \'" + date + "\' AND Votes.VoteTypeId = 1"

def getUsersQuestionsAcceptedQuery1(user, date):
	return "SELECT Posts.OwnerUserId AS UserId, count(Posts.Id) AS UsersQuestionsAccepted FROM Posts INNER JOIN Votes ON Posts.AcceptedAnswerId = Votes.PostId WHERE Posts.PostTypeId = 1 AND Posts.AcceptedAnswerId IS NOT NULL  AND Posts.OwnerUserId = " + user + " AND Votes.CreationDate < \'" + date + "\' AND Votes.VoteTypeId = 1"

def getUsersQuestionsAcceptedQuery2(user, date):
	return "SELECT Quest.OwnerUserId AS UserId, count(Quest.Id) AS UsersQuestionsAccepted FROM Posts Quest INNER JOIN Posts Answ ON Quest.AcceptedAnswerId = Answ.Id INNER JOIN Votes ON Answ.Id = Votes.PostId WHERE Quest.PostTypeId = 1 AND Quest.AcceptedAnswerId IS NOT NULL  AND Quest.OwnerUserId = " + user + " AND Votes.CreationDate < \'" + date + "\' AND Votes.VoteTypeId = 1"

# Estrae il numero di upvotes, prima di una certa data (@Date), ottenuti dalle domande postate da un certo utente (@User) */
def getQuestUpVotes(user, date):
	return "SELECT Posts.OwnerUserId AS UserId, count(Posts.Id) AS UpVotesQuest FROM Posts INNER JOIN Votes ON Posts.Id = Votes.PostId WHERE Posts.PostTypeId = 1 AND Votes.VoteTypeId = 2 AND Votes.CreationDate < \'" + date + "\' AND Posts.OwnerUserId = " + user

# Estrae il numero di downvotes, prima di una certa data (@Date), ottenuti dalle domande postate da un certo utente (@User) */
def getQuestDownVotes(user, date):
	return "SELECT Posts.OwnerUserId AS UserId, count(Posts.Id) AS DownVotesQuest FROM Posts INNER JOIN Votes ON Posts.Id = Votes.PostId WHERE Posts.PostTypeId = 1 AND Votes.VoteTypeId = 3 AND Votes.CreationDate < \'" + date + "\' AND Posts.OwnerUserId = " + user

# Estrae il numero di upvotes, prima di una certa data (@Date), ottenuti dalle risposte postate da un certo utente (@User) */
def getAnswUpVotes(user, date):
	return "SELECT Posts.OwnerUserId AS UserId, count(Posts.Id) AS UpVotesAnsw FROM Posts INNER JOIN Votes ON Posts.Id = Votes.PostId WHERE Posts.PostTypeId = 2 AND Votes.VoteTypeId = 2 AND Votes.CreationDate < \'" + date + "\' AND Posts.OwnerUserId = " + user

# Estrae il numero di downvotes, prima di una certa data (@Date), ottenuti dalle risposte postate da un certo utente (@User) */
def getAnswDownVotes(user, date):
	return "SELECT Posts.OwnerUserId AS UserId, count(Posts.Id) AS DownVotesAnsw FROM Posts INNER JOIN Votes ON Posts.Id = Votes.PostId WHERE Posts.PostTypeId = 2 AND Votes.VoteTypeId = 3 AND Votes.CreationDate < \'" + date + "\' AND Posts.OwnerUserId = " + user

# Estrae l'insieme dei badge sbloccati da un utente (@User) prima di una certa data (@Date) */
def getBadges(user, date):
	return "SELECT Badges.UserId, Badges.Name FROM Badges WHERE Badges.Date < \'" + date + "\' AND Badges.UserId = " + user


def execute_param_query(db, query):
	conn = sqlite3.connect(db)
	c = conn.cursor()
	result_set = c.execute(query)
	return result_set

def build_dataset(db, file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'))
	
	head = dict_reader.fieldnames
	head.append('UsersAnswersAccepted')
	head.append('UsersQuestionsAccepted')
	#head.append('UsersQuestionsAccepted2')
	head.append('QuestionScore')
	head.append('AnswerScore')
	head.append('BronzeBadge')
	head.append('SilverBadge')
	head.append('GoldBadge')
	head.append('Weekday')
	head.append('CodeSnippet')
	dict_writer = csv.DictWriter(open(output_file, 'w'), head)
	dict_writer.writerow(dict((fn,fn) for fn in head)) #Scrive gli header
	DayL = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

	p_badges = []

	for row in dict_reader:
		user = row['UserId']
		date = row['PostCreationDate']
		body = row['Body']
		print "User: ",user
		print "Date: ",date,"\n"
		if user != 'None':
			result_set1 = execute_param_query(db, getUsersAnswersAcceptedQuery(user, date))
			result_set2 = execute_param_query(db, getUsersQuestionsAcceptedQuery1(user, date))
			#result_set3 = execute_param_query(db, getUsersQuestionsAcceptedQuery2(user, date))
			result_set4 = execute_param_query(db, getQuestUpVotes(user, date))
			result_set5 = execute_param_query(db, getQuestDownVotes(user, date))
			result_set6 = execute_param_query(db, getAnswUpVotes(user, date))
			result_set7 = execute_param_query(db, getAnswDownVotes(user, date))
			result_set8 = execute_param_query(db, getBadges(user, date))
		
			for tup in result_set1:
				row['UsersAnswersAccepted'] = tup[1]
			for tup in result_set2:
				row['UsersQuestionsAccepted'] = tup[1]
			#for tup in result_set3:
			#	row['UsersQuestionsAccepted2'] = tup[1]
			for tup in result_set4:
				q_up = tup[1]
			for tup in result_set5:
				q_down = tup[1]
			for tup in result_set6:
				a_up = tup[1]
			for tup in result_set7:
				a_down = tup[1]
		
			q_score = q_up - q_down
			a_score = a_up - a_down
			
			row['QuestionScore'] = q_score
			row['AnswerScore'] = a_score

			bronze = 0
			silver = 0
			gold = 0

			for tup in result_set8:
				if badges.has_key(tup[1]):
					if badges[tup[1]] == 'Bronze':
						bronze += 1
					if badges[tup[1]] == 'Silver':
						silver += 1
					if badges[tup[1]] == 'Gold':
						gold += 1
				else:
					p_badges.append(tup[1])
					
			row['BronzeBadge'] = bronze
			row['SilverBadge'] = silver
			row['GoldBadge'] = gold
			
			d = date.split('T')
			dat = d[0].split('-')
			hour = d[1]
			
			print "Anno: ", dat[0]
			print "Mese: ", dat[1]
			print "Giorno: ", dat[2]
			
			weekday = DayL[datetime.date(int(dat[0]),int(dat[1]),int(dat[2])).weekday()] + ""
			row['Weekday'] = weekday
			
			code_snippet = "no"
			if '<code>' in body:
				code_snippet = "yes"

			row['CodeSnippet'] = code_snippet
		dict_writer.writerow(row)
	
	print p_badges
	return 'Done'

def p_badges(db, file_name):
	dict_reader = csv.DictReader(open(file_name, 'r'))
	new_badges = open("badges.txt", 'w')

	p_badges = []

	for row in dict_reader:
		user = row['UserId']
		date = row['PostCreationDate']
		
		print "User: ",user
		print "Date: ",date,"\n"
		if user != 'None':
			
			result_set8 = execute_param_query(db, getBadges(user, date))
		
			bronze = 0
			silver = 0
			gold = 0

			for tup in result_set8:
				if badges.has_key(tup[1]):
					if badges[tup[1]] == 'Bronze':
						bronze += 1
					if badges[tup[1]] == 'Silver':
						silver += 1
					if badges[tup[1]] == 'Gold':
						gold += 1
				else:
					if tup[1] in p_badges:
						print ""
					else:
						p_badges.append(tup[1])
						new_badges.write(tup[1]+"\n")
					
			row['BronzeBadge'] = bronze
			row['SilverBadge'] = silver
			row['GoldBadge'] = gold
			
		#dict_writer.writerow(row)
	new_badges.close()
	print p_badges
	return 'Done'

#build_dataset('academia.dump.db', 'result-set.csv', 'prova_social+day+code.csv')
p_badges('academia.dump.db', 'result-set.csv', 'prova_badges.csv')
