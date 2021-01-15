from rest_framework.fields import SerializerMethodField, HiddenField


def conv_pk_to_str(obj, key_to_model_dict):
    """
    conv_pk_to_str function: converts obj's given values from pk repr to string
    params:
    obj - dictionary of elements: key: pk or list of pks
    key_to_model_dict - dictionary of elements: key: model for pks to search for
    returns: modified obj
    """
    if obj and key_to_model_dict:
        for key, model in key_to_model_dict.items():
            if hasattr(obj[key], '__iter__'):
                obj[key] = [model.objects.get(pk=pk).__str__() for pk in obj[key]]
            else:
                obj[key] = model.objects.get(pk=obj[key]).__str__()
    return obj


class ParentFromURLHiddenField(HiddenField):
    """
    ParentFromURLHiddenField - Hidden Field that doesn't take value from user, but returns parent object
    It will create filter kwargs with help of provided dictionary (matches) and resolved URL's matches.
    Be sure that parent lookup kwarg's names match the ones configured with serializer and view.
    If you give more matches, all will be considered as filter kwargs.
    params:
    queryset - object to be filtered
    matches - dictionary of parent's lookup kwarg's names (keys) and field's names (values)
    returns: - object filtered from the queryset (first occurrence - filtering should return one object anyway!)
    """
    def __init__(self, queryset, matches, **kwargs):
        self.queryset = queryset
        self.matches = matches
        kwargs['write_only'] = True
        kwargs['default'] = None
        super().__init__(**kwargs)

    def get_value(self, dictionary):
        # change data forwarded to the to_internal_value()
        filter_kwargs = {}
        for key, value in self.matches.items():
            # getting slug from URL resolver - needs to match parent_lookup_kwarg's names!
            filter_kwargs[value] = self.context.get('request').resolver_match.kwargs[key]
        return self.queryset.filter(**filter_kwargs).first()

    def to_internal_value(self, data):
        # return model's instance, no conversion needed
        return data


class SerializerLambdaField(SerializerMethodField):
    """
    SerializerLambdaField - Custom Serializer Method Field
    Allows use of lambda function as parameter
    """
    def bind(self, field_name, parent):
        super(SerializerMethodField, self).bind(field_name, parent)

    def to_representation(self, data):
        return self.method_name(data)
