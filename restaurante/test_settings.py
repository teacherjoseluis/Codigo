__author__ = 'teacher'

from django.conf import settings
from django.test.runner import DiscoverRunner
from django.core.management import call_command

class ManagedModelTestRunner(DiscoverRunner):

    def setup_databases(self, **kwargs):
        from django.db import connections
        settings = connections['default'].settings_dict
        settings['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
        call_command('syncdb', verbosity=1, interactive=False, load_initial_data=False)

    def teardown_databases(self, old_config, **kwargs):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute('show tables;')
        parts = ('DROP TABLE IF EXISTS %s;' % table for (table,) in cursor.fetchall())
        sql = 'SET FOREIGN_KEY_CHECKS = 0;\n' + '\n'.join(parts) + 'SET FOREIGN_KEY_CHECKS = 1;\n'
        connection.cursor().execute(sql)

    def setup_test_environment(self, *args, **kwargs):
        from django.db.models.loading import get_models
        self.unmanaged_models = [m for m in get_models() if not m._meta.managed]
        for m in self.unmanaged_models:
            m._meta.managed = True
        super(ManagedModelTestRunner, self).setup_test_environment(*args,**kwargs)

    def teardown_test_environment(self, *args, **kwargs):
        super(ManagedModelTestRunner, self).teardown_test_environment(*args, **kwargs)
# reset unmanaged models
        for m in self.unmanaged_models:
            m._meta.managed = False
