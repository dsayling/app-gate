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

dirs = [validate.Dir(_.dependencies, _.owners, _.path) for _ in [x, y, z]]
        

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
    assert expected == validate.validate(files[0], approvers, dirs)




