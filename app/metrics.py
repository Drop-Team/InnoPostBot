from prometheus_client import Counter, Gauge


def save_users_count(data):
    from app.users import UserStates

    users_total = 0
    users_confirmed = 0
    for user_id in data:
        users_total += 1
        if data[user_id].state == UserStates.confirmed:
            users_confirmed += 1

    Metrics.users_count.labels("total").set(users_total)
    Metrics.users_count.labels("confirmed").set(users_confirmed)


class Metrics:
    users_count = Gauge("users_count", "users who confirmed email", ["type"])
    users_count.labels("total")
    users_count.labels("confirmed")

    errors = Counter("errors", "Errors count")

    receiving_message = Counter("receiving_message", "Receiving message from channel")

    sending_notification = Counter("sending_notification", "Sending notification to user", ["type"])
    sending_notification.labels("success")
    sending_notification.labels("blocked")

    changing_mode = Counter("changing_mode", "Changing notification mode", ["type"])
    changing_mode.labels("subscribed_off")
    changing_mode.labels("subscribed_on")

    registration = Counter("registration", "Registration", ["type"])
    registration.labels("success")

    start_command = Counter("start_command", "Using /start command", ["type"])
    start_command.labels("success")

    help_command = Counter("help_command", "Using /help command", ["type"])
    help_command.labels("success")
