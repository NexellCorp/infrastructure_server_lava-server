#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  release-queue.py
#
#  Copyright 2014 Linaro Limited
#  Author: Neil Williams <neil.williams@linaro.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import os
import subprocess


def main():
    """
    Change the changes list to call whatever is your preferred
    viewer - however, note that the most useful method will be
    to let gerrit resolve the search into an actual review or
    review list.
    """
    try:
        chk = subprocess.check_call(["git", "log", "-n1"])
    except subprocess.CalledProcessError:
        print "Ensure this script is run from the git working copy."
        return 1
    master = []
    release = []
    pattern = re.compile("\s+Change-Id: (\w+)")
    commit_pattern = re.compile("commit (.+)")
    # Get all commits on master
    subprocess.call(["git", "checkout", "master"])
    lines = subprocess.check_output(["git", "log"])
    for line in lines.split('\n'):
        if "Change-Id" in line:
            m = pattern.match(line)
            master.append(m.group(1))
    # Get all commits on release
    subprocess.call(["git", "checkout", "release"])
    lines = subprocess.check_output(["git", "log"])
    for line in lines.split('\n'):
        if "Change-Id" in line:
            m = pattern.match(line)
            release.append(m.group(1))
    diff = list(set(master) - set(release))
    # Go back to master
    subprocess.call(["git", "checkout", "master"])
    lines = subprocess.check_output(["git", "log"])

    # Print each missing commit with more information
    current_hash = ''
    for change in diff:
        for line in lines.split('\n'):
            # Get the commit hash
            if "commit " in line:
                m = commit_pattern.match(line)
                if m:
                    current_hash = m.group(1)
            # Match the Change-id
            if "Change-Id" in line:
                m = pattern.match(line)
                if change == m.group(1):
                    print "%s => %s" % (change, subprocess.check_output(["git", "show", "--pretty=oneline", current_hash]).split('\n')[0])
                    break

    return 0

if __name__ == '__main__':
    main()
