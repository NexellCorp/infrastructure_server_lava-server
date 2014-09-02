#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  version.py
#
#  Copyright 2014 Neil Williams <codehelp@debian.org>
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
#


import subprocess
import os
import datetime


def version_tag():
    """
    Parses the git status to determine if this is a git tag
    or a developer commit and builds a version string combining
    the two. If there is no git directory, relies on this being
    a directory created from the tarball created by setup.py when
    it uses this script and retrieves the original version string
    from that.
    :return: a version string based on the tag and date
    """
    if not os.path.exists("./.git/"):
        base = os.path.basename(os.getcwd())
        name_list = ['grep', 'name=', 'setup.py']
        name_data = subprocess.check_output(name_list).strip()
        name_data = name_data.replace("name=\'", '')
        name_data = name_data.replace("\',", '')
        return base.replace("%s-" % name_data, '')
    tag_list = [
        'git', 'for-each-ref', '--sort=taggerdate', '--format',
        "'%(refname)'", 'refs/tags',
    ]
    hash_list = ['git', 'log', '-n', '1']
    tag_hash_list = ['git', 'rev-list']
    clone_data = subprocess.check_output(hash_list).strip()
    commits = clone_data.split('\n')
    clone_hash = commits[0].replace('commit ', '')[:8]
    tag_data = subprocess.check_output(tag_list).strip()
    tags = tag_data.split('\n')
    if len(tags) < 2:
        return clone_hash
    tag_line = str(tags[len(tags) - 1]).replace('\'', '').strip()
    tag_name = tag_line.split("/")[2]
    tag_hash_list.append(tag_name)
    tag_hash = subprocess.check_output(tag_hash_list).strip()
    tags = tag_hash.split('\n')
    tag_hash = tags[0][:8]
    if tag_hash == clone_hash:
        return tag_name
    else:
        dev_time = datetime.datetime.utcnow()
        # our tags are one month behind, 04 is tagged in 05
        # however, the tag is not necessarily made on the first day of 05
        # so if out by two, allow for an "extended month" to ensure
        # an incremental version
        bits = tag_name.split('.')
        tag_month = int(bits[1])
        extended = dev_time.day
        if int(dev_time.month) - 1 > tag_month:
            extended = int(dev_time.day) + 31
        delayed_tag = "%d.%02d" % (dev_time.year, dev_time.month)
        return "%s.%02d.%02d" % (tag_name, extended, dev_time.hour)


def main():
    print version_tag()
    return 0

if __name__ == '__main__':

    main()
