"""Contains functions for verifying user credentials and postid."""


from werkzeug.wrappers.response import Response
from flask import abort
import insta485


def w_postid(postid, connection):
    """Verify credentials and postid."""
    credentials = insta485.api.posts.authenticate_http()
    if credentials == 403:
        abort(Response("Forbidden", status=403))
    username = str(credentials)

    if int(postid) < 1 or int(postid) > insta485.api.newest_postid(connection):
        abort(Response("Not Found", status=404))

    return username


def wo_postid():
    """Verify credentials."""
    credentials = insta485.api.posts.authenticate_http()
    if credentials == 403:
        abort(Response("Forbidden", status=403))
    username = str(credentials)

    return username
