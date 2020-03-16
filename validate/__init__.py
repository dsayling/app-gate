from concurrent.futures import ThreadPoolExecutor, as_completed
import pathlib
import logging

ALL_DIRS = {}

class Dir(object):
    """Create one of these for every directory in the root.
    """
    def __init__(self,dependencies, owners, path):
        self.dependencies = dependencies
        self._direct_owners = owners
        self.path = path
        ALL_DIRS[path] = self

    def __repr__(self):
        return f"Dir[{self.path}, {self._direct_owners}]"

    def contains(self,file):
        """Check to see if the directory has the file.
        :returns: bool
        """
        return self.path in file
    
    def has_dependency(self,file):
        """Check to see if the directory has the file.
        :returns: bool
        """
        return any(dep_path in file for dep_path in self.dependencies)

    @property
    def owners(self):
        if self._direct_owners:
            return self._direct_owners   
        parent = self
        owners = []
        while not owners:
            parent = parent.get_parent_directory()
            owners = parent.owners if parent.owners else []
            # if you hit the root, no owners
            if not parent:
                break
        return owners

    def has_approval(self, approvers):
        """Check to see if approvers are allowed to approve this directory.
        :returns: bool
        """
        for a in approvers:
            # get dependecy owners at some point
            if a in self.owners:
                return True
        return False

    def get_parent_directory(self):
        """Get the parent directory object by just 
        :returns: bool
        """
        tmp_path=pathlib.Path(self.path)
        parent_dir = ALL_DIRS.get(f'{tmp_path.parent}/')
        logging.debug(f"Parent dir:{parent_dir}, may not be in tree")
        return parent_dir


def validate(f, approvers, dirs=None):
    """Make sure all the impacted dirs have approval.

    validate('y/file', approvers['A','C']) -> True
    validate('y/file', approvers['B']) -> True
    """
    if not approvers:
        return False
    impacted_dirs = []
    dirs = dirs or []
    for d in dirs:
        # check if dir has file
        if d.contains(f):
            impacted_dirs.append((d, d.has_approval(approvers)))
        # check if file in dir.dependncies
        if d.has_dependency(f):
            impacted_dirs.append((d, d.has_approval(approvers)))
    logging.info(impacted_dirs)
    # check all impacted directories have approval
    return all(_[1] for _ in impacted_dirs)

def validate_approvals(files, approvers, dirs=None):
    """Make sure every file has approval. 
    
    Thread with futures after getting the directory tree.
    Threading to get the path and the dirs wont work since its blocking anyway.

    """
    # get dirs, pathlib.Path.cwd()?
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(validate, _, approvers, dirs) for _ in files]
        results = []
        for future in as_completed(futures):
            results.append(future.result())
        logging.warning(results)

    return all(results)
