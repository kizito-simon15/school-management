from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView, View
from .forms import InvoiceItemFormset, InvoiceReceiptFormSet
from .models import Invoice, InvoiceItem, Receipt, SalaryInvoice
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.template.loader import render_to_string


class SalaryInvoiceListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = SalaryInvoice
    template_name = 'finance/salary_list.html'
    context_object_name = 'invoices'
    paginate_by = 10
    permission_required = 'finance.view_salaryinvoice'
    permission_denied_message  = 'Access Denied'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.GET.get('q')
        if search_term:
            queryset = queryset.filter(
                Q(staff__surname__icontains=search_term) |
                Q(staff__firstname__icontains=search_term) |
                Q(month__icontains=search_term) |
                Q(issued_date__icontains=search_term)
            )

        # Apply ordering to the queryset
        queryset = queryset.order_by('-month', '-issued_date')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoices = context['invoices']

        # Calculate total net salary, gross salary, and deductions for each month
        invoices_by_month = []
        current_month = None
        total_net_salary = 0
        total_gross_salary = 0
        total_deductions = 0

        for invoice in invoices:
            if invoice.month != current_month:
                # Append total for previous month, if applicable
                if current_month is not None:
                    invoices_by_month.append({
                        'month': current_month,
                        'total_net_salary': total_net_salary,
                        'total_gross_salary': total_gross_salary,
                        'total_deductions': total_deductions,
                    })
                # Reset totals for new month
                current_month = invoice.month
                total_net_salary = 0
                total_gross_salary = 0
                total_deductions = 0

            total_net_salary += invoice.net_salary
            total_gross_salary += invoice.gross_salary
            total_deductions += invoice.deductions

        # Append totals for the last month
        if current_month is not None:
            invoices_by_month.append({
                'month': current_month,
                'total_net_salary': total_net_salary,
                'total_gross_salary': total_gross_salary,
                'total_deductions': total_deductions,
            })

        context['invoices_by_month'] = invoices_by_month
        return context


def salary_list(request):
    search_term = request.GET.get('q')
    year = request.GET.get('year')
    month = request.GET.get('month')

    # Filter salary invoices by year and month
    invoices = SalaryInvoice.objects.all()

    if year and month:
        invoices = invoices.filter(month__year=year, month__month=month)

    # Apply search filter
    if search_term:
        invoices = invoices.filter(
            Q(staff__surname__icontains=search_term) |
            Q(staff__firstname__icontains=search_term) |
            Q(month__icontains=search_term) |
            Q(issued_date__icontains=search_term)
        )

    # Calculate total net salary, gross salary, and deductions for the given month
    total_net_salary = invoices.aggregate(total_net_salary=Sum('net_salary'))['total_net_salary'] or 0
    total_gross_salary = invoices.aggregate(total_gross_salary=Sum('gross_salary'))['total_gross_salary'] or 0
    total_deductions = invoices.aggregate(total_deductions=Sum('deductions'))['total_deductions'] or 0

    context = {
        'invoices': invoices,
        'year': year,
        'month': month,
        'search_term': search_term,
        'total_net_salary': total_net_salary,
        'total_gross_salary': total_gross_salary,
        'total_deductions': total_deductions,
    }

    return render(request, 'finance/salary_list.html', context)

class SalaryInvoiceDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = SalaryInvoice
    template_name = 'finance/salary_detail.html'
    context_object_name = 'invoice'
    permission_required = 'finance.view_salaryinvoice'
    permission_denied_message = 'Access Denied'


class SalaryInvoiceCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = SalaryInvoice
    template_name = 'finance/salary_form.html'
    fields = ['staff', 'month', 'gross_salary', 'deductions', 'issued_date', 'remarks']  # Exclude 'net_salary'
    success_url = reverse_lazy('salary-invoice-list')
    permission_required = 'finance.add_salaryinvoice'
    permission_denied_message = 'Access Denied'

    def form_valid(self, form):
        # Calculate net salary before saving
        form.instance.net_salary = form.instance.gross_salary - form.instance.deductions
        return super().form_valid(form)


class SalaryInvoiceUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = SalaryInvoice
    template_name = 'finance/salary_form.html'
    fields = ['staff', 'month', 'gross_salary', 'deductions', 'issued_date', 'remarks']
    success_url = reverse_lazy('salary-invoice-list')
    permission_required = 'finance.change_salaryinvoice'
    permission_denied_message = 'Access Denied'


class SalaryInvoiceDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = SalaryInvoice
    template_name = 'finance/salary_confirm_delete.html'
    success_url = reverse_lazy('salary-invoice-list')
    permission_required = 'finance.delete_salaryinvoice'
    permission_denied_message = 'Access Denied'


class InvoiceListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Invoice
    permission_required = 'finance.view_invoice'
    permission_denied_message = 'Acess denied'


class InvoiceCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Invoice
    fields = "__all__"
    success_url = "/finance/list"
    permission_required = 'finance.add_invoice'
    permission_required = 'Access Denied'

    def get_context_data(self, **kwargs):
        context = super(InvoiceCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context["items"] = InvoiceItemFormset(
                self.request.POST, prefix="invoiceitem_set"
            )
        else:
            context["items"] = InvoiceItemFormset(prefix="invoiceitem_set")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["items"]
        self.object = form.save()
        if self.object.id is not None:
            if form.is_valid() and formset.is_valid():
                formset.instance = self.object
                formset.save()
        return super().form_valid(form)


class InvoiceUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Invoice
    fields = ["student", "session", "term", "class_for", "balance_from_previous_term"]
    permission_required = 'finance.change_invoice'
    permission_denied_message = 'Access Denied'

    def get_context_data(self, **kwargs):
        context = super(InvoiceUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context["receipts"] = InvoiceReceiptFormSet(
                self.request.POST, instance=self.object
            )
            context["items"] = InvoiceItemFormset(
                self.request.POST, instance=self.object
            )
        else:
            context["receipts"] = InvoiceReceiptFormSet(instance=self.object)
            context["items"] = InvoiceItemFormset(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["receipts"]
        itemsformset = context["items"]
        if form.is_valid() and formset.is_valid() and itemsformset.is_valid():
            form.save()
            formset.save()
            itemsformset.save()
        return super().form_valid(form)


class InvoiceDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Invoice
    fields = "__all__"
    permission_required = 'finance.view_invoice'
    permission_denied_message = 'Access Denied'

    def get_context_data(self, **kwargs):
        context = super(InvoiceDetailView, self).get_context_data(**kwargs)
        context["receipts"] = Receipt.objects.filter(invoice=self.object)
        context["items"] = InvoiceItem.objects.filter(invoice=self.object)
        return context


class SearchStudents(View):
    def get(self, request):
        term = request.GET.get('term')
        students = Student.objects.filter(name__icontains=term)
        data = [{'id': student.id, 'text': student.name} for student in students]
        return JsonResponse(data, safe=False)


class InvoiceDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Invoice
    success_url = reverse_lazy("invoice-list")
    permission_required = 'finance.delete_invoice'
    permission_denied_message = 'Access Denied'


class ReceiptCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Receipt
    fields = ["amount_paid", "date_paid", "comment", "payment_method"]  # Include the payment_method field
    success_url = reverse_lazy("invoice-list")
    permission_required = 'finance.add_receipt'
    permission_denied_message = "Access Denied"

    def form_valid(self, form):
        try:
            obj = form.save(commit=False)
            invoice = get_object_or_404(Invoice, pk=self.request.GET.get("invoice"))
            obj.invoice = invoice
            obj.save()
            return super().form_valid(form)
        except Exception as e:
            # Handle any exceptions here
            return HttpResponseRedirect(reverse_lazy("invoice-list"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = get_object_or_404(Invoice, pk=self.request.GET.get("invoice"))
        context["invoice"] = invoice
        return context



class ReceiptUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Receipt
    fields = ["amount_paid", "date_paid", "comment", "payment_method"]  # Include the payment_method field
    success_url = reverse_lazy("invoice-list")
    permission_required = 'finance.change_receipt'
    permission_denied_message = 'Access Denied'
    

class ReceiptDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Receipt
    success_url = reverse_lazy("invoice-list")
    permission_required = 'finance.delete_receipt'
    permission_denied_message = 'Access Denied'


@login_required
def bulk_invoice(request):
    return render(request, "finance/bulk_invoice.html")


def save_pdf(request):
    invoices = SalaryInvoice.objects.all()  # Assuming you have a SalaryInvoice model
    template_path = 'salary_pdf_template.html'  # Create a template for PDF generation
    context = {'invoices': invoices}
    # Render the template
    template = get_template(template_path)
    html = template.render(context)
    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="salary_invoices.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def print_pdf(request):
    invoices = SalaryInvoice.objects.all().order_by('-issued_date')
    context = {'invoices': invoices}
    html = render_to_string('finance/salary_list.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="salary_invoices.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


