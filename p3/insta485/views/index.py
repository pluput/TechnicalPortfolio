"""
Insta485 index (main) view.

URLs include:
/
/explore/
/users/<user_url_slug>/
/users/<user_url_slug>/followers/
/users/<user_url_slug>/following/
/posts/<postid_url_slug>/
/accounts/login/
/accounts/logout/
/accounts/create/
/accounts/delete/
/accounts/edit/
/accounts/password/
"""
import uuid
import hashlib
import pathlib
import arrow
import flask
import insta485


@insta485.app.route('/', methods=['GET'])
def show_index():
    """Display / route."""
    # Connect to database
    connection = insta485.model.get_db()

    # get username
    username = flask.session.get('username')
    if not username:
        return flask.redirect('/accounts/login/')

    cur = connection.execute(
        "SELECT DISTINCT postid, filename, owner "
        "FROM posts "
        "INNER JOIN following "
        "WHERE (owner = ?) OR "
        "(owner = following.username2 AND ? = following.username1) "
        "ORDER BY postid DESC",
        (username, username, )
    )
    posts = cur.fetchall()

    cur = connection.execute(
        "SELECT DISTINCT username, filename "
        "FROM users "
        "INNER JOIN following "
        "WHERE (username = ?) OR "
        "(following.username2 = username AND following.username1 = ?)",
        (username, username, )
    )
    users = cur.fetchall()

    cur = connection.execute(
        "SELECT DISTINCT commentid, owner, postid, text "
        "FROM comments "
        "INNER JOIN following "
        "WHERE (following.username2 = owner AND following.username1 = ?) "
        "OR (owner = ?)",
        (username, username, )
    )
    comments = cur.fetchall()

    cur = connection.execute(
        "SELECT postid, COUNT(*) "
        "FROM likes "
        "GROUP BY likes.postid"
    )
    likes = cur.fetchall()

    # Humanize posts' timestamps
    cur = connection.execute(
        "SELECT DISTINCT posts.postid, posts.created "
        "FROM posts "
        "INNER JOIN following "
        "WHERE (following.username2 = posts.owner AND "
        "following.username1 = ?) "
        "OR (posts.owner = ?)",
        (username, username, )
    )
    rows = cur.fetchall()
    dates = rows.copy()
    i = 0
    for row in rows:
        human_readable_timestamp = arrow.get(row['created'],
                                             'YYYY-MM-DD HH:mm:ss').humanize()
        dates[i] = human_readable_timestamp
        i = i + 1

    # Add database info to context
    context = {"logname": username,
               "posts": posts,
               "users": users,
               "comments": comments,
               "likes": likes,
               "dates": dates}
    return flask.render_template("index.html", **context)


@insta485.app.route('/explore/', methods=['GET'])
def show_explore():
    """Display /explore/ route."""
    # Connect to database
    connection = insta485.model.get_db()

    # get username
    username = flask.session.get('username')
    if not username:
        return flask.redirect('/accounts/login/')

    cur = connection.execute(
        "SELECT DISTINCT username, filename "
        "FROM users "
        "WHERE (username != ?) "
        "AND NOT EXISTS "
        "(SELECT * FROM following "
        "WHERE (following.username1 = ? AND following.username2 = username))",
        (username, username, )
    )
    users = cur.fetchall()

    context = {"logname": username,
               "users": users}
    return flask.render_template("explore.html", **context)


