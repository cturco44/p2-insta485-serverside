"""Views, one for each Insta485 page."""
from insta485.views.following import show_following, check_user_url_slug_exists
from insta485.views.delete import delete_account
from insta485.views.create import create_account, upload_file
from insta485.views.index import show_index
from insta485.views.post import show_post, download_file
from insta485.views.post import uncomment, like_post, unlike_post
from insta485.views.post import comment, delete_post, check_user_post
from insta485.views.post import check_user_comment, check_comment_exists
from insta485.views.post import check_post_exists
from insta485.views.explore import show_explore, follow_user
from insta485.views.edit import show_edit
from insta485.views.password import show_password
from insta485.views.password import hash_password, check_password
from insta485.views.login import login, user_exists, check_credentials
from insta485.views.logout import logout
from insta485.views.user import user
from insta485.views.followers import followers
