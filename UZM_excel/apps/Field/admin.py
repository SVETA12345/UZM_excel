from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *


admin.site.register(ContractorNNB)
admin.site.register(ContractorDrill)
admin.site.register(Client)
admin.site.register(Field)
admin.site.register(Pad)
admin.site.register(Well)
admin.site.register(Wellbore)
admin.site.register(Section)
admin.site.register(Run)
admin.site.register(WellSummary)

