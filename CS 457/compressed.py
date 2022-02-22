'''
Author: Ethan Vito
Date: 2/19/2022
'''

import csv
import sys
import json
import shutil
import os
import re
# if len(sys.argv) == 2: #pass in the file name as cmd line argument
#     file_name = sys.argv[1]

file_name = 'PA1_test.sql'

def format_command(file_name): 
    """This function takes an SQL file and tokenizes each query into a list

    Args:
        file_name (.sql): A SQL file with 

    Returns:
        command_list: a list of tokenized SQL queries, each index representing one query
    """
    command_list = []
    with open(file_name, "r") as f:
        for line in f: #iterate over each line in the file
            if(not line[:2] == '--' and not line == '\n'): #don't take in commented lines and newlines
                command_list.append(list(filter(None,re.split(', |\s|;+|\((.+)\)', line))))#add tokenized query as a single element in a list
    return command_list

def format_json(commands, file_name):
    """This functions writes out SQL queries to a JSON file

    Args:
        commands (list): a list of tokenized SQL queries, each index representing one query
        file_name (.json): A JSON file that will store each SQL query
    """
    query_json = { "Queries": []}
    for i in range(len(commands)):
        
        match commands[i][0]:
            case 'CREATE':
                query_json['Queries'].append(format_create_query(commands[i]))
            case 'DROP':
                query_json['Queries'].append(format_drop_query(commands[i]))
            case 'USE':
                query_json['Queries'].append(format_use_query(commands[i]))
            case 'ALTER':
                query_json['Queries'].append(format_alter_query(commands[i]))
            case 'SELECT':
                query_json['Queries'].append(format_select_query(commands[i]))  
            case '.EXIT':
                query_json['Queries'].append({"type": "EXIT"})
        
    with open(file_name, "w") as f:
        json.dump(query_json, f, indent=4)

def format_create_query(token_list): 
    """This function formats a SQL CREATE query into a JSON file

    Args:
        token_list (list): a list with a tokenized SQL query

    Returns:
        data: a dictionary with all the information about a CREATE DATABASE or CREATE TABLE query
    """
    if token_list[1] == 'DATABASE':
        with open("data/query formats/create_query.json", "r") as f: #open default create json to format new input
            data = json.load(f)

        data['request'] = 'DATABASE'
        data['format']['DATABASE']['name'] = token_list[2]

        return data

    elif token_list[1] == 'TABLE':
        with open("data/query formats/create_query.json", "r") as f:
            data = json.load(f)

        data['request'] = 'TABLE'
        data['format']['TABLE']['name'] = token_list[2]
        variable_list = list(filter(None,re.split(', |\s|;+', token_list[3])))
        
        var_index = 0
        while var_index < len(variable_list): #add all the variables to the query
            data['format']['TABLE']['variables'].append({"name": variable_list[var_index],
                                                                "datatype": variable_list[var_index + 1] })
            var_index += 2

        return data

def format_drop_query(token_list):
    """This function formats a SQL DROP query into a JSON file

    Args:
        token_list (list): a list with a tokenized SQL query

    Returns:
        data: a dictionary with all the information about a DROP query
    """
    if token_list[1] == 'DATABASE':
        with open("data/query formats/drop_query.json", "r") as f: #open default create json to format new input
            data = json.load(f)
        
        data['request'] = 'DATABASE'
        data['name'] = token_list[2]

        return data
    
    elif token_list[1] == 'TABLE':
        with open("data/query formats/drop_query.json", "r") as f: #open default create json to format new input
            data = json.load(f)

        data['request'] = 'TABLE'
        data['name'] = token_list[2]

        return data

def format_use_query(token_list):
    """This function formats a SQL USE query into a JSON file

    Args:
        token_list (list): a list with a tokenized SQL query

    Returns:
        data: a dictionary with all the information about a USE query
    """
    with open("data/query formats/use_query.json", "r") as f: #open default create json to format new input
        data = json.load(f)
    
    data['name'] = token_list[1]

    return data

def format_alter_query(token_list):
    """This function formats a SQL ALTER query into a JSON file

    Args:
        token_list (list): a list with a tokenized SQL query

    Returns:
        data: a dictionary with all the information about a ALTER query
    """
    with open("data/query formats/alter_query.json", "r") as f:
        data = json.load(f)

    data['request'] = 'TABLE'
    data['format']['ADD']['name'] = token_list[2]
    variable_list = token_list[4:] #new list with only variable names

    var_index = 0
    while var_index < len(variable_list): #add all the variables to the query
        data['format']['ADD']['variables'].append({"name": variable_list[var_index],
                                                            "datatype": variable_list[var_index + 1] })
        var_index += 2

    return data

def format_select_query(token_list):
    """This function formats a SQL SELECT query into a JSON file

    Args:
        token_list (list): a list with a tokenized SQL query

    Returns:
        data: a dictionary with all the information about a SELECT query
    """
    with open("data/query formats/select_query.json", "r") as f:
        data = json.load(f)
    
    if token_list[1] == '*':
        data['allColumns'] = True
    data['tableName'] = token_list[token_list.index('FROM') + 1] #the word after FROM is the table to select from

    return data
    
def get_query_list():
    """This function takes all the SQL queries that have been formatted into a json and loads converts them into an equivalent python data structure

    Returns:
        json.load(f): the sql query converted from JSON into python equivalent data
    """
    with open("data/query_list.json", "r") as f:
        return json.load(f)

curr_database = None #the current database in use
command_list = format_command(file_name)#create command list from SQL file
format_json(command_list,'data/query_list.json') #create list of all queries in json format
queries = get_query_list()['Queries'] #all queries ordered in a list

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
                if not os.path.isdir(db_name):#check if the database exists as a directory
                    print(f"!Failed to delete {db_name} because it does not exist.")
                else:
                    shutil.rmtree(db_name)#this command removes a directory and all the files within it
                    print(f"Database {db_name} deleted.")
            elif queries[i]['request'] == 'TABLE':
                table_name = queries[i]['name']
                if not os.path.isfile(curr_database + "/" + table_name + ".csv"):
                    print(f"!Failed to delete {table_name} because it does not exist.")
                else:
                    os.remove(curr_database + "/" + table_name + ".csv")
                    os.remove(curr_database + "/" + table_name + ".json")
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
                        rows = list(csv_reader) #read in all the rows from the csv and convert to a list.
                        rows[0].append(queries[i]['format']['ADD']['variables'][0]['name']) #add the new variable to the end of the field list
                    with open(curr_database + "/" + table_name + ".csv", 'w') as csv_table_file:
                        csv_writer = csv.writer(csv_table_file)
                        csv_writer.writerows(rows) #write back all the data to the csv.
                    with open(curr_database + "/" + table_name + ".json", 'w') as json_table_file:
                        variable_list.append({"datatype": queries[i]['format']['ADD']['variables'][0]['datatype']}) #this will write the fields corresponding datatypes into a dictionary.
                        json.dump(variable_list, json_table_file, indent=4)
                    print(f"Table {table_name} modified.")
        case 'EXIT':
            print("\nprogram termination")


