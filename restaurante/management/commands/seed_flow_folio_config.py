from django.core.management.base import BaseCommand

from restaurante.database_config import ensure_flow_folio_config


class Command(BaseCommand):
    help = 'Seed required Clave_Folio/Numeracion_Folio rows for generated flow documents.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print the flow configuration rows that would be created.',
        )
        parser.add_argument(
            '--no-default-branch',
            action='store_true',
            help='Do not create a minimal default client/branch when none exist.',
        )

    def handle(self, *args, **options):
        summary = ensure_flow_folio_config(
            dry_run=options['dry_run'],
            create_default_branch=not options['no_default_branch'],
        )

        prefix = 'Would create' if options['dry_run'] else 'Created'
        for key in (
            'cliente_sistema',
            'sucursal_sistema',
            'clave_folio',
            'numeracion_folio',
        ):
            count = summary[key]
            if count:
                self.stdout.write('{0} {1} {2} row(s).'.format(prefix, count, key))

        if not any(summary.values()):
            self.stdout.write('Flow folio configuration is already complete.')
