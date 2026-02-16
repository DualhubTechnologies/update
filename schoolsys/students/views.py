from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from students.forms import ParentGuardianForm, StudentForm,  UploadExcelForm
from django.db.models import Count, Q
from schoolprofile.models import SchoolClass, Stream
from students.models import  Student,ParentGuardian
from django.contrib import messages
from .excel import import_students_from_excel
from django.views.decorators.http import require_POST
from django_currentuser.middleware import _set_current_user
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string

from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from schoolprofile.models import SchoolProfile



app_name = "students"


def addstudent(request):
    _set_current_user(request.user)
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        print(request.POST)
        if form.is_valid():
            form.save()
            return redirect('students:studentDetails') 
        else:
            print("FORM ERRORS:", form.errors) 
    else:
        form = StudentForm()
    return render(request, 'students/addstudent.html', {'form': form})

# def studentDetails(request):
#         students = Student.objects.select_related('school_class', 'stream').all()
#         return render(request, 'students/studentlist.html', {'students': students})


def studentDetails(request):
    students = Student.objects.select_related('school_class', 'stream').order_by('-id')

    filters = {
        'school_class': request.GET.get('school_class', ''),
        'stream': request.GET.get('stream', ''),
        'section': request.GET.get('section', ''),
        'status': request.GET.get('status', '')
    }

    if filters['school_class'] and filters['school_class'] != 'all':
        students = students.filter(school_class__name=filters['school_class'])

    if filters['stream'] and filters['stream'] != 'all':
        students = students.filter(stream__name=filters['stream'])

    if filters['section'] and filters['section'] != 'all':
        students = students.filter(student_type=filters['section'])

    if filters['status'] and filters['status'] != 'all':
        students = students.filter(status=filters['status'])

    # 🔹 PAGINATION
    paginator = Paginator(students, 200)  # 10 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    school_classes = SchoolClass.objects.all()
    unique_streams = Stream.objects.values('name').distinct()

    return render(request, 'students/studentlist.html', {
        'students': page_obj,     # IMPORTANT
        'page_obj': page_obj,
        'school_classes': school_classes,
        'streams': unique_streams,
        'filters': filters,
    })

    
def student_list(request):
    qs = Student.objects.select_related('school_class', 'stream') \
                        .order_by('admission_number')

    data = []
    for s in qs:
        data.append({
            'id':               s.id,
            'admission_number': s.admission_number,
            'schoolpay_code':   s.schoolpay_code,
            'first_name':       s.first_name,
            'other_names':      s.other_names,
            'date_of_birth':    s.date_of_birth.isoformat(),
            'gender':           s.gender,
            'school_class':     s.school_class.name if s.school_class else None,
            'stream':           s.stream.name if s.stream else None,
            'enrollment_date':  s.enrollment_date.isoformat(),
            'status':           s.status,
            'section':          s.section,
            'address':          s.address,
            # revert photo to just the relative path
            'photo':            s.photo.name if s.photo else None,
        })

    return JsonResponse(data, safe=False)


def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect('students:student_profile', pk=student.pk)
    else:
        form = StudentForm(instance=student)

    return render(request, 'students/student_form.html', {
        'form': form,
        'student': student,
        'is_edit': True
    })


# Delete Student View
def delete_student(request, id):
    student = get_object_or_404(Student, id=id)
    student.delete()
    return redirect('students:studentDetails') 



 
# dashboards starthere   
 
def EnrolmentSummary(request):

    active_qs = Student.objects.filter(status='active')
    context = {
        'total_enrolment':    active_qs.count(),
        'male_count':         active_qs.filter(gender='male').count(),
        'female_count':       active_qs.filter(gender='female').count(),
        'boarding_count':     active_qs.filter(student_type='BOARDING').count(),
    }
    return render(request, 'students/Enrolmentsummary.html', context)


def class_gender_statistics_data(request):
    qs = Student.objects.filter(status='active')
    stats = (
        qs
        .values('school_class__name')
        .annotate(
            male=Count('id', filter=Q(gender='male')),
            female=Count('id', filter=Q(gender='female'))
        )
        .order_by('school_class__name')
    )
    labels        = [item['school_class__name'] for item in stats]
    male_counts   = [item['male'] for item in stats]
    female_counts = [item['female'] for item in stats]
    return JsonResponse({
        'labels':        labels,
        'male_counts':   male_counts,
        'female_counts': female_counts
    })
    
    
    # excel
def upload_students_excel_json(request):
    excel_file = request.FILES.get('excel_file')
    if not excel_file:
        return JsonResponse(
            {'success': False, 'errors': ['No file was uploaded.'], 'imported': 0, 'total': 0},
            status=400
        )
    _set_current_user(request.user)
    try:
        result = import_students_from_excel(excel_file)

        # If importer returns a tuple, unpack it.
        if isinstance(result, tuple) and len(result) == 3:
            imported, total, errors = result
            if errors:
                return JsonResponse({
                    'success': False,
                    'imported': imported,
                    'total': total,
                    'errors': errors
                }, status=200)
            return JsonResponse({
                'success': True,
                'imported': imported,
                'total': total,
                'message': f"Imported {imported} students successfully."
            }, status=200)

        # If importer returned a string (message), treat as full success:
        message = str(result)
        return JsonResponse({'success': True, 'message': message}, status=200)

    except Exception as e:
        # Catch any exception and split on “; ” to build an errors list
        msg = str(e)
        errs = msg.split('; ')
        return JsonResponse({
            'success': False,
            'errors': errs,
            'imported': 0,
            'total': 0
        }, status=200)
    


