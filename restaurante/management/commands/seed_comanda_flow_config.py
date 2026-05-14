from django.core.management.base import BaseCommand

from restaurante.database_config import ensure_comanda_flow_config


class Command(BaseCommand):
    help = 'Seed minimal configuration rows required by the high-level comanda API flow.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print the comanda flow configuration rows that would be created.',
        )
        parser.add_argument(
            '--no-default-branch',
            action='store_true',
            help='Do not create a minimal default client/branch when none exist.',
        )

    def handle(self, *args, **options):
        summary = ensure_comanda_flow_config(
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
            'tipo_cuenta_contable',
            'catalogo_clasificacion',
            'ubicacion_area_preparacion',
            'ubicacion_mesa',
            'detalle_ubicacion',
            'registro_maestro',
            'receta_item',
            'stock_ingrediente',
            'configuracion_comanda',
            'regla_ruteo_preparacion',
            'comanda_clave_folio',
            'comanda_numeracion_folio',
            'comanda_documento_movimiento',
            'comanda_documento_concepto',
        ):
            count = summary[key]
            if count:
                self.stdout.write('{0} {1} {2} row(s).'.format(prefix, count, key))

        if not any(summary.values()):
            self.stdout.write('Comanda flow configuration is already complete.')
