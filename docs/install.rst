Installation Guide
==================

Note that this cannot be a Linux shell 101, so if the terminology and commands that follow
are new for you, refer to the usual sources like
`The Debian Administrator's Handbook`_, `The Linux Command Line`_, and
`The Art of Command Line`_ to get yourself acquainted.

.. _The Debian Administrator's Handbook: http://debian-handbook.info/browse/stable/
.. _The Linux Command Line: http://linuxcommand.org/tlcl.php
.. _The Art of Command Line: https://github.com/jlevy/the-art-of-command-line#the-art-of-command-line


General Installation Options
----------------------------

See :ref:`build-from-source` on using the provided ``build.sh`` script,
which will install `rTorrent-PS` into ``~/.local/rtorrent/‹version›``.

The stable rTorrent version **0.9.6** is built by default, but 0.9.4
is also supported (but not tested anymore). And not all patches are
applied equally, depending on whether they're needed, or applicable at all.

After installation, make sure to read through the :doc:`setup` chapter
in order to get the display-related changes set up correctly,
since on many machines this requires some special configuration of your terminal.

Also take note of the
`pimp-my-box <https://github.com/pyroscope/pimp-my-box>`_ project that
does it all (almost) automatically for Debian-type systems (and is the
preferred way to install on those systems). The automation is done using
`Ansible <http://docs.ansible.com/>`_, which implies you can easily
admin several systems with it, and also maintain them – so it's not a
one-shot installation bash script creating a setup that can never be
changed again.

.. note:: If you also install the `PyroScope command line
    utilities <https://github.com/pyroscope/pyrocore>`_, do not forget to
    activate the extended features available together with *rTorrent-PS*, as
    mentioned in the
    `Configuration Guide <https://pyrocore.readthedocs.org/en/latest/setup.html#extending-your-rtorrent-rc>`_.
    Starting with *version 1.1*, that activation is automatic.


OS-Specific Installation Options
--------------------------------

.. _install-deb:

Installation Using Debian Packages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For a limited set of Debian-derived platforms, there are packages
available that contain pre-compiled binaries (and only those, no
configuration or init scripts). You can download and install such a
package from `Bintray`_ —
assuming one is available for your platform. The packages install the
`rTorrent-PS` binary including some libraries into ``/opt/rtorrent``.

Example on `Debian Stretch`:

.. code-block:: bash

    version="0.9.6-PS-1.0-272-g388cfab~stretch_amd64"
    bintray="https://bintray.com/artifact/download/pyroscope"
    cd /tmp
    curl -Lko rt-ps.deb "$bintray/rtorrent-ps/rtorrent-ps_$version.deb"
    dpkg -i rt-ps.deb

After installation, you must provide a configuration file
(``~/.rtorrent.rc``), and either use the absolute path to the binary to
start it, or link it into ``/usr/local`` like this:

.. code-block:: bash

    ln -s /opt/rtorrent/bin/rtorrent /usr/local/bin

.. note:: You can safely install the package and test it
    out in parallel to an existing installation, just use the absolute path
    ``/opt/rtorrent/bin/rtorrent`` to start `rTorrent`.
    Your (session) data is in no way affected,
    as long as you normally run a *0.9.x* version.


Installation on Arch Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^

There are now two options contributed by `xsmile <https://github.com/xsmile>`_
for installing on `Arch` via ``pacman``.

#. The ``pkg2pacman`` command of ``build.sh`` creates a package similar to the
   `Debian` one, embedding a tested version combination of dependencies.
   See :ref:`build-pkg2deb` for general instructions on building that
   variant, and use ``pkg2pacman`` instead of ``pkg2deb``.
#. The *“Arch User Repository”* (AUR) PKGBUILDs maintained by @xsmile.
   These use a standard `Arch` build process, but include the usual `rTorrent-PS`
   patches.

   There is one package for ``libtorrent-ps``, and one for ``rtorrent-ps``,
   and both *take their dependencies from the normal OS packages*:

   - https://aur.archlinux.org/packages/libtorrent-ps/
   - https://aur.archlinux.org/packages/rtorrent-ps/

There is also the
`rtorrent-pyro-git <https://aur.archlinux.org/packages/rtorrent-pyro-git/>`_
AUR package.
It is *not* the same as you get from using ``build.sh``,
and not recommended anymore by *this* project, given the new options above.

If you have problems with building or installing any of these packages,
contact *their maintainer*.


