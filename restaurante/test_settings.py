__author__ = 'teacher'

from django.apps import apps
from django.db import connections
from django.test.runner import DiscoverRunner


DJANGO_CORE_TABLES = {
    'auth_group',
    'auth_group_permissions',
    'auth_permission',
    'auth_user',
    'auth_user_groups',
    'auth_user_user_permissions',
    'django_admin_log',
    'django_content_type',
    'django_migrations',
    'django_session',
}


class ManagedModelTestRunner(DiscoverRunner):
    """Temporarily include legacy unmanaged restaurant tables in test databases.

    The project keeps most business tables outside Django migrations. For tests,
    Django can still create those tables if the model metadata is marked managed
    before the test database is set up. Tables owned by Django contrib apps stay
    excluded because their migrations create the real auth/session schemas.
    """

    def setup_databases(self, **kwargs):
        old_config = super(ManagedModelTestRunner, self).setup_databases(**kwargs)
        self._create_prefetch_id_sequences()
        return old_config

    def setup_test_environment(self, *args, **kwargs):
        self.unmanaged_models = [
            model
            for model in apps.get_models()
            if not model._meta.managed and model._meta.db_table not in DJANGO_CORE_TABLES
        ]
        for m in self.unmanaged_models:
            m._meta.managed = True
        super(ManagedModelTestRunner, self).setup_test_environment(*args,**kwargs)

    def teardown_test_environment(self, *args, **kwargs):
        super(ManagedModelTestRunner, self).teardown_test_environment(*args, **kwargs)
        for m in self.unmanaged_models:
            m._meta.managed = False

    def _create_prefetch_id_sequences(self):
        connection = connections['default']
        if connection.vendor != 'postgresql':
            return

        with connection.cursor() as cursor:
            for model in self.unmanaged_models:
                pk = model._meta.pk
                if pk is None or pk.db_column != 'ID':
                    continue
                sequence_name = '{0}_ID_seq'.format(model._meta.db_table)
                cursor.execute(
                    'CREATE SEQUENCE IF NOT EXISTS {0}'.format(
                        connection.ops.quote_name(sequence_name)
                    )
                )
