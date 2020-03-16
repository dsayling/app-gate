from concurrent.futures import ThreadPoolExecutor, as_completed
import pathlib
import logging

ALL_DIRS = {}

def get_data(filename: str) -> list:
    """Get data from a file in list of lines.
    
    Returns empty list if not a file or empty
    """
    if not pathlib.Path(filename).exists():
        return []
    with open(filename, "r") as fh:
        text = fh.read().splitlines()
    return text

def dir_factory(root: pathlib.Path) -> list:
    """Run the path down and load the directories, also, return them as a list
    """
    dirs = []
    for d in root.glob('**'):
        if d.is_dir:
            dirs.append(RealDir.from_path(d))
    return dirs


class Dir(object):
    """Create one of these for every directory in the root.
    """
    def __init__(self,dependencies, owners, path):
        self.dependencies = dependencies
        self._direct_owners = owners
        self.path = path
        self._parent_owners = None
        ALL_DIRS[path] = self

    def __repr__(self):
        return f"Dir[{self.path}, {self._direct_owners}]"

    def contains(self,f):
        """Check to see if the directory has the file.
        :returns: bool
        """
        return self.path in f
    
    def has_dependency(self,f):
        """Check to see if the directory has the file.
        :returns: bool
        """
        return any(dep_path in f for dep_path in self.dependencies)

    @property
    def owners(self):
        if self._parent_owners:
            return self._parent_owners
        parent = self
        owners = self._direct_owners[:]
        while True:
            parent = parent.get_parent_directory()
            if not parent:
                break
            owners.extend(parent.owners) if parent.owners else []
            # if you hit the root, no owners
        logging.warning(f'{self} has {owners}')
        self._parent_owners = owners
        return set(owners)

    def has_approval(self, approvers):
        """Check to see if approvers are allowed to approve this directory.
        :returns: bool
        """
        logging.debug(approvers)
        if not self.owners:
            return True
        for a in approvers:
            if a in self.owners:
                return True
        return False

    def get_parent_directory(self):
        """Get the parent directory object by just 
        :returns: bool
        """
        tmp_path=pathlib.Path(self.path)
        parent_dir = ALL_DIRS.get(f'{tmp_path.parent}/')
        return parent_dir

class RealDir(Dir):

    @classmethod
    def from_path(cls, path):
        """Provide a path, open the files if there."""
        dependencies = get_data(path / 'DEPENDENCIES')
        owners = get_data(path / 'OWNERS')
        return cls(dependencies, owners, path)

    def contains(self, f):
        try:
            next(self.path.glob(f))
        except StopIteration:
            return False
        return True


def check_approval(f, approvers, dirs=None):
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
    logging.critical(impacted_dirs)
    # check all impacted directories have approval
    return all(_[1] for _ in impacted_dirs)

def check_approvals(files, approvers, dirs=None):
    """Make sure every file has approval. 
    
    Thread with futures after getting the directory tree.
    Threading to get the path and the dirs wont work since its blocking anyway.

    """
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_approval, _, approvers, dirs) for _ in files]
        results = []
        for future in as_completed(futures):
            results.append(future.result())
        logging.warning(results)

    return all(results)
