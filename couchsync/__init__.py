from .models import Revision, registered_models
from django.core.signals import Signal
from django.db.models.signals import post_save, post_delete


def save_document_handler(sender, **kwargs):
    if sender != Revision and not kwargs.get('raw', False):
        instance = kwargs.get('instance')
        if getattr(instance, 'new_edits', True):
            Revision(object=instance).save()


def delete_document_handler(sender, **kwargs):
    if sender != Revision:
        instance = kwargs.get('instance')
        Revision(object=instance, delete=True).save()


def register(model):
    if model not in registered_models:
        Signal.connect(post_save, save_document_handler, sender=model,
                       dispatch_uid='couchsync.save')
        Signal.connect(post_delete, delete_document_handler, sender=model,
                       dispatch_uid='couchsync.delete')
        registered_models.append(model)
