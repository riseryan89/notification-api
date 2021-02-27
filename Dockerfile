# ------------------------------------------------------------------------------
# Base image
# ------------------------------------------------------------------------------
FROM python:3.8-slim AS base

# ------------------------------------------------------------------------------
# Install dependencies
# ------------------------------------------------------------------------------
FROM base AS deps
COPY requirements.txt ./
RUN apt update > /dev/null && \
        apt install -y build-essential && \
        pip install --disable-pip-version-check -r requirements.txt

# ------------------------------------------------------------------------------
# Final image
# ------------------------------------------------------------------------------
FROM base
WORKDIR /usr/src/app
COPY . /usr/src/app

COPY --from=deps /root/.cache /root/.cache
RUN pip install --disable-pip-version-check -r requirements.txt && \
        rm -rf /root/.cache

EXPOSE 5000

CMD ["gunicorn", "--preload", "-c", "gunicorn.conf.py", "app.main:create_app()"]

