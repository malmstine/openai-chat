# USER_WHITE_LIST=1137456967:493865338
from openai_chat.telebot import get_user_action


def test__get_user_action():
    msg = "/users add 1137456967"
    result = get_user_action(msg)
    assert result == ("add", 1137456967)


def test__get_user_action__rem():
    msg = "/users rem 1137456967"
    result = get_user_action(msg)
    assert result == ("rem", 1137456967)
