=================
Lifespan Protocol
=================

**Version**: 2.0 (2019-03-20)

The Lifespan ASGI sub-specification outlines how to communicate
lifespan events such as startup and shutdown within ASGI. The lifespan
being referred to is that of main event loop. In a multi-process
environment there will be lifespan events in each process.

The lifespan messages allow for a application to initialise and
shutdown in the context of a running event loop. An example of this
would be creating a connection pool and subsequently closing the
connection pool to release the connections.

A possible implementation of this protocol is given below::

    class App:

        def __init__(self, scope):
            self.scope = scope

        async def __call__(self, receive, send):
            if self.scope['type'] == 'lifespan':
                while True:
                    message = await receive()
                    if message['type'] == 'lifespan.startup':
                        await self.startup()
                        await send({'type': 'lifespan.startup.complete'})
                    elif message['type'] == 'lifespan.shutdown':
                        await self.shutdown()
                        await send({'type': 'lifespan.shutdown.complete'})
                        return
            else:
                pass # Handle other types

        async def startup(self):
            ...

        async def shutdown(self):
            ...


Scope
'''''

The lifespan scope exists for the duration of the event loop. The
scope itself contains basic metadata:

* ``type``: ``lifespan``
* ``asgi["version"]``: The version of the ASGI spec, as a string.
* ``asgi["spec_version"]``: The version of this spec being used, as a string. Optional, defaults to ``"1.0"``.

If an exception is raised when calling the application callable with a
``lifespan.startup`` message or a scope with type ``lifespan``
the server must continue but not send any lifespan events.

This allows for compatibility with applications that do not support the lifespan
protocol. If you want to log an error that occurred during lifespan startup and
prevent the server from starting, then send back ``lifespan.startup.failed``
instead.


Startup
'''''''

Sent when the server is ready to startup and receive connections, but
before it has started to do so.

Keys:

* ``type``: ``lifespan.startup``


Startup Complete
''''''''''''''''

Sent by the application when it has completed its startup. A server
must wait for this message before it starts processing connections.

Keys:

* ``type``: ``lifespan.startup.complete``


Startup Failed
''''''''''''''

Sent by the application when it has failed to complete its startup. If a server
sees this it should log/print the message provided and then exit.

Keys:

* ``type``: ``lifespan.startup.failed``
* ``message``: Unicode string (optional, defaults to ``""``).


Shutdown
''''''''

Sent when the server has stopped accepting connections and closed all
active connections.

Keys:

* ``type``:  ``lifespan.shutdown``


Shutdown Complete
'''''''''''''''''

Sent by the application when it has completed its cleanup. A server
must wait for this message before terminating.

Keys:

* ``type``: ``lifespan.shutdown.complete``


Shutdown Failed
'''''''''''''''

Sent by the application when it has failed to complete its cleanup. If a server
sees this it should log/print the message provided and then terminate.

Keys:

* ``type``: ``lifespan.shutdown.failed``
* ``message``: Unicode string (optional, defaults to ``""``).


Version History
===============

* 2.0 (2019-03-04): Added startup.failed and shutdown.failed,
  clarified exception handling during startup phase.
* 1.0 (2018-09-06): Updated ASGI spec with a lifespan protocol.


Copyright
=========

This document has been placed in the public domain.
