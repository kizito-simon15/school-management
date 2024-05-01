from django.contrib import admin
from .models import Category, Expenditure, ExpenditureInvoice

# Register your models here.
admin.site.register(Category)
admin.site.register(Expenditure)
admin.site.register(ExpenditureInvoice)

