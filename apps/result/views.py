from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import DetailView, ListView, View
from apps.corecode.models import AcademicSession, AcademicTerm,ExamType,SiteConfig, StudentClass, Subject
from apps.students.models import Student
from collections import defaultdict
from .forms import CreateResults, EditResults, ViewResultsForm, ViewResultsFormSet
from .models import Result
from django.views.generic.base import TemplateView
from django.db.models import Sum, Avg, Count
from django.forms import formset_factory, modelformset_factory
from django.db.models import Q

@login_required
@permission_required('result.add_result', raise_exception=True)
def create_result(request):
    students = Student.objects.all()
    
        # Logic to determine the current session
    current_session = AcademicSession.objects.filter(current=True).first()
    if current_session is None:
        # Handle the case where no session is active for the current date
        # Perhaps set a default session or display an error message
        pass

    # Logic to determine the current term
    current_term = AcademicTerm.objects.filter(current=True).first()
    if current_term is None:
        # Handle the case where no term is active for the current date
        # Perhaps set a default term or display an error message
        pass
    
    current_exam = ExamType.objects.filter(current=True).first()
    if current_exam is None:
        # Handle the case where no exam type is active
        # Perhaps set a default exam type or display an error message
        pass
    
    # Set current_session and current_term in the session
    request.session['current_session'] = current_session.id if current_session else None
    request.session['current_term'] = current_term.id if current_term else None
    request.session['current_exam'] = current_exam.id if current_exam else None


    # Group students by class
    students_by_class = {}
    for student in students:
        class_key = student.current_class
        if class_key not in students_by_class:
            students_by_class[class_key] = []
        students_by_class[class_key].append(student)

    if request.method == "POST":
        # after visiting the second page
        if "finish" in request.POST:
            form = CreateResults(request.POST)
            if form.is_valid():
                subjects = form.cleaned_data["subjects"]
                session = form.cleaned_data["session"]
                term = form.cleaned_data["term"]
                exam = form.cleaned_data["exam"]
                students = request.POST.get("students")
                if students:  # Check if students are selected
                    results = []
                    for student in students.split(","):
                        stu = Student.objects.get(pk=student)
                        if stu.current_class:
                            for subject in subjects:
                                check = Result.objects.filter(
                                    session=session,
                                    term=term,
                                    exam=exam,
                                    current_class=stu.current_class,
                                    subject=subject,
                                    student=stu,
                                ).first()
                                if not check:
                                    results.append(
                                        Result(
                                            session=session,
                                            term=term,
                                            exam=exam,
                                            current_class=stu.current_class,
                                            subject=subject,
                                            student=stu,
                                        )
                                    )

                    Result.objects.bulk_create(results)
                    # Store selected students in session
                    request.session['selected_students'] = students
                    # Store selected student's name in session
                    selected_student_names = ', '.join([f"{Student.objects.get(pk=student_id).surname} {Student.objects.get(pk=student_id).firstname} {Student.objects.get(pk=student_id).other_name}" for student_id in students.split(",")])
                    request.session['selected_student_name'] = selected_student_names
                    # Redirect to edit-results
                    return redirect("edit-results")
                else:
                    messages.warning(request, "You didn't select any student.")
                    # Render the customized template
                    return render(request, "result/create_result.html", {"students": students, "students_by_class": students_by_class})
                     
        # after choosing students
        id_list = request.POST.getlist("students")
        if id_list:
            # Store selected students in session
            request.session['selected_students'] = id_list
            form = CreateResults(
                initial={
                    "session": request.session.get('current_session'),
                    "term": request.session.get('current_term'),
                    "exam": request.session.get('current_exam'),
                }
            )
            studentlist = ",".join(id_list)
            return render(
                request,
                "result/create_result_page2.html",  # Render create_results_part2.html template
                {"students": studentlist, "form": form, "count": len(id_list), "students_by_class": students_by_class},
            )
        else:
            messages.warning(request, "You didn't select any student.")

    # Render the customized template
    return render(request, "result/create_result.html", {"students": students, "students_by_class": students_by_class})


