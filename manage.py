#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
# Ensure PyMySQL provides MySQLdb interface when mysqlclient is not installed.
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    # Bypass MySQL 8.0+ version requirement for MariaDB/older MySQL
    from django.db.backends.mysql.base import DatabaseWrapper
    DatabaseWrapper.check_database_version_supported = lambda self: None
except Exception:
    pass


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tapai_ko_sathi.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
