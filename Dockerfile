# Use the maximum version for which dependency wheels are available
FROM python:3.9-slim

# linkchecker creates ~/.linkchecker/ (700) containing linkcheckerrc et al
ENV HOME /tmp

# Enables access to local files when run with -v "$PWD":/mnt
VOLUME /mnt

WORKDIR /mnt

# Dependencies change on their own schedule so install them separately
RUN pip install --no-cache-dir \
    beautifulsoup4 dnspython pyxdg requests cchardet polib

RUN pip install --no-cache-dir \
   https://github.com/linkchecker/linkchecker/archive/master.zip

ENTRYPOINT ["linkchecker"]
