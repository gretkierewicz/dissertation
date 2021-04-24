# Based on the 'Regulamin Pracy' (08/03/2021)
# https://www.cok.agh.edu.pl/fileadmin/_migrated/COK/DUSOS/pliki_pensum_akty_prawne/Regulamin_PRACY_tj..pdf

import json
import os

# pensum groups
badawczo_dydaktyczna = 'badawczo-dydaktyczna'
dydaktyczna = 'dydaktyczna'


def get_pensum(position, group=dydaktyczna):
    """
    get_pensum function to read pensum value of Group-Position pair based on JSON data:
    data/PensumThresholds_BadawczoDydaktyczna.json and data/PensumThresholds_Dydaktyczna.json files
    position: name of employee's position
    group: (optional, def='dydaktyczna')) name of pensum group
    return: pensum value if position-group mathup is found in JSON data, None otherwise
    """
    base_path = os.path.dirname(__file__)
    with open(
            os.path.join(base_path, "data/PensumThresholds_BadawczoDydaktyczna.json"), 'r', encoding='utf8'
    ) as json_file:
        for item in json.load(json_file):
            if (position.lower() in [x.lower() for x in item.get('positions')]) and (group == badawczo_dydaktyczna):
                return item.get('value')
    with open(
            os.path.join(base_path, "data/PensumThresholds_Dydaktyczna.json"), 'r', encoding='utf8'
    ) as json_file:
        for item in json.load(json_file):
            if (position.lower() in [x.lower() for x in item.get('positions')]) and (group == dydaktyczna):
                return item.get('value')


def get_pensum_function_names():
    """
    get_pensum_function_names lists all names of employee's functions based on JSON data:
    data/PensumReduction.json file
    """
    base_path = os.path.dirname(__file__)
    with open(
            os.path.join(base_path, "data/PensumReduction.json"), 'r', encoding='utf8'
    ) as json_file:
        return [item.get('function') for item in json.load(json_file)]


def get_pensum_reduction_value(function):
    """
    get_pensum_reduction_value returns pensum reduction for given function name based on JSON data:
    data/PensumReduction.json file
    """
    base_path = os.path.dirname(__file__)
    with open(
            os.path.join(base_path, "data/PensumReduction.json"), 'r', encoding='utf8'
    ) as json_file:
        try:
            return [item.get('value') for item in json.load(json_file) if item.get('function') == function].pop()
        except IndexError:
            return None


def get_additional_hours_factors_choices():
    """
    get_additional_hours_factors_choices returns list of tuples (key, display_name), based on data in JSON file:
    data/additional_hours_factors.json
    """
    base_path = os.path.dirname(__file__)
    with open(
            os.path.join(base_path, "data/additional_hours_factors.json"), 'r', encoding='utf8'
    ) as json_file:
        try:
            return [
                (item.get('factor ID'), item.get('factor description'))
                for item in json.load(json_file).get('additional hours factors')
            ]
        except IndexError:
            return None