@insta485.app.route('/users/<path:curr_user>/')
def show_users(curr_user):
    """Display /users/curr_user/ route."""
    # Connect to database
    connection = insta485.model.get_db()

    # get username
    username = flask.session.get('username')
    if not username:
        return flask.redirect('/accounts/login/')

    cur = connection.execute(
        "SELECT DISTINCT fullname "
        "FROM users "
        "WHERE users.username = ?",
        (curr_user, )
    )
    fullname = cur.fetchone()

    cur = connection.execute(
        "SELECT DISTINCT username2 "
        "FROM users "
        "INNER JOIN following "
        "WHERE username1 = ? AND username2 = ?",
        (username, curr_user, )
    )
    is_following = cur.fetchone()

    cur = connection.execute(
        "SELECT COUNT(*) "
        "FROM posts "
        "WHERE posts.owner = ?",
        (curr_user, )
    )
    total_posts = cur.fetchall()

    cur = connection.execute(
        "SELECT COUNT(*) "
        "FROM following "
        "WHERE following.username2 = ?",
        (curr_user, )
    )
    followers = cur.fetchall()

    cur = connection.execute(
        "SELECT COUNT(*) "
        "FROM following "
        "WHERE following.username1 = ?",
        (curr_user, )
    )
    following = cur.fetchall()

    cur = connection.execute(
        "SELECT DISTINCT postid, filename "
        "FROM posts "
        "WHERE posts.owner = ?",
        (curr_user, )
    )
    posts = cur.fetchall()

    context = {"logname": username,
               "curr_user": curr_user,
               "fullname": fullname,
               "is_following": is_following,
               "total_posts": total_posts,
               "followers": followers,
               "following": following,
               "posts": posts}
    return flask.render_template("users.html", **context)


@insta485.app.route('/users/<path:curr_user>/followers/', methods=['GET'])
def show_followers(curr_user):
    """Display /users/curr_user/followers/ route."""
    # Connect to database
    connection = insta485.model.get_db()

    # get username
    username = flask.session.get('username')
    if not username:
        return flask.redirect('/accounts/login/')

    # Check if user exists first
    cur = connection.execute(
        "SELECT * "
        "FROM users "
        "WHERE username = ?",
        (username, )
    )
    user_exists = cur.fetchone()
    if not user_exists:
        flask.abort(404)

    cur = connection.execute(
        "SELECT DISTINCT username, filename "
        "FROM users, following "
        "WHERE (username != ?) AND "
        "(following.username2 == ? AND following.username1 == username) "
        "AND EXISTS "
        "(SELECT * FROM following "
        "WHERE (following.username1 == ? AND following.username2 = username))",
        (curr_user, curr_user, username, )
    )
    followers_we_follow = cur.fetchall()

    cur = connection.execute(
        "SELECT DISTINCT username, filename "
        "FROM users, following "
        "WHERE (username != ?) AND "
        "(following.username2 == ? AND following.username1 == username) "
        "AND NOT EXISTS "
        "(SELECT * FROM following "
        "WHERE (following.username1 == ? AND following.username2 = username))",
        (curr_user, curr_user, username, )
    )
    followers = cur.fetchall()

    context = {"logname": username,
               "curr_user": curr_user,
               "followers_we_follow": followers_we_follow,
               "followers": followers}
    return flask.render_template("followers.html", **context)


@insta485.app.route('/users/<path:curr_user>/following/', methods=['GET'])
def show_following(curr_user):
    """Display /users/curr_user/following/ route."""
    # Connect to database
    connection = insta485.model.get_db()

    # get username
    username = flask.session.get('username')
    if not username:
        return flask.redirect('/accounts/login/')

    # Check if user exists first
    cur = connection.execute(
        "SELECT * "
        "FROM users "
        "WHERE username = ?",
        (curr_user, )
    )
    user_exists = cur.fetchone()
    if not user_exists:
        flask.abort(404)

    cur = connection.execute(
        "SELECT DISTINCT username, filename "
        "FROM users, following "
        "WHERE (username != ?) AND "
        "(following.username1 == ? AND following.username2 == username) "
        "AND EXISTS "
        "(SELECT * FROM following "
        "WHERE (following.username1 == ? AND following.username2 = username))",
        (curr_user, curr_user, username, )
    )
    following_we_follow = cur.fetchall()

    cur = connection.execute(
        "SELECT DISTINCT username, filename "
        "FROM users, following "
        "WHERE (username != ?) AND "
        "(following.username1 == ? AND following.username2 == username) "
        "AND NOT EXISTS "
        "(SELECT * FROM following "
        "WHERE (following.username1 == ? AND following.username2 = username))",
        (curr_user, curr_user, username, )
    )
    following = cur.fetchall()

    context = {"logname": username,
               "curr_user": curr_user,
               "following_we_follow": following_we_follow,
               "following": following}
    return flask.render_template("following.html", **context)


