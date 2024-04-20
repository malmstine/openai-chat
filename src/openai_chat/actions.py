def users_command(msg):
    msg: str = msg.text
    if msg.startswith("/users "):
        action = msg[7:]
        if action == "lst":
            return True
        if action.startswith("add ") or action.startswith("rem ") or action.startswith("lst "):
            user = msg[4:]
            if user:
                return True
    return False


def get_user_action(msg: str) -> tuple[str, int | None]:
    action = msg[7:]
    action, user = action[:3], action[4:]
    if action == "lst":
        return action, None
    return action, int(user)
