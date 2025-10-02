# Use the maximum Python version tested
FROM python:3.13-slim

# linkchecker creates $XDG_CONFIG_HOME/linkchecker/ (700) containing linkcheckerrc et al
ENV HOME=/tmp

# Enables access to local files when run with -v "$PWD":/mnt
VOLUME /mnt

WORKDIR /mnt

# Dependencies change on their own schedule so install them separately
RUN pip install --no-cache-dir beautifulsoup4 dnspython requests polib

RUN set -x \
    && apt-get update -qq \
    && apt-get install -y -qq --no-install-recommends git \
    && pip install --no-cache-dir git+https://github.com/linkchecker/linkchecker.git \
    && apt-get -y -qq purge git \
    && apt-get autoremove -y -qq \
    && apt-get clean -y -qq all \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["linkchecker"]