@insta485.app.route('/following/', methods=['POST'])
def post_follow():
    """Request /following/ post."""
    # connect db
    connection = insta485.model.get_db()

    # get username
    username = flask.session.get('username')
    if not username:
        return flask.redirect('/accounts/login/')

    operation = flask.request.form["operation"]
    username2 = flask.request.form["username"]
    target = flask.request.args.get("target")
    if not target:
        target = '/'

    cur = connection.execute(
        "SELECT * "
        "FROM following "
        "WHERE username1 = ? AND username2 = ?",
        (username, username2, )
    )
    temp = cur.fetchone()

    if operation == 'follow':
        if temp:
            flask.abort(409)

        cur = connection.execute(
            "INSERT INTO following(username1, username2) "
            "VALUES (?, ?)",
            (username, username2, )
        )

    else:
        if not temp:
            flask.abort(409)

        cur = connection.execute(
            "DELETE FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (username, username2, )
        )

    return flask.redirect(target)


@insta485.app.route('/posts/<path:postid>/')
def show_post(postid):
    """Display /posts/postid/ route."""
    # Connect to database
    connection = insta485.model.get_db()

    # get username
    username = flask.session.get('username')
    if not username:
        return flask.redirect('/accounts/login/')

    cur = connection.execute(
        "SELECT DISTINCT postid, filename, owner "
        "FROM posts "
        "WHERE postid = ? ",
        (postid, )
    )
    post = cur.fetchall()

    cur = connection.execute(
        "SELECT DISTINCT username, users.filename "
        "FROM users "
        "INNER JOIN posts "
        "WHERE posts.postid == ? AND posts.owner == username",
        (postid, )
    )
    user = cur.fetchall()

    cur = connection.execute(
        "SELECT postid, owner, COUNT(*) "
        "FROM likes "
        "WHERE likes.postid == ?",
        (postid, )
    )
    likes = cur.fetchall()

    cur = connection.execute(
        "SELECT DISTINCT commentid, owner, postid, text "
        "FROM comments "
        "WHERE comments.postid == ?",
        (postid, )
    )
    comments = cur.fetchall()

    # Humanize posts' timestamps
    cur = connection.execute(
        "SELECT DISTINCT posts.created "
        "FROM posts "
        "WHERE posts.postid == ?",
        (postid, )
    )
    row = cur.fetchall()
    human_readable_timestamp = arrow.get(row[0]['created'],
                                         'YYYY-MM-DD HH:mm:ss').humanize()
    date = human_readable_timestamp

    context = {"logname": username,
               "post": post,
               "user": user,
               "likes": likes,
               "comments": comments,
               "date": date}
    return flask.render_template("post.html", **context)


@insta485.app.route('/posts/', methods=['POST'])
def post_posts():
    """Request /posts/ post."""
    # connect db
    connection = insta485.model.get_db()

    # get username
    username = flask.session.get('username')
    if not username:
        flask.redirect('/accounts/login/')

    # set target
    target = flask.request.args.get("target")
    if not target:
        target = '/users/' + username + '/'

    operation = flask.request.form["operation"]
    if operation == 'create':
        fileobj = flask.request.files["file"]
        if not fileobj:
            flask.abort(400)

        filename = fileobj.filename

        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix
        uuid_filename = f"{stem}{suffix}"

        # save on disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_filename
        fileobj.save(path)

        connection.execute(
            "INSERT INTO posts (filename, owner) "
            "VALUES (?, ?)",
            (uuid_filename, username, )
        )

    else:
        postid = flask.request.form['postid']
        cur = connection.execute(
            "SELECT * "
            "FROM posts "
            "WHERE postid = ?",
            (postid, )
        )
        post = cur.fetchone()

        if post['owner'] != username:
            flask.abort(403)

        temp = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"] /
                            post['filename'])
        temp.unlink()

        connection.execute(
            "DELETE FROM posts "
            "WHERE postid = ?",
            (postid, )
        )

    return flask.redirect(target)


