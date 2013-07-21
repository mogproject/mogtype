#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Yosuke Mizutani
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
mogtype - The Simplest Typing Training Tool

CLI-based typing training tool for Japanese Kana typing.
"""

from optparse import OptionParser
import sys
import os
import locale
import time
import random
import curses
from keymap import normalize, ords, get_kana, is_valid

# Version settings.
PROGRAM_NAME = 'mogtype'
PROGRAM_VERSION = '0.0.1'

# Default settings.
SCRIPT_DIR = os.path.dirname(__file__)
SCRIPT_BASE_NAME = os.path.basename(__file__)
DEFAULT_DB_FILE = SCRIPT_DIR + '/mogtype.txt'
DEFAULT_MAX_COUNT = 8


class Sentence(object):
    def __init__(self, text):
        unicode_text = unicode(text, 'utf-8')
        self.orig = unicode_text.encode('utf-8')
        self.norm = normalize(unicode_text).encode('utf-8')
        self.ords = ords(unicode_text)

    def __str__(self):
        return 'Sentence(%s, %s, %s)' % (self.orig, self.norm, self.ords)


class MogType(object):
    def __init__(self, stdscr, path=None, count=None):
        # Load sentence database.
        self.sentences = self._load(path or DEFAULT_DB_FILE)
        self.max_count = count or DEFAULT_MAX_COUNT
        self.max_count = int(self.max_count)

        # Initialize status.
        self.status = MogTypeStatus()

        # Initialize window.
        self.view = MogTypeView(stdscr)

        # Main loop.
        self._main_loop()

    def _load(self, path):
        self.sentences = []
        with open(path) as f:
            for line in f:
                self.sentences.append(Sentence(line.rstrip()))
        return self.sentences

    def _main_loop(self):
        for count in range(1, self.max_count + 1):
            # Select random sentence.
            st = self.sentences[random.randint(0, len(self.sentences) - 1)]
            self.view.print_sentence(st, count, self.max_count)

            # Main loop.
            pos = 0
            while pos < len(st.ords):
                self.view.print_progress(st, pos, self.status)
                c = self.view.get_ch()

                if c == st.ords[pos]:  # correct character
                    pos += 1
                    self.status.success()
                    self.view.clear_mistake()
                elif is_valid(c):  # mistake
                    self.status.fail()
                    self.view.print_mistake(get_kana(c).encode('utf-8'))
                elif c == 0x1b:  # ESCAPE
                    return
                else:
                    pass

        # Show result.
        self.view.print_result()
        self.view.get_ch()


class MogTypeStatus(object):
    def __init__(self):
        self.num_success = 0  # Number of characters that were correctly typed.
        self.num_failed = 0  # Number of mistakes.

    def success(self):
        self.num_success += 1

    def fail(self):
        self.num_failed += 1

    def start_timer(self):
        pass  # TBI

    def stop_timer(self):
        pass  # TBI

    def miss(self):
        return min(999, self.num_failed)

    def accurancy(self):
        total = self.num_success + self.num_failed
        return 100.0 * self.num_success / total if total else 0.0


class MogTypeView(object):
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.print_constant()

    def print_constant(self):
        self.stdscr.addstr(0, 0, 'No:')
        self.stdscr.hline(1, 0, '=', 80)
        self.stdscr.addstr(0, 54, 'Miss: ')
        self.stdscr.addstr(0, 64, 'Accurancy:---.-%')
        self.stdscr.addstr(4, 0, '+' + '-' * 78 + '+')
        self.stdscr.addstr(5, 0, '|')
        self.stdscr.addstr(6, 0, '+' + '-' * 78 + '+')
        self.stdscr.hline(9, 0, '=', 80)
        self.stdscr.addstr(10, 0, 'Press ESC to exit')

    def print_sentence(self, sentence, count, max_count):
        self.stdscr.addstr(0, 4, '%3d/%3d' % (count, max_count))
        self.stdscr.addstr(2, 0, sentence.orig)
        self.stdscr.clrtoeol()

    def print_progress(self, sentence, pos, status):
        self.stdscr.addstr(5, 2, sentence.norm)
        self.stdscr.clrtoeol()
        self.stdscr.addstr(5, 79, '|')
        self.print_status(status)
        self.stdscr.move(5, pos * 2 + 2)

    def print_mistake(self, ch):
        self.stdscr.addstr(8, 0, 'Oops! You typed: %s' % ch)

    def print_status(self, status):
        self.stdscr.addstr(0, 59, '%3d' % status.miss())
        self.stdscr.addstr(0, 74, ('%.1f' % status.accurancy()).rjust(5))

    def clear_mistake(self):
        self.stdscr.move(8, 0)
        self.stdscr.clrtoeol()

    def print_result(self):
        self.stdscr.addstr(10, 0, 'Press any key to exit')

    def get_ch(self):
        return self.stdscr.getch()


def main():
    # Get command line argument.
    parser = OptionParser(version='%s %s' % (PROGRAM_NAME, PROGRAM_VERSION))
    parser.add_option(
        '-f', '--file', dest='path',
        help='path to the sentence database (default: mogtype.txt)',
        metavar='PATH'
    )
    parser.add_option(
        '-c', '--count', dest='count',
        help='number of exercises (default: 8)', metavar='COUNT'
    )

    options = parser.parse_args()[0]

    # Set locale
    locale.setlocale(locale.LC_ALL, (''))

    # Launch mogtype
    try:
        curses.wrapper(lambda scr: MogType(stdscr=scr, **options.__dict__))
    except Exception, e:
        print(e)
        return 3
    return 0

if __name__ == '__main__':
    sys.exit(main())
