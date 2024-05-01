from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from apps.corecode.models import AcademicSession, AcademicTerm, ExamType, StudentClass, Subject
from apps.students.models import Student
from django.db.models import Sum, Avg, Count

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    exam = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    current_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    test_score = models.IntegerField(
        null=True, blank=True, default=None, validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    exam_score = models.IntegerField(
        null=True, blank=True, default=None, validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    average = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    overall_average = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    overall_status = models.CharField(max_length=10, default='FAIL')
    status = models.CharField(max_length=10, default='FAIL')
    gpa = models.DecimalField(max_digits=5, decimal_places=3, default=0.000)
    subject_grade = models.CharField(max_length=1, default='F')


    class Meta:
        ordering = ["subject"]

    def __str__(self):
        return f"{self.student} {self.session} {self.term} {self.subject}"

    def save(self, *args, **kwargs):
        if self.test_score is not None and self.exam_score is None:
            # If test score is provided and exam score is None
            self.average = self.test_score
        elif self.test_score is None and self.exam_score is not None:
            # If test score is None and exam score is provided
            self.average = self.exam_score
        elif self.test_score is not None and self.exam_score is not None:
            # If both test score and exam score are provided
            self.average = (self.test_score + self.exam_score) / 2
        else:
            # If both test score and exam score are None
            self.average = 0
            
        self.overall_average = self.calculate_overall_average()

        super().save(*args, **kwargs)

    def calculate_overall_average(self):
        # Retrieve all results for the student
        student_results = Result.objects.filter(student=self.student)

        # Calculate the total sum of averages
        total_sum_average = sum(result.average for result in student_results)

        # Calculate the overall average
        overall_average = total_sum_average / student_results.count()

        return overall_average

    def calculate_result(self):
        # Calculate result attributes after saving
        pass

    def calculate_total_sum_average(self):
        """
        Calculate the total of all subject averages.
        """
        # Retrieve all results for the student
        student_results = Result.objects.filter(student=self.student)

        # Calculate the total average
        total_sum_average = sum(result.average for result in student_results)

        return total_sum_average


    def calculate_overall_status(self):
        if self.overall_average >= 25:
            return "PASS"
        else:
            return "FAIL"

    def calculate_status(self):
        if self.average >= 25:
            return "PASS"
        else:
            return "FAIL"

    def calculate_grade(self):
        if self.average >= 41:
            return "A"
        elif 30 <= self.average < 41:
            return "B"
        elif 25 <= self.average < 30:
            return "C"
        elif 15 <= self.average < 25:
            return "D"
        else:
            return "F"

    def calculate_overall_total_marks(self):
        return Subject.objects.count() * 50

    @classmethod
    def calculate_overall_grade(cls, student):
        # Get all results for the student
        student_results = Result.objects.filter(student=student)

        # Calculate the overall average
        overall_average = sum(result.average for result in student_results) / student_results.count()

        # Determine the overall grade based on the overall average
        if overall_average >= 41:
            return "A"
        elif 30 <= overall_average < 41:
            return "B"
        elif 24 < overall_average < 30:
            return "C"
        elif 14 < overall_average <= 24:
            return "D"
        else:
            return "F"

    def calculate_comments(self):
        if self.average is not None:
            grade = self.calculate_grade()
            if grade == "A":
                return "VIZURI SANA"
            elif grade == "B":
                return "VIZURI"
            elif grade == "C":
                return "WASTANI"
            elif grade == "D":
                return "HAFIFU"
            else:
                return "MBAYA"
        else:
            return "No grades available"


    @classmethod
    def calculate_position(cls, overall_average):
        """
        Calculate the position based on overall average.
        """
        if overall_average is not None:
            # Get all distinct overall averages in descending order
            distinct_averages = cls.objects.values_list('overall_average', flat=True).distinct().order_by('-overall_average')
            # Find the position of the current overall average
            try:
                position = list(distinct_averages).index(overall_average) + 1
            except ValueError:
                position = None
        else:
            position = None
        return position

    @classmethod
    def calculate_student_position(cls, overall_average, student_class):
        if overall_average is not None:
            # Retrieve all distinct overall averages for students in the same class
            distinct_averages = cls.objects.filter(
                student__current_class=student_class
            ).values_list('overall_average', flat=True).distinct().order_by('-overall_average')

            # Find the position of the current overall average
            try:
                student_position = list(distinct_averages).index(overall_average) + 1
            except ValueError:
                student_position = None
        else:
            student_position = None
        return student_position

    @classmethod
    def total_students(cls, class_name):
        # Implement logic to count total students in the given class
        # For example:
        return Student.objects.filter(current_class=class_name).count()

    def calculate_gpa(self):
        # Map grades to points
        grade_points = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'F': 0}

        # Retrieve all results for the student
        results = Result.objects.filter(student=self.student)

        # Calculate total points
        total_points = sum(grade_points.get(result.calculate_grade(), 0) for result in results)

        # Calculate GPA
        count = results.count()
        if count == 0:
            return 0.000  # Handle the case when there are no results
        else:
            return round(total_points / count, 3)

    @classmethod
    def calculate_subject_gpa(cls, student_class, subject):
        # Map grades to points
        grade_points = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'F': 0}

        # Retrieve all results for the given class and subject
        results = Result.objects.filter(current_class=student_class, subject=subject)

        # Calculate total points for the subject
        total_points = sum(grade_points.get(result.calculate_grade(), 0) for result in results)

        # Calculate total number of students
        count = results.count()

        # Calculate GPA for the subject
        if count == 0:
            return 0.000  # Handle the case when there are no results
        else:
            return round(total_points / count, 3)

    @classmethod
    def calculate_subject_overall_average(cls, student_class, subject):
        # Retrieve all results for the given class and subject
        results = Result.objects.filter(current_class=student_class, subject=subject)

        # Calculate total average of the subject for all students in the class
        total_average = sum(result.average for result in results)

        # Calculate total number of students taking the subject
        count = results.count()

        # Calculate subject overall average
        if count == 0:
            return 0.00  # Handle the case when there are no results
        else:
            return round(total_average / count, 2)
    
    def calculate_subject_grade(self, student_class, subject):
        # Retrieve all results for the given class and subject
        results = Result.objects.filter(current_class=student_class, subject=subject)

        # Calculate subject overall average
        subject_overall_average = self.calculate_subject_overall_average(student_class, subject)

        # Determine the subject grade based on the subject overall average
        if subject_overall_average >= 41:
            return "A"
        elif 30 <= subject_overall_average < 41:
            return "B"
        elif 25 <= subject_overall_average < 30:
            return "C"
        elif 15 <= subject_overall_average < 25:
            return "D"
        else:
            return "F"