def users_command(msg):
    msg: str = msg.text
    if msg.startswith("/users "):
        action = msg[7:]
        if action.startswith("add ") or action.startswith("rem "):
            user = msg[4:]
            if user:
                return True
    return False


def get_user_action(msg: str) -> tuple[str, int]:
    action = msg[7:]
    action, user = action[:3], action[4:]
    return action, int(user)
