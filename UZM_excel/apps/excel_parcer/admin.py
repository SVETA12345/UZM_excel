from django.contrib import admin
from .models import Device, Data, List

admin.site.register(Device)
admin.site.register(List)


@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    list_display = ("run", "depth", 'CX', "CX", "CY", "CZ", "BX", "BY", "BZ", "in_statistics")
    search_fields = ("run__run_number", "depth")
