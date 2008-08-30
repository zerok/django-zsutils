from django.db import models

class GFKManager(models.Manager):
    """
    A simple manager that offers the usual stuff as well as a new method 
    ``relate``, that limits the number of required queries for generic
    relationships.
    """
    def __init__(self, *args, **kwargs):
        if 'content_type_field' in kwargs.keys():
            self._content_type_field = kwargs['content_type_field']
            del kwargs['content_type_field']
        else:
            self._content_type_field = 'content_type'

        if 'content_object_field' in kwargs.keys():
            self._content_object_field = kwargs['content_object_field']
            del kwargs['content_object_field']
        else:
            self._content_object_field = 'content_object'

        if 'object_id_field' in kwargs.keys():
            self._object_id_field = kwargs['object_id_field']
            del kwargs['object_id_field']
        else:
            self._object_id_field = 'object_id'

        super(GFKManager, self).__init__(*args, **kwargs)

    def relate(self, qs):
        """
        Queries for all distinct content types in the resultset all
        relevant objects and binds them to the original resultset.
        Ideally this should minimize the number of queries required
        for resultsets of n objects of m distinct content types 
        including GenericForeignKeys from 1+n queries to 1+m (or 
        if the content types haven't been cached yet 1+2m) which 
        in most cases should be lower than 1+n.

        Usage::
            
            items = GenericItem.objects.select_related('content_type').all()
            items = GenericItem.objects.relate(items)
            
        When fetching the items, only select the related content types,
        since otherwise you will end up with one extra query for each
        item.

        You can find more details on:
        <http://zerokspot.com/weblog/2008/08/13/genericforeignkeys-with-less-queries/>
        """
        model_map = {}
        item_map = {}
        for item in qs:
            object_id = getattr(item, self._object_id_field)
            content_type = getattr(item, self._content_type_field)
            model_map.setdefault(content_type, {}) \
                [object_id] = item.id
            item_map[item.id] = item
        for ct, items_ in model_map.items():
            for o in ct.model_class().objects.select_related() \
                    .filter(id__in=items_.keys()).all():
                setattr(item_map[items_[o.id]],self._content_object_field, o)
        return qs

