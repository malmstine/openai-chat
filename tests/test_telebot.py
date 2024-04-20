from openai_chat.actions import get_user_action


def test__get_user_action():
    msg = "/users add 1137456967"
    result = get_user_action(msg)
    assert result == ("add", 1137456967)


def test__get_user_action__rem():
    msg = "/users rem 1137456967"
    result = get_user_action(msg)
    assert result == ("rem", 1137456967)
