# app-gate


# app requirements

* pip installable so I can easily add an executable to the path
* acceptance tests per the give examples that run on the command
* dockerfile to easily demonstrate without doing anything complicated  

# validate

## mock root
   x/
     DEPENDENCIES = "y\n"
     OWNERS = "A\nB\n"
   y/
     OWNERS = "B\nC\n"
     file
If a change modifies y/file, it affects both directories y (contains file) and x (depends on y). This change must at a minimum be approved by either B alone (owner of x and y) or both A (owner of x) and C (owner of y).

if y/file is changed, then A and C or B must accept.


## rules

1. A change is approved if all of the affected directories are approved.
2. A directory is considered to be affected by a change if either: (1) a file in that directory was changed, or (2) a file in a (transitive) dependency directory was changed.
3. In case (1), we only consider changes to files directly contained within a directory, not files in subdirectories, etc.
4. Case (2) includes transitive changes, so a directory is also affected if a dependency of one of its dependencies changes, etc.
5. A directory has approval if at least one engineer listed in an OWNERS file in it or any of its parent directories has approved it.

## functional
1. grab all the Dirs that require approval
2. Dirs that require approval are directories that have a file that's been touched, Dir.has_file(touched_file) or if the file is in a Dir.dependency field
3. Dirs have approval if any reviewer is in the Dir.owners

# filetree

figure out the file tree code later
use pathlib and iterate and instansiate and read the files as you go
gonna be interesting to link them together

