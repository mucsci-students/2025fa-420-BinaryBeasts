import json  

# Loads a config file and returns it as a dict
# Any exceptions will be caught in main
def load_config(config_file: str)->dict:         
    # Open config file
    with open(config_file, 'r') as file:        
        # Convert JSON to a dict                 
        return json.load(file)