@insta485.app.route('/likes/', methods=['POST'])
def post_like():
    """Request /likes/ post."""
    # connect db
    connection = insta485.model.get_db()

    # get username
    username = flask.session.get('username')
    if not username:
        return flask.redirect('/accounts/login/')

    target = flask.request.args.get("target")
    if not target:
        target = '/'

    operation = flask.request.form["operation"]
    postid = flask.request.form["postid"]
    cur = connection.execute(
        "SELECT owner, created "
        "FROM posts "
        "WHERE postid = ?",
        (postid, )
    )
    posts = cur.fetchone()

    cur = connection.execute(
        "SELECT owner "
        "FROM likes "
        "WHERE owner = ? AND postid = ?",
        (username, postid, )
    )
    likes = cur.fetchall()

    if operation == 'like':
        if likes:
            flask.abort(409)

        if posts['owner'] == "":
            flask.abort(409)

        cur = connection.execute(
            "INSERT INTO likes(created, postid, owner) "
            "VALUES (datetime('now'), ?, ?)",
            (postid, username, )
        )

    else:
        if not likes:
            flask.abort(409)

        cur = connection.execute(
            "SELECT likeid "
            "FROM likes "
            "WHERE owner = ? AND postid = ?",
            (username, postid, )
        )
        likes_id = cur.fetchone()

        if likes_id['likeid'] == "":
            flask.abort(409)

        cur = connection.execute(
            "DELETE FROM likes "
            "WHERE likeid = ?",
            (likes_id['likeid'], )
        )

    return flask.redirect(target)


@insta485.app.route('/comments/', methods=['POST'])
def post_comments():
    """Request /comments/ post."""
    # connect db
    connection = insta485.model.get_db()

    # get username
    username = flask.session.get('username')
    if not username:
        return flask.redirect('/accounts/login/')

    target = flask.request.args.get('target')
    if not target:
        target = '/'

    operation = flask.request.form["operation"]

    if operation == "create":
        text = flask.request.form["text"]
        postid = flask.request.form["postid"]

        if text == "":
            flask.abort(400)

        cur = connection.execute(
            "INSERT INTO comments(postid, owner, text) VALUES (?, ?, ?)",
            (postid, username, text, )
        )

    else:
        commentid = flask.request.form["commentid"]
        cur = connection.execute(
            "SELECT * "
            "FROM comments "
            "WHERE commentid = ?",
            (commentid, )
        )
        comment = cur.fetchone()

        if not username == comment['owner']:
            flask.abort(403)

        cur = connection.execute(
            "DELETE FROM comments "
            "WHERE commentid = ?",
            (commentid, )
        )

    return flask.redirect(target)


# information is posted from post_login
@insta485.app.route('/accounts/login/', methods=['GET', 'POST'])
def show_login():
    """Display /accounts/login/ route."""
    if flask.request.method == 'POST':
        # set user cookies from login post
        flask.session['username'] = flask.request.form['username']
        return flask.redirect(flask.url_for('index'))

    return flask.render_template("login.html")


@insta485.app.route('/accounts/logout/', methods=['POST'])
def show_logout():
    """Request /accounts/logout/ post."""
    # clear session cookies
    flask.session.clear()
    return flask.redirect(flask.url_for('show_login'))


@insta485.app.route('/accounts/', methods=['POST'])
def post_accounts():
    """Request /accounts/ post."""
    # assign target
    target = flask.request.args.get("target")
    if not target:
        target = '/'

    # Connect to database
    connection = insta485.model.get_db()

    operation = flask.request.form['operation']
    if operation == 'login':
        post_login()
    elif operation == 'create':
        post_create(connection)
    elif operation == 'delete':
        post_delete(connection)
    elif operation == 'edit_account':
        post_edit(connection)
    else:
        post_upd_password(connection)

    return flask.redirect(target)


