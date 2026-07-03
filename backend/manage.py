#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import sys

from config.server import ensure_dev_settings, inject_runserver_port


def main():
    """Run administrative tasks."""
    ensure_dev_settings()
    inject_runserver_port(sys.argv)
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
