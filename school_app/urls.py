from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

def admin_redirect(request):
    return redirect(reverse('admin:index'))

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("apps.corecode.urls")),
    path("student/", include("apps.students.urls")),
    path("staff/", include("apps.staffs.urls")),
    path("finance/", include("apps.finance.urls")),
    path("expenditures/", include("expenditures.urls")),
    path("event/", include("event.urls")),
    path("result/", include("apps.result.urls")),
    path("updations/", include("updations.urls")),
    path("school_properties/", include("school_properties.urls")),
    # Add a URL pattern for redirecting to the admin site
    path('goto-admin/', admin_redirect, name='goto-admin'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

