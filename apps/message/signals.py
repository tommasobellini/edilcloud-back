# -*- coding: utf-8 -*-

import os

import filetype
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from . import models as message_models
from apps.profile import models as profile_models
from apps.notify import models as notify_models
from web.core.middleware.thread_local import get_current_profile, get_current_request
from web.core.utils import get_html_message, get_bell_notification_status, get_email_notification_status
from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
from websocket import create_connection

from .models import MessageFileAssignment

def get_filetype(file):
    kind = filetype.guess(file)
    if kind is None:
        return
    return kind.mime

def get_files(obj):
    media_list = []
    request = get_current_request()
    medias = MessageFileAssignment.objects.filter(message=obj)
    for media in medias:
        try:
            photo_url = media.media.url
            protocol = request.is_secure()
            if protocol:
                protocol = 'https://'
            else:
                protocol = 'http://'
            host = request.get_host()
            media_url = protocol + host + photo_url
        except:
            media_url = None
        name, extension = os.path.splitext(media.media.name)
        if extension == '.wav':
            type = 'audio/wav'
        else:
            type = get_filetype(media.media)
        media_list.append(
            {
                "media_url": media_url,
                "id": media.id,
                "size": media.media.size,
                "name": name.split('/')[-1],
                "extension": extension,
                "type": type,
                "message": media.message.id
            }
        )
    return media_list


@receiver([post_save, post_delete], sender=message_models.Message)
def message_notification(sender, instance, **kwargs):
    company_staff = []
    profile = get_current_profile()
    # If there is no JWT token in the request,
    # then we don't create notifications (Useful at admin & shell for debugging)
    if not profile or instance.status == 0:
        return

    try:
        endpoint = os.path.join(settings.PROTOCOL+'://', settings.BASE_URL, 'comunica')
        if instance.talk.content_type.name == 'company':
            company_staff = instance.talk.content_object.profiles.all()
            title = instance.talk.content_type.name
            source = instance.talk.content_object.name
        elif instance.talk.content_type.name == 'project':
            endpoint = os.path.join(settings.PROTOCOL+'://', settings.BASE_URL, 'project')
            title = instance.talk.content_type.name
            company_staff = instance.talk.content_object.profiles.all().union(
                instance.talk.content_object.company.get_owners_and_delegates(),
                instance.sender.company.get_owners_and_delegates()
            )
            all_staff = instance.talk.content_object.internal_projects.all().values_list('profiles', flat=True)
            if all_staff:
                company_staff = company_staff.union(profile_models.Profile.objects.filter(id__in=all_staff))
            source = instance.talk.content_object.name
        elif instance.talk.content_type.name == 'profile':
            company_staff = [instance.talk.content_object]
            title = 'staff'
            source = instance.sender.last_name

        content = "Mr <strong>%s %s</strong> have created this event. " % (profile.first_name, profile.last_name)

        if 'created' in kwargs:
            if kwargs['created']:
                subject = _('New Message from %s (%s)' % (title, source))
            else:
                subject = _('Message updated by %s (%s)' % (title, source))
        else:
            subject = _('Message deleted by %s (%s)' % (title, source))

        final_content = "For simplicity, the following button will redirect to the target page."
        body = get_html_message(content, final_content, endpoint)
        type = ContentType.objects.get(model=instance.talk.content_type.name.lower())

        notify_obj = notify_models.Notify.objects.create(
            sender=profile, subject=subject, body=body,
            content_type=type, object_id=instance.talk.object_id,
            creator=profile.user, last_modifier=profile.user
        )

        recipient_objs = []

        for staff in company_staff:
            bell_status = get_bell_notification_status(
                staff, instance.talk.content_type.name
            )
            email_status = get_email_notification_status(
                staff, instance.talk.content_type.name
            )

            if bell_status or email_status:
                recipient_objs.append(notify_models.NotificationRecipient(
                    notification=notify_obj, is_email=email_status,
                    is_notify=bell_status, recipient=staff,
                    creator=profile.user, last_modifier=profile.user)
                )

        notify_models.NotificationRecipient.objects.bulk_create(
            recipient_objs,
            batch_size=100
        )
        files = get_files(instance)
        SOCKET_HOST = os.environ.get('SOCKET_HOST')
        SOCKET_PORT = os.environ.get('SOCKET_PORT')
        SOCKET_URL = os.environ.get('SOCKET_URL')
        if SOCKET_URL:
            socketIO = SocketIO(SOCKET_URL)
        else:
            socketIO = SocketIO(SOCKET_HOST, SOCKET_PORT)
        socketIO.emit("chat_channel", {
            "message": {
                "id": notify_obj.id,
                "body": instance.body,
                "talk": {
                    "id": instance.talk.id,
                    "code": instance.talk.code,
                    "content_type_name": instance.talk.content_type.name,
                    "object_id": instance.talk.object_id,
                },
                "sender": {
                    "id": notify_obj.sender.id,
                    "first_name": notify_obj.sender.first_name,
                    "last_name": notify_obj.sender.last_name,
                    "photo": None,
                    "role": notify_obj.sender.role,
                    "company": {
                        "id": notify_obj.sender.company.id,
                        "name": notify_obj.sender.company.name,
                        "category": {}
                    }
                },
                "files": files
            }
        })
    except Exception as e:
        print(e)