from .models import AcademicSession, AcademicTerm, ExamType, SiteConfig


def site_defaults(request):
    current_session = AcademicSession.objects.get(current=True)
    current_term = AcademicTerm.objects.get(current=True)
    current_exam = ExamType.objects.get(current=True)
    vals = SiteConfig.objects.all()
    contexts = {
        "current_session": current_session.name,
        "current_term": current_term.name,
        "current_exam": current_exam.name,
    }
    for val in vals:
        contexts[val.key] = val.value

    return contexts
