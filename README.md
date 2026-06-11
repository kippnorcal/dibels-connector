# DIBELS connector
Automation for fetching DIBELS files from sftp server and loading to Google Cloud Storage.

## Dependencies
- Python
- Docker
- Google Cloud Storage
- Mailgun

## Setup

### .env File
At the root of the repo, create a `.env` file with the following varaibles:

```dotenv
# SFTP Server Crendentials
HOST=
USER=
PASS=
PORT=
REMOTE_DIR=
HOST_KEY=


# Google Cloud Storage
GOOGLE_APPLICATION_CREDENTIALS= # Name of credential file
GBQ_PROJECT=
BUCKET=
CLOUD_STORAGE_BASE_PATH=


# Mailgun & email notification variables
MG_DOMAIN=
MG_API_URL=
MG_API_KEY=
FROM_ADDRESS=
TO_ADDRESS=
FAILURE_EMAIL=
```

### Cloud Storage Credentials
Save credential file in the project's root dir and make sure it's name matches the `GOOGLE_APPLICATION_CREDENTIALS` variable in the `.env` file.

### Year Regex Variable
The automation will try to identify the year of the file by looking for a `YYYY-YYYY` format in the file name. The regex pattern for this is in a variable named `REGEX_PATTERN` near the top of the `main.py` file.

The year identified by the regex will be used in the file path on Google Cloud Storage to separate files by year. If the naming convention ever changes, and the regex fails to find a year, a `ValueError` will be raised. Update the regex pattern to fix this. [Regex101](https://regex101.com/) is a great site for testing patterns.

## Build and Run Job

Build the Docker image by running the following command in the project's root:

```shell
docker build -t dibels-connector .
```

Run the job by running the below command. By default, the automation will look for new files from the last 24 hours.

```shell
docker run --rm -t dibels-connector
```

To get files since a specific date, use the `--since-date` runtime argument and add a date in `YYYY-MM-DD` format:

```shell
docker run --rm -t dibels-connector --since-date 2026-06-01
```

To get all files from the server, use the `--get-all` runtime argument:

```shell
docker run --rm -t dibels-connector --get-all
```