Homebrew Tap for Mac OSX
^^^^^^^^^^^^^^^^^^^^^^^^

See the
`homebrew-rtorrent-ps <https://github.com/pyroscope/homebrew-rtorrent-ps>`_
repository for instructions to build *rTorrent-PS* and related
dependencies on Mac OSX.

**Right now, it is not maintained by anyone.**


.. _DebianInstallFromSource:

Manual Turn-Key System Setup
----------------------------

Introduction
^^^^^^^^^^^^

The following shows installation instructions for a working `rTorrent`
instance in combination with `PyroScope` **from scratch**, on `Debian` and
most Debian-derived distros. Note that the `pimp-my-box`_ project does
all this automatically for you, and is the tested and maintained way of
installation — this page is just a reference of the core installation steps
(if you run into problems, join the ``freenode`` IRC channel for help).

While the package names and the use of ``apt-get`` are somewhat
dependent on `Debian`, the `Preparatory Steps`_ commands which are executed
under ``root`` are similar for other distributions, and the compilation
instructions should work as-is on practically any Linux and (F)BSD.
These instructions are explicitly known to work on `Debian Jessie + Stretch`, and
`Ubuntu Xenial + Bionic`.

The whole procedure takes 15 – 20 minutes,
including full compilation from source.
Subtract about 5 minutes if you install `rTorrent` via a package.
This on a quad-core 3.3 GHz Xeon CPU with 32 GiB RAM,
and assuming you are familiar with the procedure,
or just blindly paste the command blocks that follow.
Add plenty of reading time when doing your first setup,
and it's still under an hour.

.. note::

    If you don't understand a word of what follows,
    hit |deb-adm|_ so then you do.

Non-packaged software is installed exclusively into your normal user
account (home directory), i.e. this description works OK for non-root users as long as
the required packages are installed before-hand. The default install
location is ``~/.local/rtorrent/«version»``, which means you can easily
delete any installed software, and also run several versions
concurrently.

For shared multi-user setups, this works fine also — compile and install
to ``/opt/rtorrent`` using ``./build.sh install``, then provide access
to all users by calling ``chmod -R go+rX /opt/rtorrent``. Perform the
steps from `PyroScope Installation`_ onwards for each user repeatedly, so
they get their own instance.

.. important::

    Most of the command blocks further below can be copied &
    pasted wholesale into a terminal. Note that ``bash`` *here documents*
    (``... <<'EOF'``) **MUST** be pasted at once, up to and including the
    line having a single ``EOF`` on it.

.. warning::

    If you have an existing ``/usr/local`` installation of
    `rTorrent` / `libtorrent`, it is *very* prudent to ``make uninstall`` that before
    compiling another version. Those *might* prevent successful compilation
    if your lookup paths somehow bring those versions to the front.

    In the same vein, remove any packages of
    ``libtorrent`` and ``rtorrent`` you have on your machine. The build
    instructions on this page then ensure that it is *no* problem to have
    several versions concurrently on your machine.
    If anything goes wrong, you can easily reinstall the packages provided by your OS.

.. _pimp-my-box: https://github.com/pyroscope/pimp-my-box
.. _deb-adm: http://static.debian-handbook.info/browse/stable/short-remedial-course.html
.. |deb-adm| replace:: The Debian Administrator's Handbook


Preparatory Steps
^^^^^^^^^^^^^^^^^

Installing Build Dependencies
"""""""""""""""""""""""""""""

First, you need to install a few **required** packages — **and no, this
is not optional in any way**. These are the only steps that must be
performed by the ``root`` user (i.e. in a root shell, or by writing
``sudo`` before the actual command):

.. code-block:: shell

    apt-get install sudo locales lsb-release build-essential pkg-config \
        subversion git time lsof binutils tmux curl wget \
        python-setuptools python-virtualenv python-dev \
        libssl-dev zlib1g-dev libncurses-dev libncursesw5-dev \
        libcppunit-dev autoconf automake libtool \
        libffi-dev libxml2-dev libxslt1-dev
    test "$LANG" = "en_US.UTF-8" \
        || echo "en_US.UTF-8 UTF-8" >>/etc/locale.gen \
        && locale-gen --lang en_US.UTF-8

Note that you can always show Debian's current build dependencies for
rTorrent using this command:

.. code-block:: shell

    echo $(apt-cache showsrc rtorrent libtorrent-dev | \
        grep Build-Depends: | cut -f2 -d: | tr ",)" " \\n" | cut -f1 -d"(")

On Fedora (26), use this (**list is user-provided, report any problems**):

.. code-block:: shell

    dnf install -y \
        redhat-lsb-core make autoconf automake libtool gcc gcc-c++ pkgconf-pkg-config \
        subversion git time lsof binutils tmux curl wget which \
        python-setuptools python-virtualenv python-devel python2-cffi \
        openssl-devel zlib-devel ncurses-devel cppunit-devel libxml2-devel libxslt-devel


Optional ``root`` Setup Steps
"""""""""""""""""""""""""""""