def load_streams(request):
    school_class_id = request.GET.get('school_class')
    if school_class_id:
        streams = Stream.objects.filter(school_class_id=school_class_id).order_by('name')
    else:
        streams = Stream.objects.none()
    stream_data = [{'id': s.id, 'name': s.name} for s in streams]
    return JsonResponse(stream_data, safe=False)

def get_student_info(request):
    admission_number = request.GET.get('admission_number', '').strip()
    try:
        student = Student.objects.get(admission_number__iexact=admission_number)
        return JsonResponse({
            'status': 'ok',
            'first_name': student.first_name,
            'other_names': student.other_names or '',
            'id': student.id,
            'photo_url': student.photo.url if student.photo else '',
            'status': student.status,
            'gender': student.gender
        })
    except Student.DoesNotExist:
        return JsonResponse({'status': 'not_found'})
    


def studentProfile(request, pk):
        student = get_object_or_404(Student.objects.select_related('school_class', 'stream'), pk=pk)
        return render(request, 'students/studentProfile.html', {
                    'student': student,
                    })

def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect('students:studentDetails')
    else:
        form = StudentForm(instance=student)

    return render(request, 'students/student_form.html', {'form': form, 'student': student})

@require_POST
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    return redirect('students:studentDetails')



@login_required
def student_photo_search(request):
    """
    Initial GET -> shows search form only (no students).
    After search -> shows matching students with photos.
    Search by:
      - class name (or class_id)
      - student name (first/last/other)
      - admission_number (regno)
    """
    q = (request.GET.get("q") or "").strip()
    class_id = (request.GET.get("class_id") or "").strip()

    classes = SchoolClass.objects.all().order_by("name")

    students = None  # None means: no search performed yet

    # Only run query if user actually provided something
    if q or class_id:
        students_qs = Student.objects.select_related("school_class", "stream")

        if class_id:
            students_qs = students_qs.filter(school_class_id=class_id)

        if q:
            # search by name or regno/admission_number
            students_qs = students_qs.filter(
                Q(admission_number__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(other_names__icontains=q)
            )

        students = students_qs.order_by("first_name", "last_name")[:200]  # limit to protect page

    return render(
        request,
        "students/photo_search.html",
        {
            "classes": classes,
            "students": students,         # None = show no results section
            "q": q,
            "class_id": class_id,
        },
    )


@login_required
@require_POST
def student_photo_upload(request, student_id):
    """
    AJAX endpoint: upload a new photo for a student.
    """
    student = get_object_or_404(Student, id=student_id)

    file = request.FILES.get("photo")
    if not file:
        return HttpResponseBadRequest("No photo uploaded")

    allowed = {"image/jpeg", "image/png", "image/webp"}
    if getattr(file, "content_type", "") and file.content_type not in allowed:
        return HttpResponseBadRequest("Unsupported file type")

    student.photo = file
    student.save(update_fields=["photo", "updated_at"])

    return JsonResponse({
        "ok": True,
        "student_id": student.id,
        "photo_url": student.photo.url if student.photo else "",
        "full_name": student.full_name,
        "admission_number": student.admission_number,
    })


@login_required
def parent_guardian_add(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    guardians = student.guardians.all()  # uses related_name

    if request.method == 'POST':
        form = ParentGuardianForm(request.POST)
        if form.is_valid():
            guardian = form.save(commit=False)
            guardian.student = student
            guardian.save()
            messages.success(request, "Parent/Guardian added successfully.")
            return redirect('students:parent_guardians', student_id=student.id)
    else:
        form = ParentGuardianForm()

    return render(request, 'students/parent_guardians.html', {
        'student': student,
        'guardians': guardians,
        'form': form,
    })

@login_required
def parent_guardian_edit(request, guardian_id):
    guardian = get_object_or_404(ParentGuardian, pk=guardian_id)
    student = guardian.student

    if request.method == 'POST':
        form = ParentGuardianForm(request.POST, instance=guardian)
        if form.is_valid():
            form.save()
            messages.success(request, "Parent/Guardian updated successfully.")
            return redirect(
                'students:parent_guardians',
                student_id=student.id
            )
    else:
        form = ParentGuardianForm(instance=guardian)

    return render(request, 'students/parent_guardian_edit.html', {
        'form': form,
        'guardian': guardian,
        'student': student,
    })

@login_required
def parent_guardian_delete(request, guardian_id):
    guardian = get_object_or_404(ParentGuardian, pk=guardian_id)
    student_id = guardian.student.id

    guardian.delete()
    messages.success(request, "Parent / Guardian deleted successfully.")

    return redirect('students:parent_guardians', student_id=student_id)


def generate_admission_letter(request, student_id):
    student = Student.objects.get(id=student_id)

    school = SchoolProfile.objects.first()  # singleton pattern

    template = get_template("letters/admission_letter.html")
    html = template.render({
        "student": student,
        "school": school,
    })

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = (
        f'attachment; filename="Admission_{student.full_name}.pdf"'
    )

    pisa.CreatePDF(html, dest=response)

    return response

@login_required
def list_admissions(request):
    return render(request, 'students/listadmissions.html')