from django.contrib import admin
from .models import ClaveFolio


class ClaveFolioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombredocumento', 'clavefolio', 'id_clientesistema')
    search_fields = ('nombredocumento', 'clavefolio')


admin.site.register(ClaveFolio, ClaveFolioAdmin)
