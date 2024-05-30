"""REST API for posts."""
# import hashlib
import flask
import insta485
from ..views.index import login_general


@insta485.app.route('/api/v1/', methods=['GET'])
def get_api_urls():
    """Return API resource URLs."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }

    return flask.jsonify(**context), 200


@insta485.app.route('/api/v1/posts/', methods=['GET'])
def get_posts():
    """Return posts based on args."""
    credentials = authenticate_http()
    if credentials == 403:
        return flask.jsonify({"message": "Forbidden", "status_code": 403}), 403
    username = str(credentials)

    connection = insta485.model.get_db()

    postid = flask.request.args.get("postid_lte",
                                    default=newest_postid(connection),
                                    type=int)
    page = flask.request.args.get("page", default=0, type=int)
    size = flask.request.args.get("size", default=10, type=int)
    if size < 0 or page < 0:
        return flask.jsonify({"message": "Bad Request",
                              "status_code": 400}), 400

    if postid < 1 or postid > newest_postid(connection):
        return flask.jsonify({"message": "Not Found", "status_code": 404}), 404

    offset = (size * page)

    cur = connection.execute(
        "SELECT DISTINCT postid "
        "FROM posts "
        "INNER JOIN following "
        "WHERE ((owner = ?) OR "
        "(owner = following.username2 AND ? = following.username1)) AND "
        "postid <= ? "
        "ORDER BY postid DESC "
        "LIMIT ? OFFSET ? ",
        (username, username, postid, size, offset, )
    )
    posts = cur.fetchall()

    results = []
    for post in posts:
        results.append({"postid": post["postid"],
                        "url": "/api/v1/posts/" + str(post["postid"]) + "/"})

    num_posts = len(results)

    next_url = ""
    if (num_posts) >= (size):
        next_url = "/api/v1/posts/?size=" + str(size) + "&page="
        next_url += str(page + 1) + "&postid_lte=" + str(postid)

    if flask.request.query_string:
        url = flask.request.full_path
    else:
        url = flask.request.path

    return flask.jsonify({"next": next_url, "results": results,
                          "url": url}), 200


@insta485.app.route('/api/v1/posts/<int:postid>/', methods=['GET'])
def get_one_post(postid):
    """Return one post, including comments and likes."""
    credentials = authenticate_http()
    if credentials == 403:
        return flask.jsonify({"message": "Forbidden", "status_code": 403}), 403
    username = str(credentials)

    connection = insta485.model.get_db()

    if postid < 1 or postid > newest_postid(connection):
        return flask.jsonify({"message": "Not Found", "status_code": 404}), 404

    cur = connection.execute(
        "SELECT DISTINCT postid, filename, owner, created "
        "FROM posts "
        "WHERE postid = ? ",
        (postid, )
      )
    post = cur.fetchone()

    cur = connection.execute(
        "SELECT DISTINCT username, users.filename "
        "FROM users "
        "INNER JOIN posts "
        "WHERE posts.postid = ? AND posts.owner = username",
        (postid, )
    )
    user = cur.fetchone()

    cur = connection.execute(
        "SELECT DISTINCT postid, owner "
        "FROM likes "
        "WHERE likes.postid = ?",
        (postid, )
    )
    likes = cur.fetchall()

    cur = connection.execute(
        "SELECT DISTINCT likeid "
        "FROM likes "
        "WHERE likes.postid = ? AND "
        "likes.owner = ? ",
        (postid, username, )
    )
    user_likes = cur.fetchone()
    if not user_likes:
        logged_user_likes = False
        likes_url = None
    else:
        logged_user_likes = True
        likes_url = "/api/v1/likes/" + str(user_likes['likeid']) + "/"

    cur = connection.execute(
        "SELECT DISTINCT commentid, owner, postid, text "
        "FROM comments "
        "WHERE comments.postid = ?",
        (postid, )
    )
    comments = cur.fetchall()

    results = []
    for comment in comments:
        logged_user_owns = bool(comment['owner'] == username)

        results.append({"commentid": comment['commentid'],
                        "lognameOwnsThis": logged_user_owns,
                        "owner": comment['owner'],
                        "ownerShowUrl": "/users/" + comment['owner'] + "/",
                        "text": comment['text'],
                        "url": "/api/v1/comments/" +
                        str(comment['commentid']) + "/"})

    return flask.jsonify({"comments": results,
                          "comments_url": "/api/v1/comments/?postid="
                          + str(postid), "created": post['created'],
                          "imgUrl": "/uploads/" + post['filename'],
                          "likes": {"lognameLikesThis": logged_user_likes,
                                    "numLikes": len(likes),
                                    "url": likes_url},
                          "owner": post['owner'], "ownerImgUrl": "/uploads/"
                          + user['filename'], "ownerShowUrl": "/users/"
                          + post['owner'] + "/", "postShowUrl": "/posts/"
                          + str(postid) + "/", "postid": postid,
                          "url": flask.request.path}), 200


def authenticate_http():
    """Authenticate that a user is signed in."""
    if not flask.session.get('username') or flask.session.get('password'):
        auth = flask.request.authorization
        if not auth:
            return 403
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
    else:
        username = flask.session.get('username')
        password = flask.session.get('password')
        return username

    return login_general(username, password)


def newest_postid(connection):
    """Get newest postid."""
    cur = connection.execute(
          "SELECT DISTINCT postid "
          "FROM posts "
          "ORDER BY postid DESC"
      )
    total_posts = cur.fetchall()

    return total_posts[0]["postid"]