If you're security-conscious, you can create a ``rtorrent`` user and do
all the following setup steps under that new account. Doing that ensures
that there is *no way*, on a properly maintained ∗nix system, for the
build and setup scripts to break either your machine or your normal user
account.

.. code-block:: shell

    groupadd rtorrent
    useradd -g rtorrent -G rtorrent,users -c "rTorrent client" \
            -s /bin/bash --create-home rtorrent
    chmod 750 ~rtorrent
    su - rtorrent -c "mkdir -p ~/bin"



rTorrent Installation
^^^^^^^^^^^^^^^^^^^^^

Install via Debian Packages
"""""""""""""""""""""""""""

See :ref:`install-deb` above for details.
After adding the right package for your platform,
skip the next section and continue with `PyroScope Installation`_.

.. note::

    During `rTorrent` instance setup, do not forget to change the
    value of ``pyro.extended`` to 1 so the extended features are actually accessible!
    Starting with *version 1.1*, that activation is automatic.

.. _Bintray: https://bintray.com/pkg/show/general/pyroscope/rtorrent-ps/rtorrent-ps
.. _rTorrent-PS: https://github.com/pyroscope/rtorrent-ps


.. _build-from-source:

Build from Source
"""""""""""""""""

Get the `build script`_ and call it with the ``all`` parameter as shown
below; the script will then download, build, and install all necessary
components, storing temporary files in the current directory. You can
pass the ``clean_all`` parameter to remove those temporary files later
on, after everything works. Make sure you followed the
`Preparatory Steps`_ in the section further up on this page.

.. note::

    Be sure to select the version of rTorrent you want to
    compile, as determined by the settings at the start of the script. If
    you have no preference otherwise, stick to the default set in the
    script. Note that such a choice is sticky once you performed the
    ``download`` step, until you call ``clean_all`` again.

All installations go to ``~/.local/rtorrent/«version»/``, and disturb
neither any host setup nor another version of rTorrent you've installed
the same way.

.. code-block:: shell

    # Run this in your NORMAL user account!
    mkdir -p ~/src/; cd $_
    git clone https://github.com/pyroscope/rtorrent-ps.git
    cd rtorrent-ps

    # Use this if you have the resources, adapt for the number of cores
    # and the amount of free memory you have available.
    export MAKE_OPTS="-j4"

    # Check the VERSION SELECTION at the top of the script, and edit as needed
    nice time ./build.sh all  # build 'deps', 'vanilla', and then 'extended'

Note that the unpatched version is still available as
``rtorrent-vanilla``, and you can simply switch by changing the symlink
in ``~/bin``, or by calling either version with its full path.
See the :doc:`manual` for more details on the changes applied.

.. note::

    If you use the configuration as outlined below, do not forget
    to change the value of ``pyro.extended`` to 1 in case you want to unlock
    the additional features of the extended version!
    Starting with *version 1.1*, that activation is automatic.

.. _build script: https://raw.githubusercontent.com/pyroscope/rtorrent-ps/master/build.sh
.. _RtorrentExtended: https://github.com/pyroscope/rtorrent-ps/blob/master/docs/RtorrentExtended.md


PyroScope Installation
^^^^^^^^^^^^^^^^^^^^^^

The installation of ``pyrocore`` is done from source, see its `manual`_
for more details.

.. code-block:: shell

    # Run this in your NORMAL user account!
    mkdir -p ~/bin ~/.local
    git clone "https://github.com/pyroscope/pyrocore.git" ~/.local/pyroscope

    # Pass "/usr/bin/python2", or whatever else fits, to the script as its
    # 1st argument, if the default of "/usr/bin/python" is not a suitable
    # version.
    ~/.local/pyroscope/update-to-head.sh

    # Check success
    exec $SHELL -l
    pyroadmin --version

The last call's output should look similar to this:

.. code-block:: console

    $ pyroadmin --version
    pyroadmin 0.6.1.dev20180601 on Python 2.7.13


