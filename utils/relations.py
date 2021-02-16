from functools import reduce

from rest_framework.fields import HiddenField
from rest_framework_nested.relations import NestedHyperlinkedIdentityField


class AdvNestedHyperlinkedIdentityField(NestedHyperlinkedIdentityField):
    def get_url(self, obj, view_name, request, format):
        """
        NestedHyperlinkedIdentityField that allows null lookup_field.
        It simplifies creation of OneToOne relation hyper-links, where only parent's kwargs are passed.
        """
        if hasattr(obj, 'pk') and obj.pk in (None, ''):
            return None

        if self.lookup_field:
            # default lookup from rest_framework.relations.HyperlinkedRelatedField
            lookup_value = getattr(obj, self.lookup_field)
            kwargs = {self.lookup_url_kwarg: lookup_value}
        else:
            kwargs = {}

        # multi-level lookup
        for parent_lookup_kwarg in list(self.parent_lookup_kwargs.keys()):
            underscored_lookup = self.parent_lookup_kwargs[parent_lookup_kwarg]

            # split each lookup by their __, e.g. "parent__pk" will be split into "parent" and "pk", or
            # "parent__super__pk" would be split into "parent", "super" and "pk"
            lookups = underscored_lookup.split('__')

            # use the Django ORM to lookup this value, e.g., obj.parent.pk
            lookup_value = reduce(getattr, [obj] + lookups)

            # store the lookup_name and value in kwargs, which is later passed to the reverse method
            kwargs.update({parent_lookup_kwarg: lookup_value})

        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)


class ParentHiddenRelatedField(HiddenField):
    """
    GetParentHiddenField - Hidden Field that returns parent object pointed with URL or passed with serializer's data
    params: queryset - queryset to find instance with
    params: parent_lookup_kwargs - parent's lookup URL kwargs names (keys) and fields (values)
    return: model instance
    """
    def __init__(self, queryset, parent_lookup_kwargs, **kwargs):
        self.queryset = queryset
        self.parent_lookup_kwargs = parent_lookup_kwargs
        kwargs['write_only'] = True
        kwargs['default'] = None
        super().__init__(**kwargs)

    def get_value(self, dictionary):
        # in case of bulk data sent return instance hidden under field's name
        # instance needs to be set up in parent's create/update methods
        if dictionary.get(self.field_name) and (dictionary.get(self.field_name) in self.queryset):
            return dictionary.get(self.field_name)
        # update data forwarded to the to_internal_value() method
        filter_kwargs = {}
        for key, value in self.parent_lookup_kwargs.items():
            # get slug from URL resolver - needs to match parent_lookup_kwargs's names!
            if self.context.get('request'):
                filter_kwargs[value] = self.context.get('request').resolver_match.kwargs.get(key)
        return self.queryset.filter(**filter_kwargs).first()

    def to_internal_value(self, data):
        # return model's instance, no conversion needed
        return data
