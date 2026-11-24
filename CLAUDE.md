# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-script job (`main.py`) that pulls DIBELS progress-monitoring CSVs from an SFTP server and uploads them to Google Cloud Storage. It runs in Docker on a remote server; there is no test suite or linter configured.

## Commands

```shell
docker build -t dibels-connector .
docker run --rm -t dibels-connector                          # files modified in the last 24h
docker run --rm -t dibels-connector --since-date 2026-06-01  # files modified since a date
```

The README still documents `--get-all`, but that flag was removed from `main.py`; only `--since-date` exists.

Dependencies are managed with Pipenv (Python 3.14). The Dockerfile runs `pipenv install --skip-lock`, so `Pipfile.lock` is not used in the image build.

## How it works

- Config comes entirely from environment variables (see the `.env` section in README.md): SFTP creds (`HOST`, `PORT`, `USER`, `PASS`, `REMOTE_DIR`, `HOST_KEY`), GCS (`BUCKET`, `CLOUD_STORAGE_BASE_PATH`, `GOOGLE_APPLICATION_CREDENTIALS`), and Mailgun vars consumed by `job_notifications`.
- `HOST_KEY` is a base64-encoded RSA public key, pinned explicitly into paramiko's host keys as `[HOST]:PORT` before connecting.
- For each file in `REMOTE_DIR` whose `st_mtime` is newer than the query time, the school year (`YYYY-YYYY`, via `REGEX_PATTERN`) is extracted from the remote filename. If no year is found, `_extract_year` raises `ValueError`. The file is downloaded to `/code/data/` (the connector only ever runs in Docker, so this hardcoded container path is intended), read with pandas as all-string columns, and uploaded to `{CLOUD_STORAGE_BASE_PATH}/{year}/dibels_progress_monitoring_{year}.csv`. Each run overwrites the blob for that year.
- `gbq_connector.CloudStorageClient` and `job_notifications.create_notifications` are internal KIPP NorCal packages from PyPI. Success and failure both send a Mailgun email; failures include the stack trace. Logs go to `app.log` and stdout, and `app.log` is attached to the notification.
## Deployment

On every push to `main`, `.github/workflows/deploy.yml` SSHes into the host server, hard-resets to `origin/main`, and rebuilds the Docker image. Scheduling of the container happens outside this repo.
