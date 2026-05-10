from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection

from restaurante.test_settings import DJANGO_CORE_TABLES


class Command(BaseCommand):
    help = (
        'Create missing unmanaged restaurant tables and PostgreSQL ID sequences '
        'from Django model metadata.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print the tables and sequences that would be created.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        existing_tables = set(connection.introspection.table_names())
        legacy_models = [
            model
            for model in apps.get_models()
            if not model._meta.managed and model._meta.db_table not in DJANGO_CORE_TABLES
        ]

        missing_models = [
            model for model in legacy_models if model._meta.db_table not in existing_tables
        ]

        for model in missing_models:
            table_name = model._meta.db_table
            if dry_run:
                self.stdout.write('Would create table {0}'.format(table_name))
                continue

            self.stdout.write('Creating table {0}'.format(table_name))
            with connection.schema_editor() as schema_editor:
                schema_editor.create_model(model)

        self._create_prefetch_sequences(legacy_models, dry_run)

        if not missing_models and dry_run:
            self.stdout.write('No missing legacy tables detected.')

    def _create_prefetch_sequences(self, legacy_models, dry_run):
        if connection.vendor != 'postgresql':
            return

        with connection.cursor() as cursor:
            for model in legacy_models:
                pk = model._meta.pk
                if pk is None or pk.get_internal_type() not in (
                    'AutoField',
                    'BigAutoField',
                    'BigIntegerField',
                    'IntegerField',
                ):
                    continue

                sequence_name = '{0}_ID_seq'.format(model._meta.db_table)
                if dry_run:
                    self.stdout.write('Would ensure sequence {0}'.format(sequence_name))
                    continue

                cursor.execute(
                    'CREATE SEQUENCE IF NOT EXISTS {0}'.format(
                        connection.ops.quote_name(sequence_name)
                    )
                )
