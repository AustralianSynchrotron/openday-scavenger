FROM python:3.12-bullseye AS python_base

ENV PYTHONUNBUFFERED 1


# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/0.4.10/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.cargo/bin/:$PATH"

# Extra things needed to run e2e tests in CI
# Ignore this for local/prod development
FROM python_base AS python_e2e

ENV UV_PROJECT_ENVIRONMENT=/root/.cache/uv

WORKDIR /usr/src/app

COPY . .

RUN uv sync --all-extras