"""
A command line utility called validate_approvals that validates that
the correct people have approved changes to a set of files.
It takes arguments via two flags, --approvers and --changed-files. Both flags' arguments are comma separated.

$ validate_approvals --approvers alovelace,ghopper --changed-files src/com/twitter/follow/Follow.java,src/com/twitter/user
"""
from validate import main
