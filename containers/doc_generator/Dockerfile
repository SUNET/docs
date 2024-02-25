FROM debian:bookworm-20231120-slim@sha256:93ff361288a7c365614a5791efa3633ce4224542afb6b53a1790330a8e52fc7d

MAINTAINER victor@sunet.se

EXPOSE 8080/tcp

# Metadata
LABEL version="1.03"
LABEL description="doc_generator"

# Set work dir
WORKDIR /app

# Copy the requirement.txt file needed to install deps
COPY ./requirements.txt /app/requirements.txt

# Install deps
RUN apt-get update \
    && apt-get install -y \
    python3-pip \
    python3-dev \
    python3 \
    build-essential \
    zip \
    git \
    curl \
    wget \
    swig \
    libz-dev \
    dnsutils \
    mercurial \
    python3-venv \
    && python3 -m venv .venv && . .venv/bin/activate \
    && pip3 install --require-hashes -r requirements.txt

    #\
    #&& apt-get remove -y \
    #wget \
    #gcc \
    #python3-pip \
    #python3-dev \
    #&& apt-get autoremove -y

# Remove setuid and setgid
RUN find / -xdev -perm /6000 -type f -exec chmod a-s {} \; || true

# Add user and add to softhsm group
# RUN useradd doc_generator -u 1000 -s /usr/sbin/nologin
# RUN usermod -a -G softhsm pkcs11_ca

# Copy files
COPY ./doc_generator /app/doc_generator
# COPY ./tests /app/tests
# COPY ./data/trusted_keys /app/trusted_keys
# COPY ./containers/healthcheck.sh /app/healthcheck.sh
# COPY ./containers/healthcheck.py /app/healthcheck.py
COPY ./containers/logging.json /app/logging.json
# COPY ./data/tls_certificate.pem /app/tls_certificate.pem
# COPY ./data/tls_key.key /app/tls_key.key


# RUN mkdir -p /app/pages/generating /app/pages/prod
# RUN chown doc_generator -R /app/pages/generating /app/pages/prod


# WORKDIR /app

# Run as user
# USER doc_generator


# Add healthcheck
# HEALTHCHECK --interval=120s --timeout=15s --retries=1 --start-period=30s \
#     CMD sh -c '. .venv/bin/activate && python3 healthcheck.py' || bash -c 'kill -s 15 1 && (sleep 7; kill -s 9 1)'

# CMD sh -c '. .venv/bin/activate && uvicorn src.pkcs11_ca_service.main:app --ssl-keyfile tls_key.key --ssl-certfile tls_certificate.pem --ssl-version 2 --log-config ./logging.json --host 0.0.0.0 --port 443 --workers 1 --header server:pkcs11_ca'

CMD sh -c '. .venv/bin/activate && uvicorn doc_generator.main:app --ssl-keyfile tls_key.key --ssl-certfile tls_certificate.pem --ssl-version 2 --log-config ./logging.json --host 0.0.0.0 --port 443 --workers 1 --header server:pkcs11_ca'
CMD sh -c '. .venv/bin/activate && uvicorn doc_generator.main:app --log-config ./logging.json --host 0.0.0.0 --port 8080 --workers 1'
