from django.shortcuts import render

def dashboard(request):
    return render(request, 'partials/dashboard.html')
def students_list(request):
    return render(request, 'partials/students_list.html')
def student_create(request):
    return render(request, 'partials/student_form.html')
def fees(request):
    return render(request, 'partials/student_form.html')
def student_profile(request):
    return render(request, 'partials/student_profile.html')

