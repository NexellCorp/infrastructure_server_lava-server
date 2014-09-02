.. _migrating_from_deployment_tool:

Migrating from lava-deployment-tool to packages
***********************************************

Please read the section on :ref:`packaging_components` for details of
how the LAVA packaging is organised. In particular, note the section
on :ref:`packaging_daemon_renaming`.

There are two main migration methods:

#. Upgrading Ubuntu from precise to trusty
#. Replacing precise with Debian testing

Either involves moving the (possibly large) amount of files in
the LAVA log directories, so a backup of those files would be
useful.

.. warning:: A backup of the entire server is also recommended as there is
             **no support for downgrading** from packaging back to
             lava-deployment-tool.

The best method for any one installation will depend on the local admins.
A fresh install is often faster than an upgrade from one LTS to another,
as long as the database export process is reliable. If there is a lot of
data on the machine besides LAVA content, there will need to be some
consideration of how a kernel and OS upgrade will affect those other
services.

Due to limitations within ``lava-deployment-tool`` and ``lava-manifest``,
there is no way to migrate to the packaging based on django1.6 using
the tools already installed within the existing LAVA instance.

.. note:: A default LAVA install from packages supports ``http://``, not
          ``https://`` in the Apache configuration. If your existing
          instance uses ``https://``, ensure you have a copy of the
          apache configuration and remember to port those changes to
          apache2.4 in ``/etc/apache2/sites-available/lava-server.conf``.

.. _postgres_export:

Exporting the postgres database
###############################

Most admins will have custom ways to get a dump of the postgres
database and any script which can dump the data and import it
successfully into a fresh, upgraded, install will be suitable.

``lava-deployment-tool`` would have read variables from the
``instance.conf`` and used a call based on::

   $ pg_dump \
        --no-owner \
        --format=custom \
        --host=$dbserver \
        --port=$dbport \
        --username=$dbuser \
        --no-password $dbname \
        --schema=public \
        > "$destdir/database.dump"

A new install will need the database user created::

    sudo -u postgres createuser \
        --no-createdb --encrypted \
        --login --no-superuser \
        --no-createrole --no-password \
        --port $dbport $dbuser
    sudo -u postgres psql --port 5432 \
        --command="ALTER USER \"lavaserver\" WITH PASSWORD '$dbpass';"


``lava-deployment-tool`` would attempt a restore from this dump by
using the variables from ``instance.conf`` and calls based on::

    sudo -u postgres dropdb \
        --port $dbport \
        $dbname || true
    sudo -u postgres createdb \
        --encoding=UTF-8 \
        --locale=en_US.UTF-8 \
        --template=template0 \
        --owner=$dbuser \
        --port $dbport \
        --no-password \
        $dbname
    sudo -u postgres createlang \
        --port $dbport \
        plpgsql \
        $dbname || true
    sudo -u postgres pg_restore \
        --exit-on-error --no-owner \
        --port $dbport \
        --role $dbuser \
        --dbname $dbname \
        "${1}" > /dev/null

.. tip:: If your database is very large, consider adding the ``--jobs``
         option to ``pg_restore`` to parallelise the postgresql workload.
         See the postgresql documentation (``man 1 pg_restore``) for the
         best value to pass as the number of concurrent jobs to use.

Whatever method is chosen, verify that the dump from ``postgresql-9.1``
can be successfully imported into ``postgresql-9.3`` then check the
migration by connecting to the new database using the username, database
name and password specified in ``instance.conf`` and check for the
relevant tables. e.g.::

 sudo su postgres lavaserver
 psql
  psql (9.3.4)
  ...
 postgres=# \l
  lava-production | lava-production | UTF8     | en_US.UTF-8 | en_US.UTF-8 |
  ...
 postgres=# \dt
   ...
    public | dashboard_app_attachment                   | table | lavaserver
   ...
 postgres=# \q

.. _assumptions:

Assumptions
###########

#. LAVA is already installed using ``lava-deployment-tool`` on
   Ubuntu Precise Pangolin 12.04LTS in ``/srv/lava/instances/``
#. postgresql9.1 is installed and running on port 5432::

    ls -a /var/run/postgresql/

#. there are idle devices or possibly running test jobs

#. any local buildouts are either removed or merged back to
   master and updated. (This is a precaution to ensure that
   there are no development changes like database migrations which
   exist only in the buildout and not in master.)

.. _requirements:

Requirements
############

