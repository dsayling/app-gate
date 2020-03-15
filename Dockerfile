FROM python:3.7

COPY tests/requirements.txt /workspace/tests/requirements.txt

RUN pip install --upgrade pip \
    && pip install -r /workspace/tests/requirements.txt

COPY tests /workspaces/tests

WORKDIR /workspaces/tests

CMD pytest