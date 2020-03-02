If you do not want to install any additional libraries/dependencies you can use the Docker image.

Example for external web site check:
```docker run --rm -it -u $(id -u):$(id -g) linkchecker/linkchecker --verbose https://google.com```

Local HTML file check:
``docker run --rm -it -u $(id -u):$(id -g) -v "$PWD":/mnt linkchecker/linkchecker --verbose index.html``
