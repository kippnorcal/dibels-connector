import argparse
import logging
import sys
import traceback

from job_notifications import create_notifications


# Logging Config
logging.basicConfig(
    handlers=[
        logging.FileHandler(filename="app.log", mode="w+"),
        logging.StreamHandler(sys.stdout),
    ],
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S%p %Z",
)


# Runtime Arg Config
parser = argparse.ArgumentParser()

parser.add_argument(
    "--start-date",
    help="Start Date: format YYYY-MM-DD",
    dest="start_date",
    default=None,
)


# Globals
args = parser.parse_args()
logger = logging.getLogger(__name__)
notifications = create_notifications("Dibels Connector", "mailgun", logs="app.log")


def main():
    pass


if __name__ == "__main__":
    try:
        main()
        notifications.notify()
    except Exception as e:
        logging.exception(e)
        stack_trace = traceback.format_exc()
        notifications.notify(error_message=stack_trace)
