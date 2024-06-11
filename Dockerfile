FROM debian
ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV LANG=C.UTF-8
ENV PYTHON_VERSION=3.11
RUN /bin/sh -c set -eux; apt-get update; apt-get install -y --no-install-recommends ca-certificates curl gnupg netbase sq wget git mercurial openssh-client subversion procps autoconf automake bzip2 default-libmysqlclient-dev dpkg-dev file g++ gcc imagemagick libbz2-dev libc6-dev libcurl4-openssl-dev libdb-dev libevent-dev libffi-dev libgdbm-dev libglib2.0-dev libgmp-dev libjpeg-dev libkrb5-dev liblzma-dev libmagickcore-dev libmagickwand-dev libmaxminddb-dev libncurses5-dev libncursesw5-dev libpng-dev libpq-dev libreadline-dev libsqlite3-dev libssl-dev libtool libwebp-dev libxml2-dev libxslt-dev libyaml-dev make patch unzip xz-utils zlib1g-dev libbluetooth-dev tk-dev uuid-dev python3 python3-pip python3-pandas python3-pandas-lib python3-jira python3-openpyxl python3-lxml python3-pretty-yaml; rm -rf /var/lib/apt/lists/* # buildkit
RUN /bin/sh -c set -eux; for src in idle3 pydoc3 python3 python3-config; do dst="$(echo "$src" | tr -d 3)"; [ -s "/usr/local/bin/$src" ]; [ ! -e "/usr/local/bin/$dst" ]; ln -svT "$src" "/usr/local/bin/$dst"; done # buildkit
CMD ["python3", "/usr/local/sbin/server.py"]
