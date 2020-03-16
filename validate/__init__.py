#!/usr/bin/env python
"""
A command line utility called validate_approvals that validates that
the correct people have approved changes to a set of files.
It takes arguments via two flags, --approvers and --changed-files. Both flags' arguments are comma separated.

$ validate_approvals --approvers alovelace,ghopper --changed-files src/com/twitter/follow/Follow.java,src/com/twitter/user
"""
from validate import main
import pathlib
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approvers", help="the approvers that have approved", type=str, nargs='+', required=True)
    parser.add_argument("--changed-files", help="the approvers that have approved", type=str, nargs='+', required=True)
    root = pathlib.Path.cwd()
    dirs = main.dir_factory(root)
    args = parser.parse_args()
    if main.check_approvals(args.changed_files, args.approvers, dirs):
        print('Approved')