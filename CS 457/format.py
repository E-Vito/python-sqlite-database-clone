import json
import re

def format_command(file_name): 
    """This function takes an SQL file and tokenizes each query into a list

    Args:
        file_name (.sql): A SQL file with 

    Returns:
        list: a list of tokenized SQL queries, each index representing one query
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
    with open("data/query formats/use_query.json", "r") as f: #open default create json to format new input
        data = json.load(f)
    
    data['name'] = token_list[1]

    return data

def format_alter_query(token_list):
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
    with open("data/query formats/select_query.json", "r") as f:
        data = json.load(f)
    
    if token_list[1] == '*':
        data['allColumns'] = True
    data['tableName'] = token_list[token_list.index('FROM') + 1] #the word after FROM is the table to select from

    return data
    
def get_query_list():
    with open("data/query_list.json", "r") as f:
        return json.load(f) 