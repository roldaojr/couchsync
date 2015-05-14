import itertools
from django.db.models import Max
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (RevisionSerializer, ChangesFeedSerializer,
                          SingleDocSerializer, BulkDocsSerializer,
                          BulkDocsRequestSerializer,
                          DatabaseInfoSerializer)
from .models import Revision, doc_count, last_seq


class DatabaseInfoView(APIView):
    def get(self, request, *args, **kwargs):
        info = {
            'compact_running': False,
            'db_name': 'django',
            'doc_count': doc_count(),
            'update_seq': last_seq(),
        }
        return Response(DatabaseInfoSerializer(info).data)


class ReplicationLogView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({
            '_id': '_local/b3e44b920ee2951cb2e123b63044427a',
            '_rev': '0-8',
            'history': [
                {
                    'doc_write_failures': 0,
                    'docs_read': 2,
                    'docs_written': 2,
                    'end_last_seq': 5,
                    'end_time': "Thu, 10 Oct 2013 05:56:38 GMT",
                    'missing_checked': 2,
                    'missing_found': 2,
                    'recorded_seq': 5,
                    'session_id': "d5a34cbbdafa70e0db5cb57d02a6b955",
                    'start_last_seq': 3,
                    'start_time': "Thu, 10 Oct 2013 05:56:38 GMT"
                }
            ],
            'replication_id_version': 3,
            'session_id': "d5a34cbbdafa70e0db5cb57d02a6b955",
            'source_last_seq': 5
        })


class ChangesFeedView(APIView):
    def get(self, request, *args, **kwargs):
        last_revisions = Revision.objects.values('docid').annotate(
            max=Max('change_seq')).values_list('max', flat=True)
        revisions = Revision.objects.filter(
            change_seq__in=last_revisions).order_by('change_seq')
        feed = {'results': revisions, 'last_seq': last_seq()}
        return Response(ChangesFeedSerializer(feed).data)


class RevisionDiffView(APIView):
    def post(self, request, *args, **kwargs):
        if isinstance(request.DATA, dict):
            revs = list(itertools.chain(*dict(request.DATA).values()))
            existing_revs = Revision.objects.filter(
                id__in=revs).values_list('id', flat=True)
            missing_revs = {}
            for d, r in dict(request.DATA).items():
                missing_revs[d] = {
                    'missing': [x for x in r if x not in existing_revs]
                }
            return Response(missing_revs)
        else:
            return Response([])


class SingleDocView(APIView):
    def get(self, request, *args, **kwargs):
        docid = kwargs.get('docid')
        revision = Revision.objects.filter(
            docid=docid).order_by('-seq').first()
        return Response(SingleDocSerializer(revision).data)


class BulkDocsView(APIView):
    def post(self, request, *args, **kwargs):
        include_docs = request.GET.get('include_docs', '').lower() == 'true'
        serializer = BulkDocsRequestSerializer(data=dict(request.DATA))
        if(serializer.is_valid()):
            docids = serializer.data['keys']
            seqs = Revision.objects.filter(
                docid__in=docids).values('docid').annotate(
                max=Max('change_seq')).values_list('max', flat=True)
            revisions = Revision.objects.filter(change_seq__in=seqs)
            return Response(BulkDocsSerializer(
                revisions, include_docs=include_docs).data)


class AllDocsView(APIView):
    def get(self, request, *args, **kwargs):
        if request.GET.get('include_docs', '').lower() == 'true':
            include_docs = True
        else:
            include_docs = False

        seqs = Revision.objects.values('docid').annotate(
            max=Max('change_seq')).values_list('max', flat=True)
        revisions = Revision.objects.filter(seq__in=seqs)
        return Response(BulkDocsSerializer(
            revisions, include_docs=include_docs).data)
