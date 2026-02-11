from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Count, Q
from calendarapp.models import SchoolTerm
from schoolprofile.models import SchoolClass
from students.models import ParentGuardian, Student
from teachers.models import StaffProfile
from django.contrib.auth.decorators import login_required

def get_current_term():
    today = timezone.now().date()
    return SchoolTerm.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    ).select_related("academic_year").first()


def get_previous_term(current_term):
    return SchoolTerm.objects.filter(
        academic_year=current_term.academic_year,
        end_date__lt=current_term.start_date
    ).order_by("-end_date").first()

    

# Create your views here.
@login_required
def user_dashboard(request):
    current_term = get_current_term()
    previous_term = get_previous_term(current_term) if current_term else None

    # ---- Students ----
    total_students = Student.objects.count()

    current_term_students = Student.objects.filter(
        admission_date__range=(
            current_term.start_date,
            current_term.end_date
        )
    ).count() if current_term else 0

    previous_term_students = Student.objects.filter(
        admission_date__range=(
            previous_term.start_date,
            previous_term.end_date
        )
    ).count() if previous_term else 0

    # Growth %
    if previous_term_students > 0:
        student_growth = round(
            ((current_term_students - previous_term_students)
             / previous_term_students) * 100,
            1
        )
    else:
        student_growth = 0

    # ---- Staff & Parents ----
    total_teachers = StaffProfile.objects.count()
    total_parents = ParentGuardian.objects.count()

    context = {
        "total_students": total_students,
        "student_growth": student_growth,
        "total_teachers": total_teachers,
        "total_parents": total_parents,
        "current_term": current_term,
    }

    return render(request, "dashboards/dashboard.html", context)


def students_per_class_data(request):
    classes = (
    SchoolClass.objects
    .annotate(student_count=Count("students", distinct=True))
    .order_by("name")
    )

    labels = [c.name for c in classes]
    data = [c.student_count for c in classes]

    return JsonResponse({
        "labels": labels,
        "data": data
    })




def students_gender_data(request):
    gender_counts = (
        Student.objects
        .filter(is_active=True)
        .values("gender")
        .annotate(total=Count("id"))
    )

    male = 0
    female = 0

    for g in gender_counts:
        if g["gender"] == "M":
            male = g["total"]
        elif g["gender"] == "F":
            female = g["total"]

    return JsonResponse({
        "labels": ["Male", "Female"],
        "data": [male, female]
    })