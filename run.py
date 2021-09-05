from app import bot
from app import fetch_client
from prometheus_client import start_http_server


def main():
    start_http_server(8000)
    fetch_client.start()
    bot.start()


if __name__ == '__main__':
    main()
