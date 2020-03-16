# making this to get some acceptance env
FROM python:3.7

# copy the test requirementes as I dont expect that to change
COPY tests/requirements.txt /workspaces/tests/requirements.txt

RUN pip install --upgrade pip \
    && pip install  -r /workspaces/tests/requirements.txt

# copy the tests then the project, could be more efficient with this 
COPY tests /workspaces/tests
COPY . /tmp/validate_approvals/

# install the pacakge into the path
RUN pip install /tmp/validate_approvals/

WORKDIR /workspaces/tests

CMD pytest