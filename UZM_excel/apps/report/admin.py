from django.contrib import admin
from .models import *

admin.site.register(Raw)
admin.site.register(DynamicNNBData)
admin.site.register(StaticNNBData)
admin.site.register(IgirgiStatic)
admin.site.register(IgirgiDynamic)
admin.site.register(Plan)
admin.site.register(ReportIndex)
