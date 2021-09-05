from prometheus_client import Counter, Gauge


def save_users_count(data):
    Metrics.users_total.set(len(data))


class Metrics:
    users_total = Gauge("users_total", "users who confirmed email")

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
