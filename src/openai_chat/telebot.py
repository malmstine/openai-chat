
def users_command(msg):
    msg: str = msg.text
    if msg.startswith("/users "):
        action = msg.lstrip("/users ")
        if action.startswith("add ") or action.startswith("rem "):
            action = action[:3]
            user = action[4:]
            if user:
                return True
    return False


def get_user_action(msg: str) -> tuple[str, int]:
    action = msg.lstrip("/users ")
    action = action[:3]
    user = action[4:]
    return action, int(user)
