__author__ = 'teacher'

from django.apps import apps
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
