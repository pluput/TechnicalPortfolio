"""REST API for likes."""
import flask
from werkzeug.exceptions import HTTPException
import insta485
from .verify import w_postid
from .verify import wo_postid


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def post_new_like():
    """Create a new like for the specified post id."""
    # grab postid
    postid = flask.request.args.get("postid")

    connection = insta485.model.get_db()

    try:
        username = w_postid(postid, connection)
    except HTTPException as like_error:
        return flask.jsonify({"message": like_error.response,
                              "status_code": like_error.code}), like_error.code

    cur = connection.execute(
        "SELECT DISTINCT likeid "
        "FROM likes "
        "WHERE likes.owner = ? AND "
        "likes.postid = ? ",
        (username, postid, )
    )
    like_exists = cur.fetchone()
    if like_exists:
        return flask.jsonify({"likeid": like_exists['likeid'],
                              "url": "/api/v1/likes/" +
                              str(like_exists['likeid'])
                              + "/"}), 200

    cur = connection.execute(
        "INSERT INTO likes(owner, postid) "
        "VALUES (?, ?) ",
        (username, postid, )
    )

    cur = connection.execute(
        "SELECT last_insert_rowid() "
        "FROM likes "
    )
    curr_likeid = cur.fetchone()

    return flask.jsonify({"likeid": curr_likeid['last_insert_rowid()'],
                          "url": "/api/v1/likes/" +
                          str(curr_likeid['last_insert_rowid()']) + "/"}), 201


@insta485.app.route('/api/v1/likes/<int:likeid>/', methods=['DELETE'])
def delete_like(likeid):
    """Delete the like based on the like id."""
    connection = insta485.model.get_db()

    try:
        username = wo_postid()
    except HTTPException as like_error:
        return flask.jsonify({"message": like_error.response,
                              "status_code": like_error.code}), like_error.code

    cur = connection.execute(
        "SELECT * "
        "FROM likes "
        "WHERE likes.likeid = ? ",
        (likeid, )
    )
    like_exists = cur.fetchone()
    if not like_exists:
        return flask.jsonify({"message": "Not Found", "status_code": 404}), 404
    if like_exists['owner'] != username:
        return flask.jsonify({"message": "Forbidden", "status_code": 403}), 403

    cur = connection.execute(
        "DELETE FROM likes "
        "WHERE likes.likeid = ? ",
        (likeid, )
    )

    return flask.jsonify({}), 204
