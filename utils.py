import os
import ast
import configparser

path = os.path.dirname(os.path.abspath(__file__))
program_config_path = os.path.join(path, 'conf/program.ini')

def get_config_values(section, option):

    config = configparser.ConfigParser()
    config.read(program_config_path)

    value = config.get(section=section, option=option)

    if '{' in value:
        return ast.literal_eval(value)
    elif '[' in value:
        return ast.literal_eval(value)
    else:
        return value
