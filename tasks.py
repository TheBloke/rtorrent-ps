# -*- coding: utf-8 -*-
#
# Project Tasks
#
from __future__ import print_function, unicode_literals

import os
import time
import glob
import shutil
import subprocess

from invoke import task

SPHINX_AUTOBUILD_PORT = 8340


def watchdog_pid(ctx):
    """Get watchdog PID via ``netstat``."""
    result = ctx.run('netstat -tulpn 2>/dev/null | grep 127.0.0.1:{:d}'
                     .format(SPHINX_AUTOBUILD_PORT), warn=True, pty=False)
    pid = result.stdout.strip()
    pid = pid.split()[-1] if pid else None
    pid = pid.split('/', 1)[0] if pid and pid != '-' else None

    return pid


@task
def docs(ctx):
    """Start watchdog to build the Sphinx docs."""
    build_dir = 'docs/_build'
    index_html = build_dir + '/html/index.html'

    stop(ctx)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    print("\n*** Generating HTML doc ***\n")
    ctx.run('builtin cd docs'
            ' && . {pwd}/.pyvenv/*/bin/activate'
            ' && nohup {pwd}/docs/Makefile SPHINXBUILD="sphinx-autobuild -p {port:d}'
            '          -i \'.*\' -i \'*.log\' -i \'*.png\' -i \'*.txt\'" html >autobuild.log 2>&1 &'
            .format(port=SPHINX_AUTOBUILD_PORT, pwd=os.getcwd()), pty=False)

    for i in range(25):
        time.sleep(2.5)
        pid = watchdog_pid(ctx)
        if pid:
            ctx.run("touch docs/index.rst")
            ctx.run('ps {}'.format(pid), pty=False)
            url = 'http://localhost:{port:d}/'.format(port=SPHINX_AUTOBUILD_PORT)
            print("\n*** Open '{}' in your browser...".format(url))
            break


@task
def stop(ctx):
    "Stop Sphinx watchdog"
    print("\n*** Stopping watchdog ***\n")
    for i in range(4):
        pid = watchdog_pid(ctx)
        if not pid:
            break
        else:
            if not i:
                ctx.run('ps {}'.format(pid), pty=False)
            ctx.run('kill {}'.format(pid), pty=False)
            time.sleep(.5)

@task
def test(ctx):
    """Run command integration tests."""
    test_dir = 'tests/commands'
    failures = 0

    for test_file in glob.glob(os.path.join(test_dir, "*.txt")):
        print("--- Running tests in '{}'...".format(test_file))

        with open(test_file, 'r') as handle:
            output = None
            for line in handle:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if line.startswith('$'):
                    output = subprocess.check_output(
                        line[1:].strip() + '; exit 0', shell=True, stderr=subprocess.STDOUT)
                    output = output.decode('utf-8')
                elif all(x in output for x in line.split('…')):
                    print('.', end='', flush=True)
                else:
                    failures += 1
                    print('\nFAIL: »{l}« not found in output\n{d}\n{o}\n{d}\n'
                          .format(l=line, o=output.rstrip(), d='~'*78))
        print('\n')

    print('\n☹ ☹ ☹  {} TEST(S) FAILED. ☹ ☹ ☹'.format(failures) if failures else '\n☺ ☺ ☺  ALL OK. ☺ ☺ ☺')
