import format as form
import csv
import sys
import json
import shutil
import os

if len(sys.argv) == 2: #pass in the file name as cmd line argument
    file_name = sys.argv[1]

curr_database = None #the current database in use
command_list = form.format_command(file_name)#create command list from SQL file
form.format_json(command_list,'data/query_list.json') #create list of all queries in json format
queries = form.get_query_list()['Queries'] #all queries ordered in a list

for i in range(len(queries)): #loop through all queries
    match queries[i]['type']: 
        case 'CREATE':
            if queries[i]['request'] == 'DATABASE': #creating a database
                db_name = queries[i]['format']['DATABASE']['name']
                if os.path.isdir(db_name): #check if the database we want to create already exists
                    print(f"!Failed to create database {queries[i]['format']['DATABASE']['name']} because it already exists.")
                else:
                    os.mkdir(db_name)
                    print(f"Database {db_name} created.")
            elif queries[i]['request'] == 'TABLE': #creating a table
                table_name = queries[i]['format']['TABLE']['name']
                if curr_database == None:
                    print("!Failed to create table, no database selected.")
                elif not curr_database == None:
                    if os.path.isfile(curr_database + "/" + table_name + ".csv"):
                        print(f"!Failed to create table {table_name} because it already exists.")
                    else:
                        variable_list = queries[i]['format']['TABLE']['variables']
                        json_variable_list_type = []
                        with open(curr_database + "/" + table_name + ".json", 'w') as json_table_file:
                            for i in range(len(variable_list)):
                                json_variable_list_type.append({"datatype": variable_list[i]['datatype']}) #keeps track of the data types for each column(field) of the table
                            json.dump(json_variable_list_type, json_table_file, indent=4)

                        with open(curr_database + "/" + table_name + ".csv", 'w') as csv_table_file: #Create the table as a csv file
                            csv_writer = csv.writer(csv_table_file)
                            fields = []
                            for i in range(len(variable_list)): #loop through variable list in query
                                fields.append(variable_list[i]['name'])
                            csv_writer.writerow(fields)
                        print(f"Table {table_name} created.")
        case 'DROP':
            if queries[i]['request'] == 'DATABASE':
                db_name = queries[i]['name']
                if not os.path.isdir(db_name):
                    print(f"!Failed to delete {db_name} because it does not exist.")
                else:
                    shutil.rmtree(db_name)
                    print(f"Database {db_name} deleted.")
            elif queries[i]['request'] == 'TABLE':
                table_name = queries[i]['name']
                if not os.path.isfile(curr_database + "/" + table_name + ".csv"):
                    print(f"!Failed to delete {table_name} because it does not exist.")
                else:
                    os.remove(curr_database + "/" + table_name + ".csv")
                    print(f"Table {table_name} deleted.")

        case 'USE':
            db_name = queries[i]['name']

            if not os.path.isdir(db_name):
                print(f"!Failed to select database {db_name} because it does not exist.")
            else:
                curr_database = db_name
                print(f"Using database {db_name}.")
        case 'SELECT':
            table_name = queries[i]['tableName']
            selectAll = queries[i]['allColumns']

            if curr_database == None:
                print("!Failed to select columns, no database selected.")
            else:
                if not os.path.isfile(curr_database + "/" + table_name + ".csv"): #does the table exist?
                    print(f"!Failed to query table {table_name} because it does not exist.")
                else:
                    if selectAll:
                        with open(curr_database + "/" + table_name + ".csv", 'r') as csv_table_file:
                            csv_reader = csv.reader(csv_table_file)
                            fields = next(csv_reader) #read in field names and store as a list
                        with open(curr_database + "/" + table_name + ".json", 'r') as json_table_file: #open table's json file to view field's datatypes
                            datatype_list = json.load(json_table_file) #load the field's corresponding datatypes into a list
                            for i in range(len(fields)):
                                if not i == (len(fields) - 1): #this makes sure that a | does not print after the last field
                                    print(f"{fields[i]} {datatype_list[i]['datatype']} | ", end='') #match the field with its datatype
                                else:
                                    print(f"{fields[i]} {datatype_list[i]['datatype']}")
                    # else: #if we are choosing specific columns instead.
        case 'ALTER TABLE':
            table_name = queries[i]['format']['ADD']['name']

            if curr_database == None:
                print("!Failed to alter table, no database selected.")
            else:
                if not os.path.isfile(curr_database + "/" + table_name + ".csv"): #does the table exist?
                    print(f"!Failed to alter table {table_name} because it does not exist.")
                else: #adding more fields to table
                    with open(curr_database + "/" + table_name + ".json", 'r') as json_table_file:
                        variable_list = json.load(json_table_file)
                    with open(curr_database + "/" + table_name + ".csv", 'r') as csv_table_file:
                        csv_reader = csv.reader(csv_table_file)
                        rows = list(csv_reader) 
                        rows[0].append(queries[i]['format']['ADD']['variables'][0]['name']) #add the new variable to the end of the field list
                    with open(curr_database + "/" + table_name + ".csv", 'w') as csv_table_file:
                        csv_writer = csv.writer(csv_table_file)
                        csv_writer.writerows(rows) #write back all the data to the csv.
                    with open(curr_database + "/" + table_name + ".json", 'w') as json_table_file:
                        variable_list.append({"datatype": queries[i]['format']['ADD']['variables'][0]['datatype']})
                        json.dump(variable_list, json_table_file, indent=4)
                    print(f"Table {table_name} modified.")
        case 'EXIT':
            print("\nprogram termination")