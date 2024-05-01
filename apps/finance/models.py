from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass
from apps.students.models import Student
from apps.staffs.models import Staff

class SalaryInvoice(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    month = models.DateField(default=timezone.now)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, editable=False)  # Net salary is calculated based on gross salary and deductions
    issued_date = models.DateField(default=timezone.now)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Invoice for {self.staff.surname} {self.staff.firstname} - {self.month.strftime('%B %Y')}"

    def get_absolute_url(self):
        return reverse("salary-invoice-detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        # Calculate net salary before saving
        self.net_salary = self.gross_salary - self.deductions
        super().save(*args, **kwargs)
        


class Invoice(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    class_for = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    balance_from_previous_term = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[("active", "Active"), ("closed", "Closed")],
        default="active",
    )

    class Meta:
        ordering = ["student"]

    def __str__(self):
        return f"{self.student}"

    def balance(self):
        payable = self.total_amount_payable()
        paid = self.total_amount_paid()
        return payable - paid

    def amount_payable(self):
        items = InvoiceItem.objects.filter(invoice=self)
        total = 0
        for item in items:
            total += item.amount
        return total

    def total_amount_payable(self):
        return self.balance_from_previous_term + self.amount_payable()

    def total_amount_paid(self):
        receipts = Receipt.objects.filter(invoice=self)
        amount = 0
        for receipt in receipts:
            amount += receipt.amount_paid
        return amount

    def get_absolute_url(self):
        return reverse("invoice-detail", kwargs={"pk": self.pk})


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    amount = models.IntegerField()



class Receipt(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount_paid = models.IntegerField()
    date_paid = models.DateField(default=timezone.now)
    comment = models.CharField(max_length=200, blank=True)
    
    # Define the choices for payment methods
    PAYMENT_METHOD_CHOICES = [
        ('NMB_BANK', 'NMB BANK'),
        ('M_PESA', 'M-PESA'),
        ('CASH', 'CASH'),
    ]
    
    # Add the payment_method field
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
    )

    def __str__(self):
        return f"Receipt on {self.date_paid}"

