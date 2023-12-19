#!/usr/bin/env python3

# Use heuristics to identify new files that maybe binaries.
# Flagged files need to be manually inspected and either added to the
# ignore list (because they are safe to redistribute), or to the reject list
# (so that they'll be removed prior to orig.tar.xz generation).

import glob
import os
import re
import sys


if __name__ == '__main__':
    ret = 0
    top = './'

    ignorelist = []
    with open('./debian/binary-check.ignore', 'r') as f:
        ignoreglobs = list(map(lambda s: s.strip(), f.readlines()))
    for pattern in ignoreglobs:
        matches = glob.glob(pattern, recursive=True, include_hidden=True)
        if len(matches) == 0:
            print(
                f"WARNING: pattern {pattern} matched no files.",
                file=sys.stderr,
            )
        ignorelist += matches

    for root, dirs, files in os.walk(top):
        for name in files:
            relpath = os.path.join(root, name)[len(top):]
            if relpath in ignorelist:
                continue
            sys.stdout.write(
                "WARNING: Possible binary %s\n" %
                (os.path.join(root, name))
            )
            ret = -1
    sys.exit(ret)
