"""REST API for comments."""
import flask
from werkzeug.exceptions import HTTPException
import insta485
from .verify import w_postid
from .verify import wo_postid


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def post_comment():
    """Create new comments based on the text in the JSON body."""
    # grab postid
    postid = flask.request.args.get("postid")
    comment = flask.request.get_json()['text']

    connection = insta485.model.get_db()

    try:
        username = w_postid(postid, connection)
    except HTTPException as comm_error:
        return flask.jsonify({"message": comm_error.response,
                              "status_code": comm_error.code}), comm_error.code

    cur = connection.execute(
        "INSERT INTO comments(owner, postid, text) "
        "VALUES (?, ?, ?) ",
        (username, postid, comment, )
    )

    cur = connection.execute(
        "SELECT last_insert_rowid() "
        "FROM comments "
    )
    last_rowid = cur.fetchone()

    cur = connection.execute(
        "SELECT owner, commentid "
        "FROM comments "
        "WHERE commentid = ? ",
        (last_rowid["last_insert_rowid()"], )
    )
    curr_comment = cur.fetchone()

    return flask.jsonify({"commentid": curr_comment['commentid'],
                          "lognameOwnsThis": True,
                          "owner": curr_comment['owner'],
                          "ownerShowUrl": "/users/" +
                          str(curr_comment['owner']) + "/",
                          "text": comment,
                          "url": "/api/v1/comments/" +
                          str(curr_comment['commentid']) + "/"}), 201


@insta485.app.route('/api/v1/comments/<int:commentid>/', methods=['DELETE'])
def delete_comment(commentid):
    """Delete the comment based on the comment id."""
    connection = insta485.model.get_db()

    try:
        username = wo_postid()
    except HTTPException as comm_error:
        return flask.jsonify({"message": comm_error.response,
                              "status_code": comm_error.code}), comm_error.code

    cur = connection.execute(
        "SELECT * "
        "FROM comments "
        "WHERE comments.commentid = ? ",
        (commentid, )
    )
    comment_exists = cur.fetchone()
    if not comment_exists:
        return flask.jsonify({"message": "Not Found", "status_code": 404}), 404
    if comment_exists['owner'] != username:
        return flask.jsonify({"message": "Forbidden", "status_code": 403}), 403

    cur = connection.execute(
        "DELETE FROM comments "
        "WHERE comments.commentid = ? ",
        (commentid, )
    )

    return flask.jsonify({}), 204
