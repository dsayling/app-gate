from concurrent.futures import ThreadPoolExecutor, as_completed
import pathlib
import logging

# globals ALL_DIRS
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

def dir_factory(root: pathlib.Path) -> set:
    """Run the path down and load the directories, also, return them as a list
    """
    global ALL_DIRS
    ALL_DIRS = {}
    dirs = []
    for d in root.glob('**'):
        if d.is_dir():
            dirs.append(RealDir.from_path(d, root))
    logging.error(ALL_DIRS.values())
    return ALL_DIRS.values()

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
        return f"Dir<{self.path}, {self._direct_owners}>"

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
        """Navigate the owners tree"""
        if self._parent_owners:
            return self._parent_owners
        parent = self.get_parent_directory()
        owners = self._direct_owners[:]
        while True:
            if not parent:
                break
            owners.extend(parent.owners) if parent.owners else []
            parent = parent.get_parent_directory()
            # if you hit the root, no owners
        self._parent_owners = owners
        return set(owners)

    def has_approval(self, approvers):
        """Check to see if approvers are allowed to approve this directory.
        :returns: bool
        """
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
        assert parent_dir is not self
        return parent_dir

class RealDir(Dir):

    def __init__(self,dependencies, owners, path, root):
        super().__init__(dependencies, owners, path)
        self.root = root

    @classmethod
    def from_path(cls, path, root):
        """Provide a path, open the files if there."""
        # terrible pattern but easy here
        existing = ALL_DIRS.get(path)
        if existing:
            logging.debug(f'found {existing}')
            return existing
        dependencies = get_data(path / 'DEPENDENCIES')
        # load dependencies onto root path
        dependencies = [root / _ for _ in dependencies]
        owners = get_data(path / 'OWNERS')
        return cls(dependencies, owners, path, root)

    def contains(self, f):
        """check the file's dir, wrt root, and compare with path"""
        v = self.root / f
        return self.path == v.parent and v.is_file()
    
    def has_dependency(self, f):
        """look up depdencies from globals.
        
        warning: you need to instantiate all the directories first.
        :returns: bool
        """
        dep_dirs = [ALL_DIRS.get(x) for x in self.dependencies]
        for r in dep_dirs:
            if r and r.contains(f):
                return True
        return False

    def get_parent_directory(self):
        """Get the parent directory object by just taking that paretn pathlib and get from glogals. 
        warning: you need to instantiate all the directories first.
        :returns: bool
        """
        parent_dir = ALL_DIRS.get(self.path.parent)
        return parent_dir


def check_approval(f, approvers, dirs=None):
    """Make sure all the impacted dirs have approval.

    validate('y/file', approvers['A','C']) -> True
    validate('y/file', approvers['B']) -> True
    """
    if not approvers:
        return False
    if ',' in approvers[0]:  # hack, happning on last acceptnace test, idc now!
        approvers = approvers[0].split(',')
    impacted_dirs = []
    dirs = dirs or []
    for d in dirs:
        # check if dir has file
        if d.contains(f):
            impacted_dirs.append((d, d.has_approval(approvers)))
        # check if file in dir.dependncies
        if d.has_dependency(f):
            impacted_dirs.append((d, d.has_approval(approvers)))
    # check all impacted directories have approval
    # logging.warning(f'{impacted}')
    for x in impacted_dirs:
        if not x[1]:
            logging.debug(f'{x[0]} not approved')
        if x[1]:
            logging.debug(f'{x[0]} approved')
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

    return all(results)

def call_args(args, dirs):
    files = args.files[0]
    # files = args.files[0].split(',')
    approvers = args.approvers[0]
    # approvers = args.approvers[0].split(',')
    logging.error(approvers)
    logging.error(files)
    return check_approvals(files, approvers, dirs)