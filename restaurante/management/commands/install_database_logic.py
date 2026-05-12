from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    help = 'Install or preview the Restaurante PL/pgSQL database logic.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print the SQL file path and size without executing it.',
        )

    def handle(self, *args, **options):
        sql_path = (
            Path(__file__).resolve().parents[2]
            / 'sql'
            / 'database_logic.sql'
        )

        if not sql_path.exists():
            raise SystemExit('Database logic SQL not found: {0}'.format(sql_path))

        sql = sql_path.read_text(encoding='utf-8')

        if options['dry_run']:
            self.stdout.write(
                'Would execute {0} ({1} bytes).'.format(sql_path, len(sql))
            )
            return

        if connection.vendor != 'postgresql':
            raise SystemExit(
                'Database logic requires PostgreSQL; current vendor is {0}.'.format(
                    connection.vendor
                )
            )

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(sql)

        if options['verbosity'] > 0:
            self.stdout.write(
                self.style.SUCCESS('Installed database logic from {0}'.format(sql_path))
            )
