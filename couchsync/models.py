from uuid import uuid4
from hashlib import md5
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

_database_last_seq = None
_database_doc_count = None
registered_models = []


class Revision(models.Model):
    change_seq = models.AutoField(primary_key=True)
    id = models.CharField(max_length=64, unique=True)
    seq = models.BigIntegerField()
    prev = models.CharField(max_length=64, null=True)
    docid = models.CharField(max_length=64)
    deleted = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.CharField(max_length=64, null=True)
    object = GenericForeignKey()

    def save(self, *args, **kwargs):
        # set docid
        self.docid = md5('{0}.{1}.{2}'.format(
            self.content_type.app_label,
            self.content_type.model,
            self.object_id
        )).hexdigest()
        # find previous revision
        revisions = type(self).objects.filter(docid=self.docid).order_by('-seq')
        if revisions.count() > 0:
            revision = revisions.first()
            self.prev = revision.id
            self.seq = revision.seq+1
        else:
            self.prev = None
            self.seq = 1

        self.id = uuid4().hex
        super(Revision, self).save(*args, **kwargs)

    @classmethod
    def get_last(cls, docid):
        last_seq = cls.objects.filter(
            docid=docid).aggregate(last=models.Max('seq'))['last']
        return cls.objects.get(seq=last_seq)


@receiver(post_save, sender=Revision)
def change_post_save(sender, **kwargs):
    global _database_last_seq, _database_doc_count
    _database_last_seq = None
    _database_doc_count = None


def last_seq():
    global _database_last_seq
    if not _database_last_seq:
        _database_last_seq = Revision.objects.aggregate(max=models.Max('seq'))['max']
    return _database_last_seq


def doc_count():
    global _database_doc_count
    if not _database_doc_count:
        _database_doc_count = Revision.objects.count()
    return _database_doc_count
