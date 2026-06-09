import argparse
import datetime
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
    "--since-date",
    help="Date to search - Date since file was last modified (format YYYY-MM-DD)",
    dest="since_date",
    default=None,
)


# Globals
args = parser.parse_args()
logger = logging.getLogger(__name__)
notifications = create_notifications("Dibels Connector", "mailgun", logs="app.log")


def _get_file_query_time() -> datetime.datetime:
    """Generates a timestamp for searching files on SFTP server. Any files modified after this timestamp will be
    uploaded to Google Cloud Storage"""
    if args.since_date is None:
        return datetime.datetime.now() - datetime.timedelta(hours=24)
    return datetime.datetime.strptime(args.since_date, "%Y-%m-%d")


def main():
    query_time = _get_file_query_time()
    logger.info(f"Looking for files modified since {query_time}")


if __name__ == "__main__":
    try:
        main()
        notifications.notify()
    except Exception as e:
        logging.exception(e)
        stack_trace = traceback.format_exc()
        notifications.notify(error_message=stack_trace)
