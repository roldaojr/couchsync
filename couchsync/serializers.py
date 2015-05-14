from rest_framework import serializers


## for doc view
def modelserializer_factory(model_class):
    if not getattr(model_class, '_default_serializer', None):
        className = '{0}Serializer'.format(model_class._meta.object_name)
        meta = type('Meta', (), {'model': model_class})
        model_serializer = type(className,
                                (serializers.ModelSerializer,),
                                {'Meta': meta})
        model_class._default_serializer = model_serializer
    return model_class._default_serializer


class SingleDocSerializer(serializers.Serializer):
    _id = serializers.CharField(source='docid')
    _rev = serializers.CharField(source='id')
    _type = serializers.CharField(source='content_type')
    _deleted = serializers.BooleanField(source='deleted', required=False)

    def to_representation(self, obj):
        data = super(SingleDocSerializer, self).to_representation(obj)

        if not obj.deleted:
            data_obj = obj.object
            type_obj = type(obj.object)
            type_serializer = modelserializer_factory(type_obj)
            data.update(type_serializer(data_obj).data)

        return data


## Database info view
class DatabaseInfoSerializer(serializers.Serializer):
    compact_running = serializers.BooleanField()
    db_name = serializers.CharField()
    doc_count = serializers.IntegerField()
    update_seq = serializers.IntegerField()


## For _bulk_docs and _all_docs view
class BulkDocsRowValueSerializer(serializers.Serializer):
    rev = serializers.CharField()
    deleted = serializers.BooleanField(required=False)


class BulkDocsRowSerializer(serializers.Serializer):
    id = serializers.CharField(source='docid')
    key = serializers.CharField(source='docid')
    value = BulkDocsRowValueSerializer()
    doc = SingleDocSerializer(required=False)

    def __init__(self, *args, **kwargs):
        self.include_docs = kwargs.pop('include_docs', False)
        super(BulkDocsRowSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, obj):
        obj.value = {'rev': obj.id}
        if obj.deleted:
            obj.value['deleted'] = True

        if self.include_docs:
            obj.doc = obj

        return super(BulkDocsRowSerializer, self).to_representation(obj)


class BulkDocsSerializer(serializers.Serializer):
    rows = BulkDocsRowSerializer(many=True)
    offset = serializers.IntegerField()
    total = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        self.include_docs = kwargs.pop('include_docs', False)
        super(BulkDocsSerializer, self).__init__(*args, **kwargs)

    def to_representation(self, obj):
        return {
            'offset': 0,
            'total': len(obj),
            'rows': BulkDocsRowSerializer(
                obj, many=True, include_docs=self.include_docs).data
        }


class BulkDocsRequestSerializer(serializers.Serializer):
    keys = serializers.ListField(child=serializers.CharField(), required=False)
    docs = SingleDocSerializer(many=True, required=False)


## For Revisions feed view
class RevisionSerializer(serializers.Serializer):
    rev = serializers.CharField()


class RevisionSerializer(serializers.Serializer):
    seq = serializers.IntegerField()
    id = serializers.CharField(source='docid')
    deleted = serializers.BooleanField()
    revisions = RevisionSerializer(many=True)

    def to_representation(self, obj):
        obj.revisions = [{'rev': obj.id}]
        return super(RevisionSerializer, self).to_representation(obj)


class ChangesFeedSerializer(serializers.Serializer):
    results = RevisionSerializer(many=True)
    last_seq = serializers.IntegerField()



## for _revs_diff view
