FROM python:3.12-bullseye

ENV PYTHONUNBUFFERED 1

# We use uv in Docker to install the dependencies.
# Since uv is so fast we install the dependencies as a postCreateCommand step.
RUN pip install uv
