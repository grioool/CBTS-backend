def get_daily_limit_for_role(role_id: int) -> int:

    if role_id == 2:
        return 5
    elif role_id == 3:
        return 50
    elif role_id == 4:
        return 200
    else:
        return 0