To copy the test job log files to the new location, it can be useful
to have ``rsync`` installed on each machine, it is not always part
of a LAVA install.

The only parts of the existing LAVA instance which will be retained are:

* The test job log output, bundles and attachments::

   /srv/lava/instances/<INSTANCE>/var/lib/lava-server/media/

* The database (master instance only) See :ref:`postgres_export`.

* The device configuration files::

   /srv/lava/instances/<INSTANCE>/etc/lava-dispatcher/devices/
   /srv/lava/instances/<INSTANCE>/etc/lava-dispatcher/device-types/

* The lava-server instance.conf file::

   /srv/lava/instances/<INSTANCE>/etc/lava-server/instance.conf

Other configuration files are ported or generated by the packaging.

Preparing for the upgrade
#########################

#. Declare a maintenance window for scheduled downtime.
#. Take all devices offline using the Django admin interface. Wait for
   any devices in status ``GoingOffline`` to complete the test job or
   cancel the test job if necessary.
#. Ensure suitable backups exist for the database, device configuration,
   test job output files and the ``instance.conf``.
#. Ensure the machine has enough free space for a large set of package
   downloads. Ensure that the master instance also has enough free space
   for a copy of the test job output directories.
#. Incorporate into the plan for the upgrade that the master will need
   to be upgraded but then work will need to concentrate on all the
   :ref:`remote_worker_upgrade` tasks before restarting the ``lava-server``
   service on the master instance or putting any devices back online.
#. Exit out of all shells currently using the ``/srv/lava/instances/<INSTANCE>/bin/activate``
   virtual environment settings.
#. Ensure that any local buildouts are either removed or merged back to
   master and updated. (This is a precaution to ensure that
   there are no development changes like database migrations which
   exist only in the buildout and not in master.)

Select the upgrade path:
========================

Now select how you want to upgrade:

* :ref:`ubuntu_trusty_upgrade`
* :ref:`debian_jessie`

.. _ubuntu_trusty_upgrade:

Upgrading Ubuntu to Trusty Tahr 14.04LTS
########################################

.. warning:: It is worth investigating any issues with the upgrade from
             precise to trusty, in advance, using virtual machines or
             test deployments. These tests do not need LAVA installed,
             just a basic server, as there are issues with the precise
             to trusty upgrade. Fresh installs of Trusty do not seem to
             be affected or consider :ref:`debian_jessie`.

Once migrated to Trusty and using packages, the OS can be further
upgraded to Utopic Unicorn and subsequent releases in much the same way
(currently, there is no postgresql change between Trusty and Utopic).
Utopic will synchronise the LAVA packages directly with Debian, so there
will be no need to use a separate repository.

.. _master_instance_upgrade:

Master instance upgrade
=======================

#. Stop lava::

    sudo service lava stop

#. Stop apache::

    sudo service apache2 stop

   .. tip:: Alternatively, re-enable the default apache configuration
            to continue serving pages and put up a "maintenance page".
            Apache will restart during the upgrade but this will be
            only for a brief period.

#. Stop postgresql-9.1 without dropping the cluster::

    sudo service postgresql stop

   This allows the upgrade to install postgresql-9.3, use port 5432
   for 9.3 and automatically migrate the 9.1 cluster to 9.3.

#. Change apt sources. Other references to precise and precise-updates
   may also need to change - the principle change is to trusty or
   utopic. Ensure that the universe component is selected::

    deb http://archive.ubuntu.com/ubuntu trusty main universe

   Alternatively, change all the references in the current file
   from ``precise`` to ``utopic``. Remember to check for any other
   apt sources in ``/etc/apt/sources.list.d/``, e.g.::

    /etc/apt/sources.list.d/linaro-maintainers-tools-precise.list

#. update, upgrade and then dist-upgrade::

    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get dist-upgrade
    sudo apt-get autoclean

   Avoid making manual changes between the ``upgrade`` and
   ``dist-upgrade`` steps - glibc will be upgraded and some daemons will
   need to be restared, this is best done automatically when prompted
   by debconf.

   The upgrade will bring in a new kernel, so a reboot is required
   at this point to allow fuse to use the upgraded kernel module.

   .. tip:: ``apt`` has migrated to version 1.0 in Trusty, which means
            that some commands can now be run as just ``apt`` as well as
            the previous ``apt-get``. See man 1 apt after the upgrade.

   .. note:: If the machine is virtualised, ensure that the kernel upgrade
             is handled and that the machine reboots into the new image
             cleanly.

