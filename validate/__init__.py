import logging

class Dir(object):
    """Create one of these for every directory in the root.
    """
    path=''
    def __init__(self,dependencies, owners, path):
        self.dependencies = dependencies
        self._direct_owners = owners
        self.path = path

    def contains(self,x):
        """Check to see if the directory has the file."""
        return self.path in x
    
    def has_approval(self, approvers):
        for a in approvers:
            # get dependecy owners at some point
            if a in self._direct_owners:
            # if a in self.owners:
                return True
        return False

def validate(f, approvers, dirs=None):
    """Make sure all the impacted dirs have approval.

    validate('y/file', approvers['A','C']) -> True
    validate('y/file', approvers['B']) -> True
    """
    impacted_dirs = []
    dirs = dirs or []
    for d in dirs:
        # check if dir has file
        if d.contains(f):
            impacted_dirs.append((d, d.has_approval(approvers)))
        # check if file in dir.dependncies
        if any(dep_path in f for dep_path in d.dependencies):
            impacted_dirs.append((d, d.has_approval(approvers)))
    logging.info(impacted_dirs)
    # check all impacted directories have approval
    return all(_[1] for _ in impacted_dirs)