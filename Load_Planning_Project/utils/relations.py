from functools import reduce

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