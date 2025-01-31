# Description
When a `SyncConsumer` performs a blocking action like using the Django ORM, all other actively connected consumers (both `SyncConsumer` and `AsyncConsumer`) are blocked and subsequent connections from any consumer are also blocked until the blocking action is completed.

Here 'blocked' in the context of actively connected consumers means that Daphne acknowledges incoming frames from the client but no consumer code is triggered:
> daphne.ws_protocol DEBUG WebSocket incoming frame on ['127.0.0.1', 50176]

'blocked' in the context of subsequent connections means that Channels initiates the handshake and Daphne upgrades the connection to websocket, but no consumer code is triggered and ~5 seconds later the connection attempt times out:
> django.channels.server INFO WebSocket HANDSHAKING /ws/chat/sync [127.0.0.1:50834]
> daphne.http_protocol DEBUG Upgraded connection ['127.0.0.1', 50834] to WebSocket
> daphne.ws_protocol DEBUG WebSocket closed for ['127.0.0.1', 50834]
> django.channels.server INFO WebSocket DISCONNECT /ws/chat/sync [127.0.0.1:50834]

# Reproduction

**Prerequisites**
1. Create a new Python 3.10.6 virtual environment and activate it
2. Run ```pip install -r requirements.txt``` from the base of the project
3. To reproduce the issue you only need to be able to connect to a PSQL database with a user that can run the `pg_sleep` command. I created a new database called `chat` on a local PSQL 14.4 server for the purposes of this example, but you can update `DATABASES` in `settings.py` accordingly for your own setup.

**Reproducing the issue**
- Open 4 tabs, 2 connected to http://127.0.0.1:8000/chat/sync/ and 2 connected to http://127.0.0.1:8000/chat/async/. Confirm they are functioning by sending a test message and confirming in either the terminal or web developer console that the message was sent and returned by the server
- In 1 of the sync tabs, type 'sleep: 60' into the input box and hit send. Confirm the following appears in the terminal:
> chat.consumers WARNING Simulating long query in ChatSyncConsumer (seconds=60)
- While the `ChatSyncConsumer` is blocking, attempt to send a message in the 3 other tabs. In the Django 4.2 and Django 5.1 (Channels 4.2.0) environments, behavior will be identical across all 3 tabs. The console should indicate Daphne received an incoming frame, but no consumer code will run and the message will not be returned until the blocking `ChatSyncConsumer` completes. In the Django 4.1 environment (Channels 4.0.0), the other sync tab will behave as described above, but the 2 async tabs will receive and echo the message immediately.
- While the `ChatSyncConsumer` is blocking, open a new tab and attempt to connect to both the sync WS (http://127.0.0.1:8000/chat/sync/) and async WS (http://127.0.0.1:8000/chat/async/). In all environments the console should indicate a handshake occurs, but no consumer connection code will run and the connection will close after 5 seconds.
