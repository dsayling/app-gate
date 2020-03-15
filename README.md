# app-gate

# setup

Requires python:3.6 or higher

```
git clone https://github.com/dsayling/app-gate
cd app-gate
pip3 install . # or whatever pip is available

pip install https://github.com/dsayling/app-gate
```

# docker acceptance tests

## build it

requires docker
```
docker build -t app-gate .
docker run -it app-gate
```


