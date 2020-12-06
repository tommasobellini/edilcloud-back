import json

import emoji
import requests
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from . import models as notify_models
from channels.layers import get_channel_layer

from ..project.models import Project


def event_triger(msg):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'notify_notify_channel',
        {
            'type': 'notify_message',
            'message': msg
        }
    )

def addRedirectUrl(talk):
    if talk.content_type.name == 'company':
        return "https://dev.edilcloud.io/apps/chat"
    if talk.content_type.name == 'project':
        return "https://dev.edilcloud.io/apps/projects/{}".format(str(talk.object_id))
    return "https://dev.edilcloud.io"

def addHeading(talk, notify_obj):
    if talk.content_type.name == 'company':
        return "{} Company Chat".format(notify_obj.sender.company.name)
    if talk.content_type.name == 'project':
        pr = Project.objects.filter(id=talk.object_id)
        if pr:
            return "{} Project Chat".format(pr[0].name)
        else:
            return "Project Chat"


def send_push_notification(notify_obj, recipient, body):
    body = json.loads(body)
    print(body['content'])
    header = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": "Basic YTkwNWIwMTItNmE0Ny00NjcxLTg5YzYtZWY4OTQ2NGQ4OTNl"
    }

    req_players = requests.get(
        "https://onesignal.com/api/v1/players?app_id=0fbdf0cf-d9f5-4363-809f-4735b1bba268&limit=300&offset=0",
        headers=header)
    print(req_players)
    list_profiles_id = []
    list_players_recipients = []

    for req_player in req_players.json()['players']:
        print('player external user id')
        print(str(req_player['external_user_id']))
        if str(req_player['external_user_id']) == str(recipient.id):
            list_players_recipients.append(req_player['id'])

    print('list ids')
    print(list_profiles_id)
    print('list players to sent')
    print(list_players_recipients)

    payload = {
        "app_id": "8fc7c8ff-a4c8-4642-823d-4675b809a3c9",
        "include_player_ids": list_players_recipients,
        "contents": {
            "en": "made by: {} {}".format(notify_obj.sender.first_name, notify_obj.sender.last_name)
        },
        "content-available": 1,
        "headings": {
            "en": body['content']
        },
        "data": {
            "custom_data": body['content'],
            "redirect_url": "https://test.edilcloud.io" + body['url']
        },
        "small_icon": "ic_stat_onesignal_default"
    }

    # "android_channel_id": "8d3bd99c-1755-4a33-a043-60a92c8b153c",
    # "wp_wns_sound": "erotic_girl_sound",
    # "android_sound": "erotic_girl_sound",

    req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
    print(req.status_code, req.reason)

@receiver([post_save, post_delete], sender=notify_models.NotificationRecipient)
def notify_notification(sender, instance, **kwargs):
    notify_obj = instance.notification
    recipient = instance
    event_triger({
        "message": {
            "id": notify_obj.id,
            "content_type": notify_obj.content_type.name,
            "body": json.loads(notify_obj.body),
            "dest": {
                "id": recipient.recipient.pk
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
            "subject": notify_obj.subject
        }
    })