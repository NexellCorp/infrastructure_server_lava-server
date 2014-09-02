# Django settings for django_hello project used on Debian systems.

import os
from lava_server.settings.getsettings import Settings
from lava_server.extension import loader
from lava_server.settings.production import *

# Load application settings from lava_server.settings integration package
distro_settings = Settings("lava-server")

# Load the mount point from settings file
MOUNT_POINT = distro_settings.mount_point

# Load default database from distro integration
DATABASES = {'default': distro_settings.default_database}

# Load debug settings from the configuration file
DEBUG = distro_settings.DEBUG

# Load secret key from distro integration
SECRET_KEY = distro_settings.SECRET_KEY

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = distro_settings.MEDIA_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = distro_settings.MEDIA_URL

# Absolute filesystem path to the directory that will hold archived files.
ARCHIVE_ROOT = distro_settings.ARCHIVE_ROOT

# Absolute filesystem path to the directory that will hold static, read only
# files collected from all applications.
STATIC_ROOT = distro_settings.STATIC_ROOT

# URL that handles the media served from STATIC_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://static.lawrence.com", "http://example.com/static/"
STATIC_URL = distro_settings.STATIC_URL

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = distro_settings.ADMIN_MEDIA_PREFIX

# List of absolute pathnames used to resolve templates.
TEMPLATE_DIRS = [os.path.join(os.path.dirname(__file__), '..', 'templates')]
TEMPLATE_DIRS.extend(distro_settings.TEMPLATE_DIRS)

# Like TEMPLATE_DIRS but for static files
STATICFILES_DIRS = distro_settings.STATICFILES_DIRS

# A tuple that lists people who get code error notifications. When DEBUG=False
# and a view raises an exception, Django will e-mail these people with the
# full exception information. Each member of the tuple should be a tuple of
# (Full name, e-mail address). Example:
ADMINS = distro_settings.ADMINS

# A tuple in the same format as ADMINS that specifies who should get
# broken-link notifications when SEND_BROKEN_LINK_EMAILS=True.
MANAGERS = distro_settings.MANAGERS

# Whether to send an e-mail to the MANAGERS each time somebody visits a
# Django-powered page that is 404ed with a non-empty referer (i.e., a broken
# link). This is only used if CommonMiddleware is installed (see Middleware.
# See also IGNORABLE_404_STARTS, IGNORABLE_404_ENDS and Error reporting via
# e-mail.
SEND_BROKEN_LINK_EMAILS = distro_settings.SEND_BROKEN_LINK_EMAILS

# LOG_SIZE_LIMIT in megabytes
LOG_SIZE_LIMIT = distro_settings.LOG_SIZE_LIMIT

# URL of the login page
LOGIN_URL = distro_settings.LOGIN_URL

# URL of the page you get redirected to after logging in
LOGIN_REDIRECT_URL = distro_settings.LOGIN_REDIRECT_URL

# read which openID provider to use from the settings.conf
OPENID_SSO_SERVER_URL = distro_settings.OPENID_SSO_SERVER_URL

# The email address that error messages come from, such as those sent to
# ADMINS and MANAGERS.
if distro_settings.get_setting("SERVER_EMAIL"):
    SERVER_EMAIL = distro_settings.get_setting("SERVER_EMAIL")

# Allow OpenID redirect domains to be configurable
if distro_settings.get_setting("ALLOWED_EXTERNAL_OPENID_REDIRECT_DOMAINS"):
    ALLOWED_EXTERNAL_OPENID_REDIRECT_DOMAINS = distro_settings.get_setting("ALLOWED_EXTERNAL_OPENID_REDIRECT_DOMAINS")

if distro_settings.get_setting("OPENID_LAUNCHPAD_TEAMS_MAPPING"):
    OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO = False
    OPENID_LAUNCHPAD_TEAMS_MAPPING = distro_settings.get_setting("OPENID_LAUNCHPAD_TEAMS_MAPPING")

# Atlassian Crowd authentication config
AUTH_CROWD_SERVER_REST_URI = distro_settings.get_setting("AUTH_CROWD_SERVER_REST_URI")
if AUTH_CROWD_SERVER_REST_URI:
    # If Crowd server URL is configured, disable OpenID and
    # enable Crowd auth backend
    INSTALLED_APPS.append('crowdrest')
    AUTHENTICATION_BACKENDS = ['crowdrest.backend.CrowdRestBackend'] + \
        [x for x in AUTHENTICATION_BACKENDS if "OpenID" not in x]

    # Load credentials from a separate file
    from lava_server.settings.config_file import ConfigFile
    pathname = distro_settings._get_pathname("crowd")
    crowd_config = ConfigFile.load(pathname)
    AUTH_CROWD_APPLICATION_USER = crowd_config.AUTH_CROWD_APPLICATION_USER
    AUTH_CROWD_APPLICATION_PASSWORD = crowd_config.AUTH_CROWD_APPLICATION_PASSWORD
    if distro_settings.get_setting("AUTH_CROWD_GROUP_MAP"):
        AUTH_CROWD_GROUP_MAP = distro_settings.get_setting("AUTH_CROWD_GROUP_MAP")

# Load extensions
loader.contribute_to_settings(locals(), distro_settings)

from django.db.backends.signals import connection_created


def set_timeout(connection, **kw):
    connection.cursor().execute("SET statement_timeout to 30000")

connection_created.connect(set_timeout)
