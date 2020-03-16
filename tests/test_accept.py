"""
Build a command line utility called validate_approvals that validates that the correct people have approved changes to a set of files.

It will take arguments via two flags, --approvers and --changed-files. Both flags' arguments are comma separated.

As an example, the following is expected to work on the example directory structure we have provided to you.

$ validate_approvals --approvers alovelace,ghopper --changed-files src/com/twitter/follow/Follow.java,src/com/twitter/user
"""
import subprocess
import os
import unittest
import logging

logging.basicConfig(level = logging.DEBUG)
TEST_ROOT=os.path.join(os.path.dirname(__file__), 'repo_root')


def run_cmd(cmd, cwd=TEST_ROOT):
    """Runs and returns stdout"""
    response = subprocess.run(cmd.split(' '), cwd=cwd, capture_output=True, text=True)
    return response.stdout.strip()

class TestAccept(unittest.TestCase):

    def test_sanity(self):
        """
        ls src/com/twitter/follow/
        """

        cmd="ls src/com/twitter/follow/"
        stuff = run_cmd(cmd).split(' ').sort()
        assert stuff == 'DEPENDENCIES  Follow.java  OWNERS'.split(' ').sort()

    def test_0(self):
        """
        $ validate_approvals --approvers alovelace,ghopper --changed-files src/com/twitter/follow/Follow.java,src/com/twitter/user/User.java
        Approved
        """
        result = ""
        cmd = "validate_approvals --approvers alovelace,ghopper --changed-files src/com/twitter/follow/Follow.java,src/com/twitter/user/User.java"
        result = run_cmd(cmd)
        assert result == "Approved"

    def test_1(self):
        """
        $ validate_approvals --approvers alovelace --changed-files src/com/twitter/follow/Follow.java
        Insufficient approvals
        """
        result = ""
        cmd='validate_approvals --approvers alovelace --changed-files src/com/twitter/follow/Follow.java'
        result = run_cmd(cmd)
        assert result == "Insufficient approvals"

    def test_2(self):
        """
        $ validate_approvals --approvers eclarke --changed-files src/com/twitter/follow/Follow.java
        Insufficient approvals
        """
        result = ""
        cmd='validate_approvals --approvers eclarke --changed-files src/com/twitter/follow/Follow.java'
        result = run_cmd(cmd)
        assert result == "Insufficient approvals"

    def test_3(self):
        """
        $ validate_approvals --approvers alovelace,eclarke --changed-files src/com/twitter/follow/Follow.java
        Approved
        """
        result = ""
        cmd='validate_approvals --approvers alovelace,eclarke --changed-files src/com/twitter/follow/Follow.java'
        result = run_cmd(cmd)
        assert result == "Approved"

    def test_4(self):
        """
        $ validate_approvals --approvers mfox --changed-files src/com/twitter/tweet/Tweet.java
        Approved
        """
        result = ""
        cmd='validate_approvals --approvers mfox --changed-files src/com/twitter/tweet/Tweet.java'
        result = run_cmd(cmd)
        assert result == "Approved"