@login_required
@permission_required('result.add_result', raise_exception=True)
def edit_results(request):
    student_classes = StudentClass.objects.all()
    subjects = Subject.objects.all()

    if request.method == "POST":
        formset = EditResults(request.POST)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data.get('DELETE', False):  # Check if the form should be deleted
                    instance = form.instance
                    if instance.pk:  # Check if the instance exists
                        instance.delete()  # Delete the instance
                else:
                    form.save()  # Save the form if not marked for deletion
                    form.instance.calculate_result()
            messages.success(request, "Results successfully updated")
            return redirect("edit-results")
    else:
        class_select = request.GET.get('class_select')
        subject_select = request.GET.get('subject_select')
        student_name = request.GET.get('student_name')

        results = Result.objects.filter(session=request.current_session, term=request.current_term, exam=request.current_exam)

        if class_select:
            results = results.filter(current_class_id=class_select)

        if subject_select:
            results = results.filter(subject_id=subject_select)

        if student_name:
            results = results.filter(
                Q(student__firstname__icontains=student_name) |
                Q(student__surname__icontains=student_name) |
                Q(student__other_name__icontains=student_name)
            )

        formset = EditResults(queryset=results)
    return render(request, "result/edit_results.html", {"formset": formset, "student_classes": student_classes, "subjects": subjects})

