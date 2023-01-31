# -----------------------------------
# Requirements stage
FROM python:3.9-slim as builder

# Install all dependencies
RUN apt-get update -y && \
    apt-get install -y python3-dev \
    python3-pip && \
    pip3 install --upgrade pip && \
    mkdir -p /opt/python3-requirements

WORKDIR /opt/python3-requirements
COPY ./requirements.txt .
RUN python -m venv /opt/python3-requirements/venv

ENV PATH="/opt/python3-requirements/venv/bin:$PATH"
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install -r requirements.txt

# -----------------------------------
# Install application sources and run
FROM python:3.9-slim

RUN useradd -m -d /home/appuser/ appuser && \
    mkdir -p /home/appuser/app && \
    chown appuser /home/appuser/app

USER appuser
WORKDIR /home/appuser/app

# Get preinstalled environment from requirements stage
COPY --from=builder --chown=appuser:appuser /opt/python3-requirements .
# Get application sources
COPY --chown=appuser:appuser ./wlib ./wlib
COPY --chown=appuser:appuser ./wfaker.py .

ENV PATH="/home/appuser/app/venv/bin:$PATH"
CMD ["python", "wfaker.py", "-c"]
