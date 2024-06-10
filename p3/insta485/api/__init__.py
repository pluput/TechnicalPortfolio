"""Insta485 REST API."""

from insta485.api.posts import get_api_urls
from insta485.api.posts import get_posts
from insta485.api.posts import get_one_post
from insta485.api.posts import authenticate_http
from insta485.api.posts import newest_postid
from insta485.api.likes import post_new_like
from insta485.api.likes import delete_like
from insta485.api.comments import post_comment
from insta485.api.comments import delete_comment
