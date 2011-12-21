#!/usr/bin/env python
"""\
Git patch to HG changeset patch converter.

USAGE: git-patch-to-hg-export.py < git.patch > hg.patch
"""

from email.utils import parsedate_tz, mktime_tz
import re

def read_header_line(fin):
    header = None

    YIELD = 0                   # Yield the current line.
    APPEND = 1                  # Append to the current header.
    HEADER = 2                  # Start a new header.
    FINISH = 3                  # Yield the current header.

    # If Python had `goto', we wouldn't need to mess with all this.
    def action_for(header, line):
        if (line == '\n' or line == '\r\n') and header is None:
            return YIELD
        elif line.startswith(' '):
            return APPEND
        elif header is None:
            return HEADER
        else:
            return FINISH

    for line in fin:
        action = action_for(header, line)
        if action == YIELD:
            yield line
        elif action == APPEND:
            header = header[:-1] # Strip the newline.
            header += line
        elif action == HEADER:
            header = line
        else:
            yield header
            header = None
            action = action_for(header, line)
            if action == YIELD:
                yield line
            elif action == HEADER:
                header = line

def git_patch_to_hg(fin, fout):
    fout.write('# HG changeset patch\n')

    subject_re = re.compile(r'^(RE:)?\s*(\[[^]]*\])?\s*', re.I)

    # headers
    for line in read_header_line(fin):
        if line.startswith('From: '):
            fout.write('# User %s' % line[6:])
        elif line.startswith('Date: '):
            t = parsedate_tz(line[6:])
            timestamp = mktime_tz(t)
            timezone = -t[-1]
            fout.write('# Date %d %d\n' % (timestamp, timezone))
        elif line.startswith('Subject: '):
            subject = subject_re.sub('', line[9:])
            fout.write(subject + '\n')
        elif line == '\n' or line == '\r\n':
            break

    # commit message
    for line in fin:
        if line == '---\n':
            break
        fout.write(line)

    # skip over the diffstat
    for line in fin:
        if line.startswith('diff --git'):
            fout.write('\n' + line)
            break

    # diff
    # NOTE: there will still be an index line after each diff --git, but it
    # will be ignored
    for line in fin:
        fout.write(line)

    # NOTE: the --/version will still be at the end, but it will be ignored

if __name__ == "__main__":
    import sys
    git_patch_to_hg(sys.stdin, sys.stdout)


__author__ = "Mark Lodato <lodatom@gmail.com>"

__license__ = """
This is the MIT license: http://www.opensource.org/licenses/mit-license.php

Copyright (c) 2009 Mark Lodato

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
