__author__ = 'teacher'

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "restaurante.settings0")

from restaurante.models import ClaveFolio
q = ClaveFolio.objects.get(id=2)
print(q.nombredocumento)

