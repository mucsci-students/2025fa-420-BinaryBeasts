import json

#saves a config file
def save_config_file(file_path: str, data):
    
    #open file
    with open(file_path, 'w') as file:
    #wrties to the file
        json.dump(data, file)