#. Remove ``lava-deployment-tool`` - this may seem premature but
   deployment-tool is unusable on Trusty or later and would undo some
   of the changes implemented via the packaging if it was run by mistake.

#. Migrate to Postgresql9.3

   Do not remove postgresql-9.1 until the cluster has been migrated.
   To migrate the cluster, both versions need to be installed - 9.1
   can be removed after the migration (9.1 will not be able to use the
   9.3 cluster). With 9.1 installed, apt will automatically install 9.3::

    sudo service postgresql stop
    sudo pg_dropcluster --stop 9.3 main
    sudo pg_upgradecluster 9.1 main

   You can check the new cluster using ``psql``. e.g.::

    sudo su postgres lavaserver
    psql
     psql (9.3.4)
     ...
    postgres=# \l
     lava-production | lava-production | UTF8     | en_US.UTF-8 | en_US.UTF-8 |
     ...
    postgres=# \q
    exit

   Now drop the 9.1 cluster and remove 9.1::

    sudo pg_dropcluster 9.1 main
    sudo apt-get remove postgresql-9.1 postgresql-client-9.1

   Ubuntu Precise has a buggy postgresql-client-9.1 package which does
   not remove cleanly::

    sudo dpkg -P postgresql-contrib-9.1

   Check that the default postgresql port is 5432::

    grep port /etc/postgresql/9.3/main/postgresql.conf

   You can check the migration using ``psql``::

    sudo su postgres
    psql
     psql (9.3.4)
     ...
    postgres=# \l
     lava-production | lava-production | UTF8     | en_US.UTF-8 | en_US.UTF-8 |
     ...
    postgres=# \q
    exit

#. Clean-up after the upgrade.

   Apache has been upgraded to 2.4, so apache2.2 can be safely removed::

    sudo apt-get --purge autoremove

#. Add the LAVA packaging repository.

   This will remain necessary on Trusty (although the path and keyring
   may change to an official repository) but on Ubuntu Utopic Unicorn
   and later releases, the necessary packages will migrate automatically
   from Debian::

    sudo apt install emdebian-archive-keyring
    sudo vim /etc/apt/sources.list.d/lava.list

   The repository is at::

    deb http://people.linaro.org/~neil.williams/ubuntu trusty main

#. Migrate the instance configuration to the packaging location.

   The packages will respect an existing LAVA configuration, if the relevant
   files are in the correct location ``/etc/lava-server/instance.conf``::

    sudo mkdir -p /etc/lava-server/
    sudo cp /srv/lava/instances/<INSTANCE>/etc/lava-server/instance.conf /etc/lava-server/instance.conf

   Convert the LAVA_PREFIX in `/etc/lava-server/instance.conf` to the
   `FHS`_ (Filesystem Hierarchy Standard) compliant path::

    LAVA_PREFIX="/var/lib/lava-server/"

   Some settings are no longer used by the packaging but these will simply
   be ignored by the packaging.

.. _`FHS`: http://www.pathname.com/fhs/

