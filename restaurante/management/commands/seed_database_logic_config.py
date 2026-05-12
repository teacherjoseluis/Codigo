from django.core.management.base import BaseCommand

from restaurante.database_config import ensure_database_logic_config


class Command(BaseCommand):
    help = 'Seed minimal reference rows required by Restaurante database logic.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print the database logic configuration rows that would be created.',
        )
        parser.add_argument(
            '--no-default-branch',
            action='store_true',
            help='Do not create a minimal default client/branch when none exist.',
        )

    def handle(self, *args, **options):
        summary = ensure_database_logic_config(
            dry_run=options['dry_run'],
            create_default_branch=not options['no_default_branch'],
        )

        if options['verbosity'] < 1:
            return

        prefix = 'Would create' if options['dry_run'] else 'Created'
        for key in (
            'cliente_sistema',
            'sucursal_sistema',
            'clave_folio',
            'numeracion_folio',
            'documento_movimiento',
            'cuenta_contable',
            'clave_folio_operacional',
            'numeracion_folio_operacional',
            'documento_concepto',
            'libro_contable',
            'libro_sucursal',
        ):
            count = summary[key]
            if count:
                self.stdout.write('{0} {1} {2} row(s).'.format(prefix, count, key))

        if not any(summary.values()):
            self.stdout.write('Database logic configuration is already complete.')
