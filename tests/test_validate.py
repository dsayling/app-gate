import pathlib
import logging
import os

import pytest

logging.basicConfig(level = logging.DEBUG)

class Dir:
    path=''
    owners=[]
    dependencies=[]

    def contains(self,x):
        """Check to see if the directory has the file"""
        return self.path in x
    
    def has_approval(self, approvers):
        for a in approvers:
            if a in self.owners:
                return True
        return False

class x(Dir):
    dependencies = ['y',]
    owners = ['A', 'B']
    path = 'x/'

class y(Dir):
    dependencies = []
    owners = ['B', 'C']
    path = 'y/'

class z(Dir):
    dependencies = []
    owners = ['C']
    path = 'z/'


#   x/
#     DEPENDENCIES = "y\n"
#     OWNERS = "A\nB\n"
#   y/
#     OWNERS = "B\nC\n"
#     file
#   func('y/file', approvers['A','C']) -> True
#   func('y/file', approvers['B']) -> True

class case1:
#   func('y/file', approvers['A','C']) -> True
#   func('y/file', approvers['B']) -> True

    f=['y/file']

    tests = [
        (['A'], False),
        (['B'], True),
        (['C'], False),
        (['A','C'], True),
        (['B','C'], True),
        (['A','B'], True)
        ]

class case2:
#   func('x/file', approvers['A','C']) -> True
#   func('x/file', approvers['C']) -> False
    f=['x/file']

    tests = [
        (['A'], True),
        (['B'], True),
        (['C'], False),
        (['A','C'], True),
        (['B','C'], True),
        (['A','B'], True)
        ]
dirs = [x(), y(), z()]
        
def validate(f, approvers):
    """Make sure all the impacted dirs have approval.

    validate('y/file', approvers['A','C']) -> True
    validate('y/file', approvers['B']) -> True
    """
    impacted_dirs = []
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

def case_factory():
    # test case factory
    # files, approvers, expected result
    # func('y/file', approvers['B']) -> True
    cases=[]
    for c in [case1, case2]:
        for t in c.tests:
            cases.append((c.f, t[0], t[1]))
    return cases

@pytest.mark.parametrize("files,approvers,expected", case_factory())
def test_it(files, approvers, expected):
    assert expected == validate(files[0], approvers)