#. Migrate the device configurations to the packaging locations::

    sudo cp /srv/lava/instances/<INSTANCE>/etc/lava-dispatcher/devices/* /etc/lava-dispatcher/devices/

#. Migrate the instance logfiles to the packaging location.

   The permissions on these files will be fixed once ``lava-server`` is
   installed. Depending on the amount of files, the simplest way to
   migrate the files may be to use rsync::

    sudo mkdir -p /var/lib/lava-server/default/media/
    sudo rsync -vaz /srv/lava/instances/<INSTANCE>/var/lib/lava-server/media/* /var/lib/lava-server/default/media/

   .. note:: The wildcard at the end of the source directory and the
             forward slash at the end of the destination directory are
             very important.

#. Install LAVA from packages::

    sudo apt update
    sudo apt install lava-server

   The install will prompt for the instance name, you can specify the
   same instance name as the original lava-deployment-tool instance but
   this no longer affects where files are actually installed, nor does
   it affect the database name or database user. The instance name
   becomes a simple label with the packaging upgrade.

#. Restart daemons affected by the installation::

    sudo service tftpd-hpa restart

#. Pause while completing the :ref:`remote_worker_upgrade`, if relevant.

#. Run forced healthchecks on devices.

#. Return devices to ``Online`` status.

#. Complete scheduled maintenance.

.. _remote_worker_upgrade:

Remote worker upgrade
=====================

This is essentially the same as a :ref:`master_instance_upgrade`
without any database work and without copying the log files which
are all on the master.

#. Stop lava::

    sudo service lava stop

#. umount the sshfs.

   Check the output of ``mount`` and umount the relevant sshfs location.
   e.g.::

    lava-staging@staging.validation.linaro.org:/srv/lava/instances/staging/var/lib/lava-server/media
     on /srv/lava/instances/staging/var/lib/lava-server/media type
     fuse.sshfs (rw,nosuid,nodev,max_read=65536,allow_other,user=lava-staging)

    $ sudo umount /srv/lava/instances/<INSTANCE>/var/lib/lava-server/media

#. Stop apache::

    sudo service apache2 stop

#. Change apt sources. Other references to precise and precise-updates
   may also need to change - the principle change is to trusty or
   utopic. Ensure that the universe component is selected::

    deb http://archive.ubuntu.com/ubuntu trusty main universe

   Alternatively, change all the references in the current file
   from ``precise`` to ``utopic``. Remember to check for any other
   apt sources in ``/etc/apt/sources.list.d/``, e.g.::

    /etc/apt/sources.list.d/linaro-maintainers-tools-precise.list

#. update, upgrade and then dist-upgrade::

    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get dist-upgrade
    sudo apt-get autoclean

   Avoid making manual changes between the ``upgrade`` and
   ``dist-upgrade`` steps - glibc will be upgraded and some daemons will
   need to be restared, this is best done automatically when prompted
   by debconf.

   The upgrade will bring in a new kernel, so a reboot is required
   at this point to use the matching fuse support for the master.

   .. tip:: ``apt`` has migrated to version 1.0 in Trusty, which means
            that some commands can now be run as just ``apt`` as well as
            the previous ``apt-get``. See man 1 apt after the upgrade.

   .. note:: If the machine is virtualised, ensure that the kernel upgrade
             is handled and that the machine reboots into the new image
             cleanly.

#. Remove ``lava-deployment-tool`` - this may seem premature but
   deployment-tool is unusable on Trusty or later and would undo some
   of the changes implemented via the packaging if it was run by mistake.

#. Clean-up after the upgrade.

   Apache has been upgraded to 2.4, so apache2.2 can be safely removed::

    sudo apt-get --purge autoremove

#. Add the LAVA packaging repository.

   This will remain necessary on Trusty (although the path and keyring
   may change to an official repository) but on Ubuntu Utopic Unicorn
   and later releases, the necessary packages will migrate automatically
   from Debian::

    sudo apt install emdebian-archive-keyring
    sudo vim /etc/apt/sources.list.d/lava.list

   The repository is at::

    deb http://people.linaro.org/~neil.williams/ubuntu trusty main

#. Migrate the instance configuration to the packaging location.

   The packages will respect an existing LAVA configuration, if the relevant
   files are in the correct location ``/etc/lava-server/instance.conf``::

    sudo mkdir -p /etc/lava-server/
    sudo cp /srv/lava/instances/<INSTANCE>/etc/lava-server/instance.conf /etc/lava-server/instance.conf

   Convert the LAVA_PREFIX in `/etc/lava-server/instance.conf`
   to the `FHS`_ (Filesystem Hierarchy Standard) compliant path::

    LAVA_PREFIX="/var/lib/lava-server/"

   Some settings are no longer used by the packaging but these will simply
   be ignored by the packaging.

#. **Do not migrate the instance logfiles** to the packaging location.

   There is no ``rsync`` operation on a remote worker - the files are
   on an sshfs from the master. Ensure that
   ``/srv/lava/instances/<INSTANCE>/var/lib/lava-server/media``
   is empty and that there is no current sshfs mount.

#. Install LAVA from packages::

    sudo apt update
    sudo apt install lava-server

   Ensure you specify that this is not a single master instance when
   prompted by debconf.

   The install will prompt for the instance name, you can specify the
   same instance name as the original lava-deployment-tool instance but
   this no longer affects where files are actually installed, nor does
   it affect the database name or database user. The instance name
   becomes a simple label with the packaging upgrade.

   The other details which will be needed during installation are available
   in the ``instance.conf`` of the original worker. Enter the details
   when prompted. See :ref:`distributed_deployment`.

#. Enable apache on the remote worker.

   This is used to serve modified files to the devices::

    sudo a2dissite 000-default
    sudo a2ensite lava-server
    sudo service apache2 restart

#. Restart daemons affected by the installation::

    sudo service tftpd-hpa restart

#. Return to :ref:`master_instance_upgrade`.

.. _debian_jessie:

Upgrading LAVA to Debian Jessie (testing)
###########################################

See :ref:`install_debian_jessie`.

The recommended method to upgrade LAVA to Debian is to backup critical
data on the Ubuntu Precise machine and then install a fresh Debian
install. See :ref:`requirements`.

It is possible to upgrade from Ubuntu to Debian but it is not recommended
as it may end up with a mix of package setups and an unexpected final
configuration.

Most of the steps are similar to the Ubuntu upgrade steps and these
instructions also cover if you choose to make a fresh install of
Ubuntu Trusty Tahr 14.04LTS.

The data needed off the old Precise instance will be:

#. The test job data::

    /srv/lava/instances/<INSTANCE>/var/lib/lava-server/media/*

#. The database (except for remote workers) See :ref:`postgres_export`.

   * The device configuration files::

     /srv/lava/instances/<INSTANCE>/etc/lava-dispatcher/devices/
     /srv/lava/instances/<INSTANCE>/etc/lava-dispatcher/device-types/

#. The instance configuration::

    /srv/lava/instances/<INSTANCE>/etc/lava-server/instance.conf

To switch the OS, it may be best to retire the old machine / VM and
put it onto a different network address and hostname. Then dump the
postgres database and create a backup of the test job data.

The choice between using Jessie and Sid is entirely down to you.
There is no particular reason to upgrade to jessie as a route to
unstable, you can just go from wheezy to unstable, especially with
a server-based install without a graphical user interface.

.. _install_lava_master_debian:

Installing a LAVA master instance on Debian
===========================================

The process does not differ greatly from the standard installation
instructions for :ref:`debian_installation`. The extra stages occur
between installation of the base system and installation of the LAVA
packages.

#. Download an ISO for Debian 7.5 Wheezy from http://www.debian.org/

#. Install on required machine - no need for a desktop environment and
   the database installation is best left until after the upgrade to
   Jessie. ``openssh-server`` would be useful.

#. Edit the apt sources list to point at jessie instead of wheezy::

   $ sudo vim /etc/apt/sources.list

#. update, upgrade and then dist-upgrade::

    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get dist-upgrade
    sudo apt-get autoclean

   Avoid making manual changes between the ``upgrade`` and
   ``dist-upgrade`` steps - glibc will be upgraded and some daemons will
   need to be restared, this is best done automatically when prompted
   by debconf.

   The upgrade will bring in a new kernel, so a reboot is recommended
   at this point.

   .. tip:: ``apt`` has migrated to version 1.0 in Jessie, which means
            that some commands can now be run as just ``apt`` as well as
            the previous ``apt-get``. See man 1 apt after the upgrade.

#. Clean-up after the upgrade.

   Apache has been upgraded to 2.4, so apache2.2 is one of many
   packages which can be safely removed::

    sudo apt-get --purge autoremove

#. Add the LAVA packaging repository.

   .. tip:: See :ref:`install_debian_jessie` - the packaging repository is
            only necessary to ensure that all dependencies exist in Jessie.

   ::

    sudo apt install emdebian-archive-keyring
    sudo vim /etc/apt/sources.list.d/lava.list

   The repository is at::

    deb http://people.linaro.org/~neil.williams/lava jessie main

#. Migrate the instance configuration to the packaging location.

   The packages will respect an existing LAVA configuration, if the relevant
   files are in the correct location ``/etc/lava-server/instance.conf``.
   Copy the ``instance.conf`` from the precise box to the new Debian
   machine and put into place. e.g.::

    sudo mkdir -p /etc/lava-server/
    sudo cp /tmp/instance.conf /etc/lava-server/instance.conf

   Convert the LAVA_PREFIX in `/etc/lava-server/instance.conf`
   to the `FHS`_ (Filesystem Hierarchy Standard) compliant path::

    LAVA_PREFIX="/var/lib/lava-server/"

   Some settings are no longer used by the packaging but these will simply
   be ignored by the packaging.

#. Migrate the instance logfiles to the packaging location.

   The permissions on these files will be fixed once ``lava-server`` is
   installed. Depending on how the files were copied from the Ubuntu
   machine, the files can be decompressed directly into the new
   location.

#. Import the postgres database dump.

   Use the values in the ``/etc/lava-server/instance.conf`` to import
   the postgres data with the correct username, password and database
   access.

#. Install LAVA from packages::

    sudo apt update
    sudo apt install lava-server

   The install will prompt for the instance name, you can specify the
   same instance name as the original lava-deployment-tool instance but
   this no longer affects where files are actually installed, nor does
   it affect the database name or database user. The instance name
   becomes a simple label with the packaging upgrade.

#. Enable the lava-server apache configuration::

    sudo a2dissite 000-default
    sudo a2ensite lava-server
    sudo service apache2 restart

#. Restart daemons affected by the installation::

    sudo service tftpd-hpa restart

#. Ensure all devices remain offline.

#. Configure the master to work with a remote worker.

See :ref:`remote_database` and :ref:`example_postgres`. Remember to
use the ``LAVA_DB_USER`` and ``LAVA_DB_NAME`` from the ``instance.conf``
on the master. e.g.::

 host    lava-playground    lava-playground    0.0.0.0/0    md5

#. Pause to :ref:`remote_worker_debian`.

#. Run forced healthchecks on devices.

#. Return devices to ``Online`` status.

#. Complete scheduler maintenance.

.. _remote_worker_debian:

Install a LAVA remote worker using Debian
==========================================

The process does not differ greatly from the standard installation
instructions for :ref:`debian_installation`. The extra stages occur
between installation of the base system and installation of the LAVA
packages.

#. Download an ISO for Debian 7.5 Wheezy from http://www.debian.org/

#. Install on required machine - no need for a desktop environment,
   ``openssh-server`` would be useful.

#. Change apt sources to point at jessie instead of wheezy::

    /etc/apt/sources.list

#. update, upgrade and then dist-upgrade::

    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get dist-upgrade
    sudo apt-get autoclean

   Avoid making manual changes between the ``upgrade`` and
   ``dist-upgrade`` steps - glibc will be upgraded and some daemons will
   need to be restared, this is best done automatically when prompted
   by debconf.

   The upgrade will bring in a new kernel, so a reboot is recommended
   at this point.

   .. tip:: ``apt`` has migrated to version 1.0 in Jessie, which means
            that some commands can now be run as just ``apt`` as well as
            the previous ``apt-get``. See man 1 apt after the upgrade.

#. Clean-up after the upgrade.

   Apache has been upgraded to 2.4, so apache2.2 is one of many
   packages which can be safely removed::

    sudo apt-get --purge autoremove

#. Add the LAVA packaging repository.

   .. tip:: See :ref:`install_debian_jessie` - the packaging repository is
            only necessary to ensure that all dependencies exist in Jessie.

   ::

    sudo apt install emdebian-archive-keyring
    sudo vim /etc/apt/sources.list.d/lava.list

   The repository is at::

    deb http://people.linaro.org/~neil.williams/lava jessie main

#. Migrate the instance configuration to the packaging location.

   The packages will respect an existing LAVA configuration but still ask
   the questions, so keep a terminal window open with the values.
   Copy the ``instance.conf`` from the precise box to the new Debian
   machine and put into place. e.g.::

    sudo mkdir -p /etc/lava-server/
    sudo cp /tmp/instance.conf /etc/lava-server/instance.conf

   Convert the LAVA_PREFIX in `/etc/lava-server/instance.conf`
   to the `FHS`_ (Filesystem Hierarchy Standard) compliant path::

    LAVA_PREFIX="/var/lib/lava-server/"

   Some settings are no longer used by the packaging but these will simply
   be ignored by the packaging.

#. **Do not migrate the instance logfiles** to the packaging location.

   There is no ``rsync`` operation on a remote worker - the files are
   on an sshfs from the master. Ensure that ``/var/lib/lava-server/default/media``
   is empty and that there is no current sshfs mount.

#. Install LAVA from packages::

    sudo apt update
    sudo apt install lava-server

   The install will prompt for the instance name, you can specify the
   same instance name as the original lava-deployment-tool instance but
   this no longer affects where files are actually installed, nor does
   it affect the database name or database user. The instance name
   becomes a simple label with the packaging upgrade.

#. Configure the remote worker

   See :ref:`configuring_remote_worker` to setup the SSH key, the ``fuse``
   configuration and ``lava-coordinator``.

   Restart the ``lava-server`` daemon once done and check that the SSHFS
   mount operations has worked. See :ref:`check_sshfs_mount`.

#. Enable apache on the remote worker.

   This is used to serve modified files to the devices::

    sudo a2dissite 000-default
    sudo a2ensite lava-server
    sudo service apache2 restart

#. Restart daemons affected by the installation::

    sudo service tftpd-hpa restart

#. Return to :ref:`install_lava_master_debian`.