.. _manual: https://pyrocore.readthedocs.org/en/latest/installation.html


rTorrent Instance Setup
^^^^^^^^^^^^^^^^^^^^^^^

To be able to use several different instances of `rTorrent` (e.g. a second
one for experimental configuration changes), this setup doesn't use
``~/.rtorrent.rc`` at all, but keeps everything in one place under the
``~/rtorrent`` directory. If you change the assignment to ``RT_HOME``,
you can place it anywhere you like, or create alternate instances with
ease.


rTorrent Startup Script
"""""""""""""""""""""""

First, create the instance's directories and a `start script`_:

.. code-block:: shell

    # Run this in your NORMAL user account!
    export RT_HOME="${RT_HOME:-$HOME/rtorrent}"
    mkdir -p $RT_HOME; cd $_
    mkdir -p .session log work done watch/{start,load,hdtv,cleaned}
    cp ~/.local/pyroscope/docs/examples/start.sh ./start
    chmod a+x ./start

Note that this script is needed on modern systems, else the special
installation layout allowing concurrent use of several versions
will not work as expected.
So always call that script, and not ``rtorrent`` directly.

.. tip:: **Safely storing downloads on a mounted device**

    In case your data resides on a mounted device (e.g. an external USB disk),
    **add a check to the start script** that it is actually present.
    To do that, create a ``.mounted`` file in the root of your device,
    and ``exit`` the start script if not found.
    For your convenience, the code for that is already there
    at the top of ``start``, but commented out.

    If you don't check, that might lead to rehashing several terabytes of data,
    because `rTorrent` will mark the downloads stored on an absent device as broken
    (which they are without their data).

.. _start script: https://github.com/pyroscope/pyrocore/blob/master/docs/examples/start.sh


rTorrent Configuration
""""""""""""""""""""""

Next, a not-so-simple `rtorrent.rc`_ is created. It already provides
everything needed to use all features of the `PyroScope` tools.

