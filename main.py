import argparse
import base64
import datetime
import logging
import os
import sys
import traceback
from typing import Generator

from job_notifications import create_notifications
import paramiko


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

# Constants
HOSTNAME = os.getenv("HOST")
HOST_KEY = os.getenv("HOST_KEY")
PORT = int(os.getenv("PORT"))
USERNAME = os.getenv("USER")
PASSWORD = os.getenv("PASS")
REMOTE_DIR = os.getenv("REMOTE_DIR")

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

    host_key = paramiko.RSAKey(
        data=base64.b64decode(HOST_KEY)
    )

    host_lookup = f"[{HOSTNAME}]:{PORT}"

    with paramiko.SSHClient() as ssh:
        ssh.get_host_keys().add(
            host_lookup,
            "ssh-rsa",
            host_key,
        )
        print(repr(HOSTNAME))
        print(ssh.get_host_keys().keys())
        ssh.connect(
            hostname=HOSTNAME,
            port=PORT,
            username=USERNAME,
            password=PASSWORD,
        )

        with ssh.open_sftp() as sftp:
            logger.info(sftp.listdir(REMOTE_DIR))


if __name__ == "__main__":
    try:
        main()
        notifications.notify()
    except Exception as e:
        logging.exception(e)
        stack_trace = traceback.format_exc()
        notifications.notify(error_message=stack_trace)
