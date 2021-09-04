from prometheus_client import Counter, Gauge, registry


def save_users_count(data):
    Metrics.users_total.set(len(data))


class Metrics:
    users_total = Gauge("users_total", "users who confirmed email")

    errors = Counter("errors", "Errors count")

    receiving_message = Counter("receive_message", "Receiving message from channel")

    sending_message = Counter("sending_notification", "Sending notification to user", ["type"])
    sending_message.labels("success")
    sending_message.labels("blocked")

    changing_mode = Counter("changing_mode", "Changing notification mode", ["type"])
    changing_mode.labels("to_active")
    changing_mode.labels("to_registered")

    registartion = Counter("registration", "Registration", ["type"])
    registartion.labels("success")
    registartion.labels("success")

    start_command = Counter("start_command", "Using /start command", ["type"])
    start_command.labels("success")

    help_command = Counter("help_command", "Using /help command", ["type"])
    help_command.labels("success")