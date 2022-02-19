import csv
import format as form
import json
# with open('data/table_format.csv','r') as file:
#     csv_reader = csv.reader(file)

#     for line in csv_reader:
#         print(line)
with open("curr_database" + "/" + "table_name" + ".csv", 'r') as csv_table_file: #Create the table as a csv file
    csv_writer = csv.reader(csv_table_file)
    fields = list(csv_writer)
    print(fields[0])
with open("curr_database" + "/" + "table_name" + ".csv", 'w') as csv_table_file: #Create the table as a csv file
    csv_writer = csv.writer(csv_table_file)
    fields[0][0] = 2
    fields[0][1] = 3
    print(fields)
    csv_writer.writerows(fields)
    
# queries = form.get_query_list()['Queries']

# variable_list = queries[7]['format']['TABLE']['variables']
# json_variable_list_type = []
# with open("curr_database" + "/" + "table_name" + ".json", 'w') as json_table_file:
#     for i in range(len(variable_list)):
#         json_variable_list_type.append({"datatype": variable_list[i]['datatype']}) #keeps track of the data types for each column(field) of the table
#     json.dump(json_variable_list_type, json_table_file, indent = 4)

# with open("curr_database" + "/" + "table_name" + ".csv", 'w') as csv_table_file: #Create the table as a csv file
#     csv_writer = csv.writer(csv_table_file)
#     fields = []
#     for i in range(len(variable_list)): #loop through variable list in query
#         fields.append(variable_list[i]['name'])
#     csv_writer.writerow(fields)