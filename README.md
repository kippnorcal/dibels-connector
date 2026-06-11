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