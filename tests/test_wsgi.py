import pytest

from asgiref.testing import ApplicationCommunicator
from asgiref.wsgi import WsgiToAsgi


@pytest.mark.asyncio
async def test_basic_wsgi():
    """
    Makes sure the WSGI wrapper has basic functionality.
    """
    # Define WSGI app
    def wsgi_application(environ, start_response):
        assert environ["HTTP_TEST_HEADER"] == "test value"
        start_response("200 OK", [["X-Colour", "Blue"]])
        yield b"first chunk "
        yield b"second chunk"

    # Wrap it
    application = WsgiToAsgi(wsgi_application)
    # Launch it as a test application
    instance = ApplicationCommunicator(
        application,
        {
            "type": "http",
            "http_version": "1.0",
            "method": "GET",
            "path": "/foo/",
            "query_string": b"bar=baz",
            "headers": [[b"test-header", b"test value"]],
        },
    )
    await instance.send_input({"type": "http.request"})
    # Check they send stuff
    assert (await instance.receive_output(1)) == {
        "type": "http.response.start",
        "status": 200,
        "headers": [(b"x-colour", b"Blue")],
    }
    assert (await instance.receive_output(1)) == {
        "type": "http.response.body",
        "body": b"first chunk ",
        "more_body": True,
    }
    assert (await instance.receive_output(1)) == {
        "type": "http.response.body",
        "body": b"second chunk",
        "more_body": True,
    }
    assert (await instance.receive_output(1)) == {"type": "http.response.body"}


@pytest.mark.asyncio
async def test_wsgi_empty_body():
    """
    Makes sure WsgiToAsgi handles an empty body response correctly
    """

    def wsgi_application(environ, start_response):
        start_response("200 OK", [])
        return []

    application = WsgiToAsgi(wsgi_application)
    instance = ApplicationCommunicator(
        application,
        {
            "type": "http",
            "http_version": "1.0",
            "method": "GET",
            "path": "/",
            "query_string": b"",
            "headers": [],
        },
    )
    await instance.send_input({"type": "http.request"})

    # response.start should always be send
    assert (await instance.receive_output(1)) == {
        "type": "http.response.start",
        "status": 200,
        "headers": [],
    }

    assert (await instance.receive_output(1)) == {"type": "http.response.body"}


@pytest.mark.asyncio
async def test_wsgi_multi_body():
    """
    Verify that multiple http.request events with body parts are all delivered
    to the WSGI application.
    """

    def wsgi_application(environ, start_response):
        infp = environ["wsgi.input"]
        body = infp.read(12)
        assert body == b"Hello World!"
        start_response("200 OK", [])
        return []

    application = WsgiToAsgi(wsgi_application)
    instance = ApplicationCommunicator(
        application,
        {
            "type": "http",
            "http_version": "1.0",
            "method": "POST",
            "path": "/",
            "query_string": b"",
            "headers": [[b"content-length", b"12"]],
        },
    )
    await instance.send_input(
        {"type": "http.request", "body": b"Hello ", "more_body": True}
    )
    await instance.send_input({"type": "http.request", "body": b"World!"})

    assert (await instance.receive_output(1)) == {
        "type": "http.response.start",
        "status": 200,
        "headers": [],
    }

    assert (await instance.receive_output(1)) == {"type": "http.response.body"}
