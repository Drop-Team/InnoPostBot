from app import bot
from app import fetch_client
from prometheus_client import start_http_server

import config


def main():
    start_http_server(config.PROMETHEUS_PORT)
    fetch_client.start()
    bot.start()


if __name__ == '__main__':
    main()
