"""
Tapai Ko Sathi Django project package.

This module intentionally keeps side effects to a minimum.
All app configuration is handled in each app's ``apps.py``.
"""

import pymysql

pymysql.install_as_MySQLdb()

