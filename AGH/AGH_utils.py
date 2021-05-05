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
                for item in json.load(json_file).get('additional hours factors') if item.get('factor ID')
            ]
        except IndexError:
            return None


class AdditionalHoursFactorData:
    def __init__(self, factor_ID):
        base_path = os.path.dirname(__file__)
        with open(os.path.join(base_path, "data/additional_hours_factors.json"), 'r', encoding='utf8') as json_file:
            self.__json_data = json.load(json_file)
        factors = self.__json_data.get('additional hours factors')
        groups = self.__json_data.get('groups')
        factor_data = next((item for item in factors if item.get("factor ID") == factor_ID), None)

        self.factor_ID = factor_ID
        self.group_ID = factor_data.get('group ID')

        group = next((item for item in groups if item.get("group ID") == self.group_ID), None)

        self.limit_key_name = next(item for item in factor_data.keys() if item.startswith('limit per '))
        self.limit_per_unit = factor_data.get(self.limit_key_name)
        self.max_amount_for_group = group['limit per year'] if group else None
        self.is_counted_into_limit = factor_data.get('is counted into limit', True)


def __get_factor_value(factor_name, sector_name='major factors'):
    base_path = os.path.dirname(__file__)
    with open(
            os.path.join(base_path, "data/additional_hours_factors.json"), 'r', encoding='utf8'
    ) as json_file:
        return next((
            item.get('value') for item in json.load(json_file).get(sector_name) if item.get('factor ID') == factor_name
        ), None)


def get_major_factors_value(name):
    return __get_factor_value(name)


def get_job_time_hours_limit(name):
    return __get_factor_value(name, sector_name="job-time hours limits")


class ExamsFactors:
    factor_for_written_exam = factor_for_oral_exam = min_students_number = max_summary_hours = 0
    __base_path = os.path.dirname(__file__)
    with open(
            os.path.join(__base_path, "data/additional_hours_factors.json"), 'r', encoding='utf8'
    ) as __json_file:
        __data = json.load(__json_file).get('exams')
        for __rec in __data:
            if __rec.get('factor ID') == 'k':
                factor_for_written_exam = __rec.get('value for written')
                factor_for_oral_exam = __rec.get('value for oral')
            if __rec.get('factor ID') == 'N_min':
                min_students_number = __rec.get('value')
            if __rec.get('factor ID') == 'sum_max':
                max_summary_hours = __rec.get('limit per year')
