from random import randint
from rest_framework.test import APITestCase
from couchsync.models import Revision
from couchsync.serializers import (ChangesFeedSerializer, BulkDocsSerializer,
                                   SingleDocSerializer,
                                   BulkDocsRequestSerializer,
                                   DatabaseInfoSerializer)
from demo.app.models import Note


class ApiTest(APITestCase):
    def setUp(self):
        n = Note(title='New Note', content='new content')
        n.save()
        n.title = 'New title'
        n.save()
        Note(title='Another Note', content='another content').save()
        n.content = 'another edit'
        n.save()
        Note(title='Yet Another Note', content='yet another content').save()
        n.content = 'yet another edit'
        n.save()
        n = Note(title='New Note', content='new note')
        n.save()
        n.title = 'New title'
        n.save()

    def test_database_info(self):
        response = self.client.get('/couchsync/')
        serializer = DatabaseInfoSerializer(data=response.data)
        self.assertTrue(serializer.is_valid())

    def test_all_docs(self):
        response = self.client.get('/couchsync/_all_docs')
        serializer = BulkDocsSerializer(data=response.data)
        self.assertTrue(serializer.is_valid())

    def test_all_docs_include(self):
        response = self.client.get('/couchsync/_all_docs?include_docs=true')
        serializer = BulkDocsSerializer(data=response.data)
        self.assertTrue(serializer.is_valid())

    def test_changes_feed(self):
        response = self.client.get('/couchsync/_changes')
        serializer = ChangesFeedSerializer(data=response.data)
        self.assertTrue(serializer.is_valid())

    def test_single_doc(self):
        index = randint(0, Revision.objects.count() - 1)
        docid = Revision.objects.all()[index].docid
        response = self.client.get('/couchsync/{0}'.format(docid))
        serializer = SingleDocSerializer(data=response.data)
        self.assertTrue(serializer.is_valid())

    def test_bulk_docs(self):
        all_docs = Revision.objects.all().order_by('-seq')
        docs = [all_docs[0].docid, all_docs[1].docid]
        request = {'keys': docs}
        response = self.client.post('/couchsync/_bulk_docs', request)
        serializer = BulkDocsSerializer(data=response.data)
        self.assertTrue(serializer.is_valid())

    def test_bulk_docs_include_docs(self):
        all_docs = Revision.objects.all().order_by('-seq')
        docs = [all_docs[0].docid, all_docs[4].docid]
        request = {'keys': docs}
        response = self.client.post('/couchsync/_bulk_docs?include_docs=true',
                                    request)
        serializer = BulkDocsSerializer(data=response.data)
        self.assertTrue(serializer.is_valid())

    def test_revs_diff(self):
        index = randint(0, Revision.objects.count() - 1)
        revision = Revision.objects.all()[index]
        request = {
            revision.docid: ['6-123', revision.id]
        }
        response = self.client.post('/couchsync/_revs_diff', request)
        self.assertEqual(response.data[revision.docid]['missing'], ['6-123'])
