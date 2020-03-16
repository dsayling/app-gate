from concurrent.futures import ThreadPoolExecutor, as_completed
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
