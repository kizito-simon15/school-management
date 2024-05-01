from django.urls import path
from .views import (
    InvoiceCreateView,
    InvoiceDeleteView,
    InvoiceDetailView,
    InvoiceListView,
    InvoiceUpdateView,
    ReceiptCreateView,
    ReceiptUpdateView,
    bulk_invoice,
    #salary invoice view
    SalaryInvoiceListView, 
    SalaryInvoiceDetailView, 
    SalaryInvoiceCreateView, 
    SalaryInvoiceUpdateView, 
    SalaryInvoiceDeleteView,
    print_pdf,
    save_pdf,
    salary_list,
    SearchStudents,
    
)
#urls for Student Invoice
urlpatterns = [
    path("list/", InvoiceListView.as_view(), name="invoice-list"),
    path("create/", InvoiceCreateView.as_view(), name="invoice-create"),
    path("<int:pk>/detail/", InvoiceDetailView.as_view(), name="invoice-detail"),
    path("<int:pk>/update/", InvoiceUpdateView.as_view(), name="invoice-update"),
    path("<int:pk>/delete/", InvoiceDeleteView.as_view(), name="invoice-delete"),
    path("receipt/create", ReceiptCreateView.as_view(), name="receipt-create"),
    path("receipt/<int:pk>/update/", ReceiptUpdateView.as_view(), name="receipt-update"),
    path("bulk-invoice/", bulk_invoice, name="bulk-invoice"),
    #urls for SalaryInvoice
    path('invoices/', SalaryInvoiceListView.as_view(), name='salary-invoice-list'),
    path('search-students/', SearchStudents.as_view(), name='search_students'),
    path('invoices/print/', print_pdf, name='print-pdf'),
    path('save-pdf/', save_pdf, name='save-pdf'),
    path('salary-list/', salary_list, name='salary_list'), 
    path('invoices/<int:pk>/', SalaryInvoiceDetailView.as_view(), name='salary-invoice-detail'),
    path('invoices/create/', SalaryInvoiceCreateView.as_view(), name='salary-invoice-create'),
    path('invoices/<int:pk>/update/', SalaryInvoiceUpdateView.as_view(), name='salary-invoice-update'),
    path('invoices/<int:pk>/delete/', SalaryInvoiceDeleteView.as_view(), name='salary-invoice-delete'),
]
