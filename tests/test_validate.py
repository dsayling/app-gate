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
import os
import pathlib

from validate import main

import pytest

logging.basicConfig(level = logging.DEBUG)
TEST_ROOT=pathlib.Path(__file__).parent / 'repo_root'

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

class v:
    dependencies = []
    owners = []
    path = 'v/'

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
        (['A','C'], True),
        (['A','D'], False),
        (['B','D'], False),
        (['B','C'], True),
        (['B','C','D'], True),
        (['B','C','A'], True),
        (['A','B'], False)
        ]

class case7:

    f=['z/a/b/file', 'z/a/file']

    tests = [
        (['A'], False),
        (['B'], False),
        (['C'], True),
        (['D'], False),
        (['A','C'], True),
        (['A','D'], False),
        (['D','A'], False),
        (['D','C'], True),
        (['C','D'], True),
        (['B','C'], True),
        (['B','C','D'], True),
        (['A','C','D'], True),
        (['A','B'], False)
        ]

class case8:
    # use case where there is no owners

    f=['v/file']

    tests = [
        ([], False),
        (['A'], True),
        (['B'], True),
        (['C'], True),
        (['D'], True),
        (['A','C'], True),
        (['A','D'], True),
        (['C','D'], True),
        (['D','C'], True),
        (['B','C'], True),
        (['B','C','D'], True),
        (['A','C','D'], True),
        (['A','B'], True)
        ]


        

def case_factory(cs=[case1, case2, case3, case4, case5, case6, case7, case8]):
    # test case factory
    # files, approvers, expected result
    # func('y/file', approvers['B']) -> True
    cases=[]
    for c in cs:
        for t in c.tests:
            cases.append((c.f, t[0], t[1]))
    return cases

@pytest.mark.parametrize("files,approvers,expected", case_factory())
def test_main(files, approvers, expected):
    dirs = [main.Dir(_.dependencies, _.owners, _.path) for _ in [x, y, z, za, zac, zab, v]]
    assert expected == main.check_approvals(files, approvers, dirs)

@pytest.mark.parametrize("base, parent", [('z/a/c','z/a/'),('z/a/','z/'),('z/',None)])
def test_parent(base, parent):
    base=main.ALL_DIRS.get('z/a/c/')
    parent=main.ALL_DIRS.get('z/a/')
    assert base.get_parent_directory() == parent

def test_from_path():
    d = main.RealDir.from_path(TEST_ROOT / 'src/com/twitter/follow/', TEST_ROOT)
    assert d._direct_owners == ['alovelace', 'ghopper']
    assert any(['src/com/twitter/user' in str(_) for _ in d.dependencies])
    assert d.get_parent_directory() == None

def test_real_traverse():
    main.ALL_DIRS = {}  # hack to reset, love references
    test_root = TEST_ROOT
    dirs = main.dir_factory(test_root)

    assert len(dirs) == len(main.ALL_DIRS)

class AcceptCase1:
    f=['src/com/twitter/follow/Follow.java','src/com/twitter/user/User.java']
    tests = [
        (['alovelace', 'ghopper'], True),
        (['alovelace', 'ghopper', 'mfox'], True),
        ]

class AcceptCase2:
    f=['src/com/twitter/follow/Follow.java']
    tests = [
        (['alovelace'], False),
        (['eclarke'], False),
        (['eclarke', 'alovelace'], True),
        (['alovelace', 'eclarke'], True),
        ([], False),
        ]

class AcceptCase3:
    f=['src/com/twitter/tweet/Tweet.java']
    tests = [
        (['mfox'], True),
        ]

def test_owners():
    [main.Dir(_.dependencies, _.owners, _.path) for _ in [x, y, z, za, zac, zab, v]]
    d=main.ALL_DIRS.get(zab.path)
    assert d.owners == set(['C', 'D'])
    d=main.ALL_DIRS.get(zac.path)
    assert d.owners == set(['B', 'C'])

@pytest.mark.parametrize("files,approvers,expected", case_factory([AcceptCase1, AcceptCase2, AcceptCase3]))
def test_real(files, approvers, expected):
    dirs = main.dir_factory(TEST_ROOT)
    assert expected == main.check_approvals(files, approvers, dirs)

@pytest.mark.parametrize("files,approvers,expected", case_factory([AcceptCase1, AcceptCase2, AcceptCase3]))
def test_real_single(files, approvers, expected):
    dirs = main.dir_factory(TEST_ROOT)
    assert expected == main.check_approval(files[0], approvers, dirs)

def test_contains():
    main.dir_factory(TEST_ROOT)
    p = TEST_ROOT / 'src/com/twitter/follow/'
    d = main.ALL_DIRS.get(p)
    f = TEST_ROOT / 'src/com/twitter/follow/Follow.java'
    f1 = TEST_ROOT / 'src/com/twitter/follow/OWNERS'
    f2 = TEST_ROOT / 'src/com/twitter/gah'
    f3 = TEST_ROOT / 'tests/com/twitter/follow/Follow.java'
    assert d.contains(f)
    assert d.contains(f1)
    assert not d.contains(f2)
    assert not d.contains(f3)

def test_contains2():
    main.dir_factory(TEST_ROOT)
    p = TEST_ROOT / 'src/com/'
    d = main.ALL_DIRS.get(p)
    f2 = TEST_ROOT / 'src/com/twitter'
    f3 = TEST_ROOT / 'tests/com/twitter/follow/Follow.java'
    f4 = TEST_ROOT / 'src/com/twitter/followa/Follow.java'
    assert not d.contains(f2)
    assert not d.contains(f3)
    assert not d.contains(f3)
    assert not d.contains(f4)

            