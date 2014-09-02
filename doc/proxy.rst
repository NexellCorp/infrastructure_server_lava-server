.. _proxy:

Cache Proxy Setting Up
======================

Before, it used to use an internal cache mechanism for downloaded images and
hwpacks to avoid downloading repeatly, which could save time and bandwidth.

lava-dispatcher switches to use cache proxy for managing cache files
automatically. The recommended proxy is Squid.

Install Squid 
^^^^^^^^^^^^^

Squid is easy to install via apt-get::

    sudo apt-get install squid

Or if you want a configurable squid, refer to the following link to compile
and install manually: http://wiki.squid-cache.org/SquidFaq/CompilingSquid

Configure Squid
^^^^^^^^^^^^^^^

You will need to customize accroding to your server, like disk layout, space.

Need to analyse and tune by collecting information when squid running with
real cases, like cache policy, file system.

Mandatory configuration options
-------------------------------

Based on original /etc/squid/squid.conf, see below tuning.

* cache_dir ufs /var/spool/squid 30720 16 256

  Mandatory option, please modify 30720(MB) to an available size.

  There can be several cache directories on different disk, but it's better not
  use RAID on the cache directories, it's recommended by Squid: The Definitive
  Guide that it will always degrades fs performance for squid. 30720 is the
  cache amount 30GB. 16 and 256 is Level 1 and 2 sub-directories, which is
  default.

* maximum_object_size 1024000 KB

  Mandatory option.

  Setting the value as 1024000KB makes the squid cache large files less than
  1GB, for our images are usually a large one but less than 1G.

Optional configuration options
------------------------------

Some others than mandatory options.

* acl over_conn_limit maxconn 10  # make max connection limit 10

* http_access allow localnet

  Enable localnet, also, we need to define more localnet in server environment
  to make sure all boards IP and other permitted clients are included.

  acl localnet src 10.122.0.0/16

* http_access deny over_conn_limit

  Make max connection of one client less than 10, it should be enough for
  a board, it can be increased.

* cache_mem 128 MB

  It can be increased if server MEM is enough, it's for squid mem amount for
  objects.

* cache_swap_low 90

  cache_swap_high 95

  Cache size will maintain between 90% to 95%. 

* client_lifetime 12 hours

  Make a client continuous accessing time 12hrs, default is 1 days, it can be
  increased.

* high_response_time_warning 2000

  2s in 1mins no response will log in cache.log.

* There is some email configurations to be set, like 'cache_mgr', it will send
  mail if cache proxy dies.

The configuration is only workable, there can be more improvement ways, some
still need to tune on server.

Other tuning
------------

Open files number can be increased for squid will need more than 1024
limitations sometimes::

    # ulimit -n
        1024

