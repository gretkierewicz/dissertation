import random
import string


def random_str(k):
    return ''.join(random.choices(string.ascii_letters, k=k))


def random_max_len_field_str(model, field_name):
    return ''.join(random.choices(string.ascii_letters, k=getattr(model._meta.get_field(field_name), 'max_length')))


def random_bool():
    return random.choice([True, False])
