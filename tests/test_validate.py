#   x/
#     DEPENDENCIES = "y\n"
#     OWNERS = "A\nB\n"
#   y/
#     OWNERS = "B\nC\n"
#     file
#   func('y/file', approvers['A','C']) -> True
#   func('y/file', approvers['B']) -> True
#   func('x/file', approvers['A','C']) -> True
#   func('x/file', approvers['C']) -> False

import logging
import validate

import pytest

logging.basicConfig(level = logging.DEBUG)


class x:
    dependencies = ['y',]
    owners = ['A', 'B']
    path = 'x/'

class y:
    dependencies = []
    owners = ['B', 'C']
    path = 'y/'

class z:
    dependencies = []
    owners = ['C']
    path = 'z/'

class za:
    dependencies = []
    owners = []
    path = 'z/a/'

class zab:
    dependencies = ['z/a/c']
    owners = ['D']
    path = 'z/a/b/'

class zac:
    dependencies = []
    owners = ['B']
    path = 'z/a/c/'

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
    
class case3:
    f=['y/file', 'z/file']

    tests = [
        (['A'], False),
        (['B'], False),
        (['C'], False),
        (['A','C'], True),
        (['B','C'], True),
        (['A','B'], False)
        ]

# now we have cases where we need to look at the parent dir for approval
# add some more complicate scenarious based on some examples in root_dir
# realizing at this point I should have created some test case templates to help

class case4:
    f=['z/a/file']

    tests = [
        (['A'], False),
        (['B'], False),
        (['C'], True),
        (['A','C'], True),
        (['B','C'], True),
        (['B','C'], True),
        (['A','B'], False)
        ]

class case5:

    f=['z/a/file', 'x/file']

    tests = [
        (['A'], False),
        (['B'], False),
        (['C'], False),
        (['A','C'], True),
        (['B','C'], True),
        (['A','B'], False)
        ]

class case6:

    f=['z/a/c/file', 'y/file']

    tests = [
        (['A'], False),
        (['B'], False),
        (['C'], False),
        (['D'], False),
        (['A','C'], False),
        (['A','D'], False),
        (['B','D'], False),
        (['B','C'], False),
        (['B','C','D'], True),
        (['A','B'], False)
        ]

class case7:

    f=['z/a/b/file', 'z/a/file']

    tests = [
        (['A'], False),
        (['B'], False),
        (['C'], False),
        (['D'], False),
        (['A','C'], False),
        (['A','D'], False),
        (['C','D'], True),
        (['B','C'], False),
        (['B','C','D'], True),
        (['A','C','D'], True),
        (['A','B'], False)
        ]


dirs = [validate.Dir(_.dependencies, _.owners, _.path) for _ in [x, y, z, za, zac, zab]]
        

def case_factory():
    # test case factory
    # files, approvers, expected result
    # func('y/file', approvers['B']) -> True
    cases=[]
    for c in [case1, case2, case3, case4, case5, case6, case7]:
        for t in c.tests:
            cases.append((c.f, t[0], t[1]))
    return cases

@pytest.mark.parametrize("files,approvers,expected", case_factory())
def test_it(files, approvers, expected):
    assert expected == validate.validate_approvals(files, approvers, dirs)

@pytest.mark.parametrize("base, parent", [('z/a/c','z/a/'),('z/a/','z/'),('z/',None)])
def test_parent(base, parent):
    base=validate.ALL_DIRS.get('z/a/c/')
    parent=validate.ALL_DIRS.get('z/a/')
    assert base.get_parent_directory() == parent