def post_login():
    """Request login post."""
    # obtain username and password
    username = flask.request.form['username']
    password = flask.request.form['password']
    if username == "" or password == "":
        flask.abort(400)

    if login_general(username, password) == 403:
        flask.abort(403)
    else:
        # set session to current user
        flask.session['username'] = username


def login_general(username, password):
    """Verify username and password."""
    connection = insta485.model.get_db()

    # encrypt password with salt + sha algo
    cur = connection.execute(
        "SELECT DISTINCT password "
        "FROM users "
        "WHERE username = ?",
        (username, )
    )
    match = cur.fetchone()
    if not match:
        return 403
    encrypted_password = match['password'].split('$')
    salt = encrypted_password[1]

    hash_obj = hashlib.new('sha512')
    salted_password = salt + password
    hash_obj.update(salted_password.encode('utf-8'))
    hashed_password = hash_obj.hexdigest()
    password_in_db = "$".join(['sha512', salt, hashed_password])

    # check db for posted information from login
    cur = connection.execute(
        "SELECT DISTINCT username, password "
        "FROM users "
        "WHERE username = ? AND password = ?",
        (username, password_in_db, )
    )
    result = cur.fetchone()

    if not result:
        return 403

    return username


def post_create(connection):
    """Request create post."""
    # check for empty fields
    username = flask.request.form['username']
    password = flask.request.form['password']
    fullname = flask.request.form['fullname']
    email = flask.request.form['email']
    user_file = flask.request.files['file']
    if not (username and password and fullname and email and user_file):
        flask.abort(400)

    # handle file
    filename = user_file.filename
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix
    uuid_filename = f"{stem}{suffix}"

    user_file.save(insta485.app.config["UPLOAD_FOLDER"]/uuid_filename)

    # check for duplicate username
    cur = connection.execute(
        "SELECT username "
        "FROM users "
        "WHERE username=?",
        (username, )
    )
    result = cur.fetchone()
    if result:
        flask.abort(409)

    salted_password = uuid.uuid4().hex + password
    hashlib.new('sha512').update(salted_password.encode('utf-8'))
    hashed_password = hashlib.new('sha512').hexdigest()
    password_in_db = "$".join(['sha512', uuid.uuid4().hex, hashed_password])

    cur = connection.execute(
        "INSERT INTO "
        "users(username, fullname, email, filename, password) "
        "VALUES (?, ?, ?, ?, ?)",
        (username, fullname, email, uuid_filename, password_in_db, )
    )

    flask.session['username'] = username


def post_delete(connection):
    """Request delete post."""
    username = flask.session.get('username')
    if not username:
        flask.abort(403)

    cur = connection.execute(
        "SELECT * "
        "FROM posts "
        "WHERE owner = ?",
        (username, )
    )
    posts = cur.fetchall()

    for post in posts:
        temp = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"] /
                            post['filename'])
        temp.unlink()

    cur = connection.execute(
        "SELECT * "
        "FROM users "
        "WHERE username = ?",
        (username, )
    )
    user = cur.fetchone()
    temp = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"] /
                        user['filename'])
    temp.unlink()

    cur = connection.execute(
        "DELETE "
        "FROM users "
        "WHERE username = ?",
        (username, )
    )

    # logout user
    flask.session.clear()


def post_edit(connection):
    """Request edit post."""
    username = flask.session.get('username')
    if not username:
        flask.abort(403)
    fullname = flask.request.form['fullname']
    if not fullname:
        flask.abort(400)
    email = flask.request.form['email']
    if not email:
        flask.abort(400)

    file = flask.request.files['file']

    cur = connection.execute(
        "UPDATE users "
        "SET fullname = ? "
        "WHERE username = ?",
        (fullname, username, )
    )

    cur = connection.execute(
        "UPDATE users "
        "SET email = ? "
        "WHERE username = ?",
        (email, username, )
    )

    if file:
        cur = connection.execute(
            "SELECT filename "
            "FROM users "
            "WHERE username = ?",
            (username, )
        )
        name = cur.fetchone()
        temp = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"] /
                            name['filename'])
        temp.unlink()
        # delete existing photo
        fileobj = flask.request.files["file"]
        filename = fileobj.filename
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix
        uuid_filename = f"{stem}{suffix}"
        cur = connection.execute(
            "UPDATE users "
            "SET filename = ? "
            "WHERE username = ?",
            (uuid_filename, username, )
        )
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_filename
        fileobj.save(path)


