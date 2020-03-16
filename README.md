# validate_approvals
A command line utility called validate_approvals that validates that
the correct people have approved changes to a set of files.
It takes arguments via two flags, --approvers and --changed-files.
Both flags' arguments are comma separated.

# main

## setup

Requires python:3.6 or higher

```
git clone https://github.com/dsayling/app-gate
cd app-gate
pip3 install . # or whatever pip is available
```

## use it
$ validate_approvals --approvers alovelace,ghopper
             --changed-files src/com/twitter/follow/Follow.java,src/com/twitter/user
only works when files are from current dir


# docker acceptance tests

requires docker
```
docker build -t app-gate .
docker run -it app-gate
```


