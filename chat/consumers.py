import json
import logging

from channels.consumer import SyncConsumer, AsyncConsumer
from channels.db import database_sync_to_async
from django.db import connection

logger = logging.getLogger(__name__)


class ChatAsyncConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        logger.warning('websocket_connect in %s', self.__class__.__name__)
        await self.send({
            "type": "websocket.accept",
        })

    async def websocket_disconnect(self, event):
        logger.warning('websocket_disconnect in %s', self.__class__.__name__)

    async def websocket_receive(self, event):
        logger.warning('websocket_receive in %s: %s', self.__class__.__name__, event['text'])
        text_data_json = json.loads(event['text'])
        message = text_data_json['message']
        if 'sleep:' in message:
            try:
                seconds = int(message.split(':')[-1])
            except Exception as err:
                logger.warning('Using fallback of 10 seconds')
                seconds = 10
            await self.db_access(seconds=seconds)
        await self.send({
            "type": "websocket.send",
            "text": event["text"],
        })

    @database_sync_to_async
    def db_access(self, seconds):
        logger.warning('Simulating long query in %s (seconds=%s)', self.__class__.__name__, seconds)
        with connection.cursor() as cur:
            cur.execute(f'select pg_sleep({seconds})')
        logger.warning('Long query returned in %s (seconds=%s)', self.__class__.__name__, seconds)


class ChatSyncConsumer(SyncConsumer):
    def websocket_connect(self, event):
        logger.warning('websocket_connect in %s', self.__class__.__name__)
        self.send({
            "type": "websocket.accept",
        })

    def websocket_disconnect(self, event):
        logger.warning('websocket_disconnect in %s', self.__class__.__name__)

    def websocket_receive(self, event):
        logger.warning('websocket_receive in %s: %s', self.__class__.__name__, event['text'])
        text_data_json = json.loads(event['text'])
        message = text_data_json['message']
        if 'sleep:' in message:
            try:
                seconds = int(message.split(':')[-1])
            except Exception as err:
                logger.warning('Using fallback of 10 seconds')
                seconds = 10
            self.db_access(seconds=seconds)
        self.send({
            "type": "websocket.send",
            "text": event["text"],
        })

    def db_access(self, seconds):
        logger.warning('Simulating long query in %s (seconds=%s)', self.__class__.__name__, seconds)
        with connection.cursor() as cur:
            cur.execute(f'select pg_sleep({seconds})')
        logger.warning('Long query returned in %s (seconds=%s)', self.__class__.__name__, seconds)