def post_upd_password(connection):
    """Request password post."""
    username = flask.session.get('username')
    if not username:
        flask.abort(403)
    password = flask.request.form['password']
    if not password:
        flask.abort(400)
    new_pass1 = flask.request.form['new_password1']
    if not new_pass1:
        flask.abort(400)
    new_pass2 = flask.request.form['new_password2']
    if not new_pass2:
        flask.abort(400)

    algorithm = 'sha512'
    cur = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username = ?",
        (username, )
    )
    match = cur.fetchone()
    encrypted = match['password'].split('$')
    salt = encrypted[1]
    hash_obj = hashlib.new(algorithm)
    salted_password = salt + password
    hash_obj.update(salted_password.encode('utf-8'))
    hash_password = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, hash_password])
    if not password_db_string == match['password']:
        flask.abort(403)
    if not new_pass1 == new_pass2:
        flask.abort(401)
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    salted_password = salt + new_pass1
    hash_obj.update(salted_password.encode('utf-8'))
    hash_password = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, hash_password])
    cur = connection.execute(
            "UPDATE users "
            "SET password = ? "
            "WHERE username = ?",
            (password_db_string, username, )
        )


@insta485.app.route('/accounts/create/', methods=['GET'])
def show_create():
    """Display /accounts/create/ route."""
    # Connect to database
    connection = insta485.model.get_db()

    # get username
    username = flask.session.get('username')
    if not username:
        return flask.redirect('/accounts/login/')

    # query database
    cur = connection.execute(
        "SELECT username, fullname "
        "FROM users"
    )
    users = cur.fetchall()

    # add to database
    context = {"users": users}
    return flask.render_template("create.html", **context)


@insta485.app.route('/accounts/delete/')
def show_delete():
    """Display /accounts/delete/ route."""
    # Connect to database
    connection = insta485.model.get_db()

    # get username
    username = flask.session.get('username')
    if not username:
        return flask.redirect('/accounts/login/')

    # query database
    cur = connection.execute(
        "SELECT * "
        "FROM users "
        "WHERE username = ?",
        (username, )
    )
    user = cur.fetchone()

    # add to database
    context = {"logname": username,
               "user": user}
    return flask.render_template("delete.html", **context)


@insta485.app.route('/accounts/edit/', methods=['GET'])
def show_edit():
    """Display /accounts/edit/ route."""
    # Connect to database
    connection = insta485.model.get_db()

    # get username
    username = flask.session.get('username')
    if not username:
        return flask.redirect('/accounts/login/')

    # query database
    cur = connection.execute(
        "SELECT * "
        "FROM users "
        "WHERE username = ?",
        (username, )
    )
    user = cur.fetchall()

    # Add database info to context
    context = {"logname": username,
               "user": user}
    return flask.render_template("edit.html", **context)


@insta485.app.route('/accounts/password/')
def show_password():
    """Display /accounts/password/ route."""
    # get username
    username = flask.session.get('username')
    if not username:
        return flask.redirect('/accounts/login/')

    # Add database info to context
    context = {"logname": username}
    return flask.render_template("password.html", **context)


@insta485.app.route('/uploads/<path:filename>')
def show_images(filename):
    """Display /uploads/filename route."""
    # get username
    username = flask.session.get('username')
    if not username:
        flask.abort(403)

    url = pathlib.Path('/var/uploads')
    if (pathlib.Path(url/filename)).exists():
        flask.abort(404)

    return flask.send_from_directory(insta485.app.config["UPLOAD_FOLDER"],
                                     filename)