Note that built-in ``pyrocore`` settings are read from a `provided include file`_,
that in turn loads snippets from the ``~/.pyroscope/rtorrent.d`` directory.
The same mechanism is used in the main ``rtorrent.rc`` file,
so you can easily add your own customizations in new ``rtorrent.d/*.rc`` files.

To get all this set up for you, call this provided script:

.. code-block:: shell

    # Run this in your NORMAL user account!
    ~/.local/pyroscope/src/scripts/make-rtorrent-config.sh

After this, you should check at
least the ``rtorrent.d/20-host-var-settings.rc`` file and adapt the
values to your environment and preferences.
The script can be called again to get updates from `GitHub`,
**but will overwrite all standard configuration files** with their new version.
To safely customize configuration, use the ``.rcignore`` file
and then provide your own version, or read on about ``_rtlocal.rc``.


The `_rtlocal.rc`_ file is the place for some simple custom settings,
like additional resource limits or changing default values.
The ``make-rtorrent-config.sh`` script does not copy that optional file,
so follow the link and pick what you like.

Example for a ``~/rtorrent/_rtlocal.rc`` file:

.. code-block:: ini

    # Reduce retention period of uncompressed logs
    pyro.log_archival.days.set = 1

    # Enable XMLRPC logging, and open log file *now*
    pyro.log.xmlrpc.enabled = 1
    log.xmlrpc = (pyro.logfile_path, xmlrpc)


.. note::

    In ``rtorrent.rc``, change the value of ``pyro.extended`` to 1
    so the extended `rTorrent-PS` features are actually accessible!
    Starting with *version 1.1*, that activation is automatic.

.. _rtorrent.rc: https://github.com/pyroscope/pyrocore/blob/master/docs/examples/rtorrent.rc#L1
.. _provided include file: https://github.com/pyroscope/pyrocore/blob/master/src/pyrocore/data/config/rtorrent-pyro.rc#L1-L2
.. _`_rtlocal.rc`: https://github.com/pyroscope/pimp-my-box/blob/master/roles/rtorrent-ps/templates/rtorrent/_rtlocal.rc#L1-L2


CLI Tools Configuration
^^^^^^^^^^^^^^^^^^^^^^^

This adds a minimal configuration, so that the defaults are taken from
the installed software, which makes later updates a lot easier.

.. code-block:: shell

    # Run this in your NORMAL user account!
    pyroadmin --create-config

    cat >~/.pyroscope/config.ini <<EOF
    # PyroScope configuration file
    #
    # For details, see https://pyrocore.readthedocs.org/en/latest/setup.html
    #

    [GLOBAL]
    # Location of your rtorrent configuration
    rtorrent_rc = ~/rtorrent/rtorrent.rc
    scgi_url = scgi://$HOME/rtorrent/.scgi_local

    [FORMATS]
    filelist = {{py:from pyrobase.osutil import shell_escape as quote}}{{#
        }}{{for i, x in looper(d.files)}}{{d.realpath}}/{{x.path}}{{#
            }}{{if i.next is not None}}{{chr(10)}}{{endif}}{{#
        }}{{endfor}}

    movehere = {{py:from pyrobase.osutil import shell_escape as quote}}{{#
        }}mv {{d.realpath | quote}} .

    # Formats for UI commands feedback
    tag_show = {{#}}Tags: {{ chr(32).join(d.tagged) }} [{{ d.name[:33] }}…]

    [SWEEP]
    # Settings for the "rtsweep" tool

    # Use the rules from the named [SWEEP_RULES_‹name›] sections
    default_rules = builtin, custom

    # Minimum amount of space that must be kept free (adds to the space request)
    space_min_free = 10g

    [SWEEP_RULES_CUSTOM]
    # Rules to manage disk space
    #
    # Rules are ordered by the given priority. You can disable built-in rules
    # found in the [SWEEP_RULES_BUILTIN] section by changing "default_rules"
    # in the [SWEEP] section. Use "rtsweep show" to list active rules.
    #
    # Default sort order for each rule is by "loaded" date (oldest first).
    # Note that active, prio 3, and ignored items are protected!
    #
    # If the active rules fail to provide enough space, as much of the oldest
    # items as needed are removed.

    # Seeded and bigger than 500M after 7 days, inactive and big items first
    seeded7d.prio   = 910
    seeded7d.sort   = active,-size
    seeded7d.filter = ratio=+1.2 size=+500m loaded=+5d

    [ANNOUNCE]
    # Add alias names for announce URLs to this section; those aliases are used
    # at many places, e.g. by the "mktor" tool and to shorten URLs to these aliases
    EOF

Read the `pyrocore Configuration Guide`_ for more information regarding this file.
You can come back to customizing it later, the system will work fine with the above default.

.. _`pyrocore Configuration Guide`: https://pyrocore.readthedocs.org/en/latest/setup.html


First Start and Testing
^^^^^^^^^^^^^^^^^^^^^^^

tmux Configuration
""""""""""""""""""

We spruce up ``tmux`` a bit using a `custom configuration`_, before we
start it the first time. This also makes it more homey for long-time
``screen`` users:

.. code-block:: shell

    # Run this in your NORMAL user account!
    cp --no-clobber ~/.local/pyroscope/docs/examples/tmux.conf ~/.tmux.conf


Starting a tmux Session
"""""""""""""""""""""""

You're now ready to start your shiny new `rTorrent-PS`, so just do it:

.. code-block:: shell

    # Run this in your NORMAL user account!
    tmux -2u new -n rT-PS -s rtorrent "~/rtorrent/start; exec bash"

The ``exec bash`` keeps your ``tmux`` window open if ``rtorrent`` exits,
which allows you to actually read any error messages in case it ends *unexpectedly*.
If such an error occurs (e.g. about your terminal not providing enough colors),
check out :doc:`setup` and the :doc:`troubleshooting` for a fix.

After that, test the XMLRPC connection by using this command in a new ``tmux`` window:

.. code-block:: shell

    # Open a new tmux terminal window by pressing "Ctrl-a" followed by "c", and then...
    rtxmlrpc system.time_usec

You can of course add more elaborate start scripts,
like a cron watchdog, init.d scripts, or a systemd unit.
Put the above ``tmux`` call into ``ExecStart``,
and use ``… new -d …`` to run a detached session
– see the `rTorrent wiki`_ for detailed examples.

Continue with reading the `'pyrocore' manual`_ to get acquainted with that,
and :doc:`setup` for providing the necessary configuration regarding your terminal.

.. _custom configuration: https://github.com/pyroscope/pimp-my-box/blob/master/roles/rtorrent-ps/files/dotfiles/tmux.conf
.. _'pyrocore' manual: https://pyrocore.readthedocs.org/en/latest/usage.html
.. _`rTorrent wiki`: https://github.com/rakshasa/rtorrent/wiki/Common-Tasks-in-rTorrent#starting-rtorrent-on-system-startup
