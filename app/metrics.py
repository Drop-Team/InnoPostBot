from prometheus_client import Counter, Gauge


def save_users_metrics(data):
    from app.users import UserStates

    users_total = 0
    users_confirmed = 0

    users_subs_on = 0
    users_subs_off = 0

    for user_id, user in data.items():
        users_total += 1
        if user.state == UserStates.confirmed:
            users_confirmed += 1

            if user.subscribed:
                users_subs_on += 1
            else:
                users_subs_off += 1

    Metrics.users_count.labels("total").set(users_total)
    Metrics.users_count.labels("confirmed").set(users_confirmed)

    Metrics.users_mode_count.labels("subscribed_off").set(users_subs_off)
    Metrics.users_mode_count.labels("subscribed_on").set(users_subs_on)


class Metrics:
    users_count = Gauge("users_count", "users who confirmed email", ["type"])
    users_count.labels("total")
    users_count.labels("confirmed")

    users_mode_count = Gauge("users_mode", "Changing notification mode", ["type"])
    users_mode_count.labels("subscribed_off")
    users_mode_count.labels("subscribed_on")

    errors = Counter("errors", "Errors count")

    receiving_message = Counter("receiving_message", "Receiving message from channel")

    sending_notification = Counter("sending_notification", "Sending notification to user", ["type"])
    sending_notification.labels("success")
    sending_notification.labels("blocked")

    registration = Counter("registration", "Registration", ["type"])
    registration.labels("success")

    start_command = Counter("start_command", "Using /start command", ["type"])
    start_command.labels("success")

    help_command = Counter("help_command", "Using /help command", ["type"])
    help_command.labels("success")
