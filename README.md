# democrance-api-coding-test

[![Python: 3.12](https://img.shields.io/static/v1?label=python&message=3.12&color=success&style=flat&logo=python)](https://python.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

This repo is for the Democrance API test.

The [sequence diagram](https://sequencediagram.org/index.html#initialData=C4S2BsFMAIBFILYHsDGAnAhgOxTYkBnYAKFIAcM1QUQKthoAhNJAdwMjWIqpBroYBBAAoBJYgBMMwDACMMHOI1IBeFdADCAVyJIEnaOkjSQSLNDXEA5iy1loAYgAMTgKyuXmncD0GHrAAswGABtAHoMMhAwgDcARjCjaUgAfRRvXzQwgF1iZjYONABaAD4RUQAuDTRjfC9dfTRoYiwkOqQYg3z2TgAacoroAG8AHXNoCYAiADMQNCIUrAx9ScHJxkgsSd6xianwBWBF5chV6EmAZR8Aa0Jt3b3JiSRZM8mAJlcipwA2IriAJwAuKTMYAX2I5VKsEYFWIMKKpQGkLEiJK3UKFQAUhcAPIAOWgNQIZDMilYYAChgyjWgEkgMhA4AIxE2ElU6gAilo2jAkqAzBYVNZbPZnC43K5oNzeY5AsFoOFItF4mEAI48-A5PIsHrFMpiQbVWowDW8lqyjpdXWFfqG0bjKbpBqcFIgCRnOI7R3nYAATzIpzWgfmZgw4CKGBQNHp9FBWAhUJKMLhCKRhpRojRGM42LxhOJpKw5Mp0DNdXpjOZrKw7I50EE0cgZAY5ZglhsSDsjncEqcDabLelmpg-iCdSVUViCTb2pz+oGjdwQ7bFvanSa87tlQde3ObbdHsGXoeUyI0h0byjy-wHvBmehsPhjDRyKhpXneYJRMIRZLwCpa9m1vMsRzpBkMCZFk2XrYQMD9UDZQ7UUe3cDx+zghCZTqMcFUnFUZxHOcbU4dNKkwxD8DXGArU3Ei0G3Cpd0eA93U9b090mc9gEvNYo1ATp40TVFkyfNMDUqB8P3or8C1-MkYApADoAod1KJgStIOrGDiDUaAABkQCIFSkHAPgQEIIURS7MU0NcaZpgMoyGFJMyaEs3CJwiKdVVc8zCDCAB+Z0fEaQ8VDiXJ5zIioAHEGWgYRTP8lkkxTZ9Xwzd90RknFv0LBToCUqkzOMpBHJCzIAHICBMtyLOg2tYOSlAEM0qCrM7bsHCBAAWXrPCSty2ogjrPNCbyCLCPz3IIMIEii+iYvihghr4P0H1E1MXxiqScoKXM8rkklCuKur1vAqtGrrPS1ta6Agl0NAEOQmzUP6waWoQx6fGeuVxwm5Vp2mlqGvmsIfqQZ7iIOhdDRWxKvs29LxLfVFpNh2SfxO4tFNLGbvucqGNpg2Q2lCnhqFobBgFqoA)
shows some of the possible API requests and responses this project aims for.

## Table of contents
- [Quick Start](#quick-start)
- [Testing](#testing)

## Quick Start
- Clone the repository
    ```shell
    git clone https://github.com/king-phyte/democrance-api-coding-test.git
    ```

- Move into the directory
    ```shell
    cd democrance-api-coding-test
    ```

- Set up a virtual environment with [Poetry](https://python-poetry.org/docs/) and install the project dependencies (from the `poetry.lock` file to ensure deterministic builds)
  ```shell
  poetry install --no-root --sync
  ```

- Run the migrations
    ```shell
    poetry run python manage.py makemigrations
    poetry run python manage.py migrate
    ```

- Start the server
    ```shell
    poetry run python manage.py runserver localhost:8000
    ```
  *Note:* Starting the server on a privileged port (e.g. 80) may not be accessible unless you run as root.
  Visit [Django's docs](https://docs.djangoproject.com/en/5.0/ref/django-admin/#runserver) for more information.



## Testing

1. Install dev dependencies
    ```shell
    poetry install --with dev --sync --no-root
    ```

2. Install and run [pre-commit hooks](https://pre-commit.com/)
    ```shell
    poetry run pre-commit install --install-hooks
    poetry run pre-commit run --all-files
    ```

3. Run the tests with coverage reporting
    ```shell
    poetry run coverage run manage.py test api
    poetry run coverage report
    ```
