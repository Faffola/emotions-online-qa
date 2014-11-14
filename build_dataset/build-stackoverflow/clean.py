import csv

# Copia solo le colonne desiderate da un file csv e rinomina il campo 'Accepted', 
# nel caso ci fosse, in 'Successful'.
#
# parametri:
#	input_file: nome del file csv da cui leggere
#	output_file: nome del file csv su cui scrivere, il file conterrà tutte le colonne
#		di input_file tranne quelle definite nel parametro rm_columns
#	rm_columns: vettore che contiene i nomi delle colonne da non copiare 
def drop_column(input_file, output_file, rm_columns):
	dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';') # DELIMITER
	
	f = []
	for header in dict_reader.fieldnames:
		if header == 'Accepted':
			f.append('Successful')
		elif header not in rm_columns:
			f.append(header)
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f) # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header

	for row in dict_reader:
		row_cleaned = {}
		for field in row.keys():
			if field == 'Accepted':
				row_cleaned['Successful'] = row['Accepted']
			elif field not in rm_columns:
				#print 'Copy: ', field
				#print 'Value: ', row[field]
				#print '\n'
				row_cleaned[field] = row[field]
		#break
		dict_writer.writerow(row_cleaned)

c = ['Title', 'Body', 'Tags', 'PostCreationDate', 'UserId', 'PostAcceptedAnswerId', 'AnswerCount', 'HasAnswer', 'NoAnswer']
