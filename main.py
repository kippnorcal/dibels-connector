import argparse
import base64
import datetime
from io import BytesIO
import logging
import os
import re
import sys
import traceback
from typing import Generator

from gbq_connector import CloudStorageClient
from job_notifications import create_notifications
import pandas as pd
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
parser.add_argument(
    "--get-all",
    help="Get all files from SFTP",
    dest="get_all",
    action="store_true",
)

# Constants
HOSTNAME = os.getenv("HOST")
HOST_KEY = os.getenv("HOST_KEY")
PORT = os.getenv("PORT")
USERNAME = os.getenv("USER")
PASSWORD = os.getenv("PASS")
REMOTE_DIR = os.getenv("REMOTE_DIR")
CLOUD_PATH = os.getenv("CLOUD_STORAGE_BASE_PATH")
BUCKET = os.getenv("BUCKET")
REGEX_PATTERN = r'(\d{4}-\d{4})'

# Globals
args = parser.parse_args()
logger = logging.getLogger(__name__)
notifications = create_notifications("Dibels Connector", "mailgun", logs="app.log")


def _get_file_query_time() -> datetime.datetime:
    """Generates a timestamp for searching files on SFTP server. Any files modified after this timestamp will be
    uploaded to Google Cloud Storage"""
    if args.since_date is None:
        return datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(hours=24)
    return datetime.datetime.strptime(args.since_date, "%Y-%m-%d")


def _extract_year(file_name: str) -> str:
    year_regex = re.compile(REGEX_PATTERN)
    y = year_regex.search(file_name)
    year = y.group()
    if year is None:
        raise ValueError("A year in YYYY-YYYY format not found in filename.")
    return year


def main():

    cloud_storage = CloudStorageClient()

    if not args.get_all:
        query_time = _get_file_query_time()
        logger.info(f"Looking for files modified since {query_time}")
        query_epoch = query_time.timestamp()
    else:
        logger.info("Getting all files from server")
        notifications.extend_job_name(" - get all files")
        query_epoch = 0

    host_key = paramiko.RSAKey(
        data=base64.b64decode(HOST_KEY)
    )

    host_lookup = f"[{HOSTNAME}]:{PORT}"

    file_count = 0

    with paramiko.SSHClient() as ssh:
        ssh.get_host_keys().add(
            host_lookup,
            "ssh-rsa",
            host_key,
        )

        ssh.connect(
            hostname=HOSTNAME,
            port=PORT,
            username=USERNAME,
            password=PASSWORD,
        )

        with ssh.open_sftp() as sftp:
            # List files in the remote directory
            for attribute in sftp.listdir_attr(REMOTE_DIR):
                logger.info(f"Checking:  {attribute.filename}")
                if attribute.st_mtime > query_epoch:
                    remote_path = f"{REMOTE_DIR}/{attribute.filename}"
                    local_path = f"/code/data/{attribute.filename}"
                    logger.info(f"Copying {remote_path} to {local_path}")
                    sftp.get(remote_path, local_path)
                    df = pd.read_csv(local_path, sep=",", quotechar='"', doublequote=True, dtype=str, header=0)

                    year = _extract_year(attribute.filename)
                    blob_name = f"{CLOUD_PATH}/{year}/{attribute.filename}"
                    logger.info(f"Uploading to {blob_name}")
                    cloud_storage.load_dataframe_to_cloud_as_csv(BUCKET, blob_name, df)
                    file_count += 1


    logger.info(f"Loaded {file_count} file(s) to cloud storage")


if __name__ == "__main__":
    try:
        main()
        notifications.notify()
    except Exception as e:
        logging.exception(e)
        stack_trace = traceback.format_exc()
        notifications.notify(error_message=stack_trace)