class StudentResultsView(PermissionRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'result/student_results.html'
    permission_required = 'result.view_result'
    permission_denied_message = 'Access Denied'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = kwargs.get('student_id')  # Assuming you pass the student id through URL

        # Retrieve the student
        student = get_object_or_404(Student, pk=student_id)

        # Retrieve current session, term, and exam
        current_session = AcademicSession.objects.filter(current=True).first()
        current_term = AcademicTerm.objects.filter(current=True).first()
        current_exam = ExamType.objects.filter(current=True).first()

        # Retrieve results for the specified student, session, term, and exam
        student_results = Result.objects.filter(
            student_id=student_id,
            session=current_session,
            term=current_term,
            exam=current_exam
        )

        # Pass the student's name to the template
        context['student_name'] = f"{student.firstname} {student.surname} {student.other_name}"
        context['student_class'] = student.current_class

        # Calculate total marks for each subject
        subjects = {}
        total_marks = 0
        for result in student_results:
            subject_name = result.subject.name
            if subject_name not in subjects:
                subjects[subject_name] = {
                    'test_score': result.test_score or 0,
                    'exam_score': result.exam_score or 0,
                    'average': result.average or 0,
                    'total': result.total,
                    'grade': result.calculate_grade(),  # Call calculate_grade here to ensure 'grade' attribute is set
                    'status': result.calculate_status(),
                    'comments': result.calculate_comments(),  # Calculate comments for each subject
                }
            else:
                subjects[subject_name]['test_score'] += result.test_score or 0
                subjects[subject_name]['exam_score'] += result.exam_score or 0
                subjects[subject_name]['average'] += result.average or 0
            total_marks += result.average  # Update to sum of averages

        # Pass the calculated results to the template
        context['subjects'] = subjects

        # Pass current session, term, and exam to the template
        context['current_session'] = current_session.name if current_session else None
        context['current_term'] = current_term.name if current_term else None
        context['current_exam'] = current_exam.name if current_exam else None

        # Calculate additional fields
        context['total'] = total_marks  # Update to sum of averages
        context['overall_average'] = total_marks / len(subjects) if subjects else None
        context['overall_total_marks'] = len(subjects) * 50  # Assuming 50 is the highest marks
        context['overall_grade'] = Result.calculate_overall_grade(student) if student_results else None
        total_students = Result.total_students(student.current_class.id)
        context['total_students'] = total_students
        
        # Calculate overall averages for all students in the class
        student_class = student.current_class
        all_students = Student.objects.filter(current_class=student_class)
        overall_averages = []
        for each_student in all_students:
            student_results = Result.objects.filter(
                student=each_student,
                session=current_session,
                term=current_term,
                exam=current_exam
            )
            total_marks = sum(result.average for result in student_results)
            overall_avg = total_marks / len(subjects) if subjects else None
            overall_averages.append((each_student, overall_avg))

        # Sort students based on overall average
        sorted_students = sorted(overall_averages, key=lambda x: x[1], reverse=True)

        # Find student position
        student_position = None
        for i, (student_in_list, overall_avg) in enumerate(sorted_students, start=1):
            if student == student_in_list:
                student_position = i
                break

        context['student_position'] = student_position

        # Set the grade attribute for each result
        for result in student_results:
            result.grade = result.calculate_grade()

        return context


class ClassResultsView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'result/class_results.html'
    permission_required = 'result.view_result'

    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs.get('class_id')
        selected_class = StudentClass.objects.get(pk=class_id)
        session = AcademicSession.objects.get(current=True)
        term = AcademicTerm.objects.get(current=True)
        exam = ExamType.objects.get(current=True)

        context['class_id'] = class_id
        context['selected_class'] = selected_class

        students = Student.objects.filter(current_class=selected_class)

        data = []
        subjects = set()
        for student in students:
            student_data = {
                'student': student,
                'student_class': student.current_class,
                'subjects': {}
            }

            student_results = Result.objects.filter(
                student=student,
                session=session,
                term=term,
                exam=exam
            )

            # Calculate total marks and overall average
            total_marks = student_results.aggregate(total_marks=Sum('average'))['total_marks'] or 0
            overall_average = total_marks / len(student_results) if len(student_results) > 0 else 0
            overall_status = "PASS" if overall_average >= 25 else "FAIL"

            student_data['total'] = total_marks
            student_data['overall_average'] = overall_average
            student_data['overall_status'] = overall_status

            for result in student_results:
                subjects.add(result.subject.name)
                student_data['subjects'][result.subject.name] = {
                    'test_score': result.test_score,
                    'exam_score': result.exam_score,
                    'average': result.average
                }
                
            data.append(student_data)

        context['data'] = sorted(data, key=lambda x: x['overall_average'], reverse=True)
        context['subjects'] = sorted(subjects)

        subject_data = []
        for subject_name in subjects:
            subject = Subject.objects.get(name=subject_name)
            subject_overall_average = Result.calculate_subject_overall_average(selected_class, subject)
            subject_gpa = Result.calculate_subject_gpa(selected_class, subject)
            subject_grade = Result().calculate_subject_grade(selected_class, subject)
            subject_data.append({'subject': subject_name, 'average': subject_overall_average, 'gpa': subject_gpa, 'subject_grade': subject_grade})
        context['subject_data'] = sorted(subject_data, key=lambda x: x['average'], reverse=True)

        return context


# this display the list of the classes and the user will select the class whose results is going to see in the ClassResultsView
class ClassListView(View):
    def get(self, request):
        # Retrieve all classes
        classes = StudentClass.objects.all()
        context = {
            'classes': classes
        }
        return render(request, 'result/class_list.html', context)

    def post(self, request):
        # Get the selected class ID from the POST request
        class_id = request.POST.get('class_id')
        if class_id:
            # Redirect to ClassResultsView with the selected class ID
            return redirect('class-results', class_id=class_id)
        else:
            # If no class is selected, redirect bfrom django.core.validators import MinValueValidator, MaxValueValidator
            # If no class is selected, redirect back to the class list page
            return redirect('class-list')


class SingleClassResultsView(TemplateView):
    template_name = 'result/single_class_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs.get('class_id')
        selected_class = StudentClass.objects.get(pk=class_id)
        session = AcademicSession.objects.get(current=True)
        term = AcademicTerm.objects.get(current=True)
        exam = ExamType.objects.get(current=True)

        context['class_id'] = class_id
        context['selected_class'] = selected_class

        students = Student.objects.filter(current_class=selected_class)

        data = []
        subjects = set()
        for student in students:
            student_data = {
                'student': student,
                'student_class': student.current_class,
                'subjects': {}
            }

            student_results = Result.objects.filter(
                student=student,
                session=session,
                term=term,
                exam=exam
            )

            # Calculate total marks and overall average
            total_marks = student_results.aggregate(total_marks=Sum('average'))['total_marks'] or 0
            overall_average = total_marks / len(student_results) if len(student_results) > 0 else 0
            overall_status = "PASS" if overall_average >= 25 else "FAIL"

            student_data['total'] = total_marks
            student_data['overall_average'] = overall_average
            student_data['overall_status'] = overall_status

            for result in student_results:
                subjects.add(result.subject.name)
                student_data['subjects'][result.subject.name] = {
                    'test_score': result.test_score,
                    'exam_score': result.exam_score,
                    'average': result.average
                }
                
            data.append(student_data)

        context['data'] = sorted(data, key=lambda x: x['overall_average'], reverse=True)
        context['subjects'] = sorted(subjects)

        subject_data = []
        for subject_name in subjects:
            subject = Subject.objects.get(name=subject_name)
            subject_overall_average = Result.calculate_subject_overall_average(selected_class, subject)
            subject_gpa = Result.calculate_subject_gpa(selected_class, subject)
            subject_grade = Result().calculate_subject_grade(selected_class, subject)
            subject_data.append({'subject': subject_name, 'average': subject_overall_average, 'gpa': subject_gpa, 'subject_grade': subject_grade})
        context['subject_data'] = sorted(subject_data, key=lambda x: x['average'], reverse=True)

        return context


# this display the list of the classes and the user will select the class whose results is going to see in the ClassResultsView
class SingleClassListView(View):
    def get(self, request):
        # Retrieve all classes
        classes = StudentClass.objects.all()
        context = {
            'classes': classes
        }
        return render(request, 'result/single_class_list.html', context)

    def post(self, request):
        # Get the selected class ID from the POST request
        class_id = request.POST.get('class_id')
        if class_id:
            # Redirect to ClassResultsView with the selected class ID
            return redirect('single-results', class_id=class_id)
        else:
            # If no class is selected, redirect bfrom django.core.validators import MinValueValidator, MaxValueValidator
            # If no class is selected, redirect back to the class list page
            return redirect('single-class')


# In views.py
class SingleStudentResultsView(TemplateView):
    template_name = 'result/single_student_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = kwargs.get('student_id')  # Assuming you pass the student id through URL

        # Retrieve the student
        student = get_object_or_404(Student, pk=student_id)

        # Retrieve current session, term, and exam
        current_session = AcademicSession.objects.filter(current=True).first()
        current_term = AcademicTerm.objects.filter(current=True).first()
        current_exam = ExamType.objects.filter(current=True).first()

        # Retrieve results for the specified student, session, term, and exam
        student_results = Result.objects.filter(
            student_id=student_id,
            session=current_session,
            term=current_term,
            exam=current_exam
        )

        # Pass the student's name to the template
        context['student_name'] = f"{student.firstname} {student.surname} {student.other_name}"
        context['student_class'] = student.current_class

        # Calculate total marks for each subject
        subjects = {}
        total_marks = 0
        for result in student_results:
            subject_name = result.subject.name
            if subject_name not in subjects:
                subjects[subject_name] = {
                    'test_score': result.test_score or 0,
                    'exam_score': result.exam_score or 0,
                    'average': result.average or 0,
                    'total': result.total,
                    'grade': result.calculate_grade(),  # Call calculate_grade here to ensure 'grade' attribute is set
                    'status': result.calculate_status(),
                    'comments': result.calculate_comments(),  # Calculate comments for each subject
                }
            else:
                subjects[subject_name]['test_score'] += result.test_score or 0
                subjects[subject_name]['exam_score'] += result.exam_score or 0
                subjects[subject_name]['average'] += result.average or 0
            total_marks += result.average  # Update to sum of averages

        # Pass the calculated results to the template
        context['subjects'] = subjects

        # Pass current session, term, and exam to the template
        context['current_session'] = current_session.name if current_session else None
        context['current_term'] = current_term.name if current_term else None
        context['current_exam'] = current_exam.name if current_exam else None

        # Calculate additional fields
        context['total'] = total_marks  # Update to sum of averages
        context['overall_average'] = total_marks / len(subjects) if subjects else None
        context['overall_total_marks'] = len(subjects) * 50  # Assuming 50 is the highest marks
        context['overall_grade'] = Result.calculate_overall_grade(student) if student_results else None
        total_students = Result.total_students(student.current_class.id)
        context['total_students'] = total_students
        
        # Calculate overall averages for all students in the class
        student_class = student.current_class
        all_students = Student.objects.filter(current_class=student_class)
        overall_averages = []
        for each_student in all_students:
            student_results = Result.objects.filter(
                student=each_student,
                session=current_session,
                term=current_term,
                exam=current_exam
            )
            total_marks = sum(result.average for result in student_results)
            overall_avg = total_marks / len(subjects) if subjects else None
            overall_averages.append((each_student, overall_avg))

        # Sort students based on overall average
        sorted_students = sorted(overall_averages, key=lambda x: x[1], reverse=True)

        # Find student position
        student_position = None
        for i, (student_in_list, overall_avg) in enumerate(sorted_students, start=1):
            if student == student_in_list:
                student_position = i
                break

        context['student_position'] = student_position

        # Set the grade attribute for each result
        for result in student_results:
            result.grade = result.calculate_grade()

        return context
