from django.db import models
from schoolprofile.models import SchoolClass, Stream, Subject


class Student(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
    ]

    STUDENT_TYPE_CHOICES = [
        ("DAY", "Day Scholar"),
        ("BOARDING", "Boarding"),
    ]

    LEVEL_CHOICES = [
        ("NURSERY", "Nursery"),
        ("PRIMARY", "Primary"),
        ("OLEVEL", "O-Level"),
        ("ALEVEL", "A-Level"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("suspended", "Suspended"),
        ("expelled", "Expelled"),
        ("deceased", "Deceased"),
        ("unknown", "Unknown"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, default="")      # ✅ no NULL
    other_names = models.CharField(max_length=100, blank=True, default="")    # ✅ no NULL

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="active",
        help_text="Current enrollment status",
        blank=True,
        null=True,
    )

    photo = models.ImageField(
        upload_to="student_photos/",
        blank=True,
        null=True,
        # ✅ store a default file path only if that file actually exists in MEDIA storage
        # If you prefer STATIC fallback, leave default=None and handle fallback in template.
        default=None,
        help_text="Upload a student photo",
    )

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)

    admission_number = models.CharField(max_length=50, unique=True)
    admission_date = models.DateField(auto_now_add=True)
    schoolpay_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    Lin = models.CharField(max_length=50, unique=True, blank=True, null=True)

    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, null=True, blank=True)

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )

    stream = models.ForeignKey(
        Stream,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )

    student_type = models.CharField(
        max_length=10,
        choices=STUDENT_TYPE_CHOICES,
        default="DAY",
        blank=True,
        null=True,
    )

    # Uganda exam references
    uce_index_number = models.CharField(max_length=50, blank=True, default="")
    uace_index_number = models.CharField(max_length=50, blank=True, default="")

    parent_name = models.CharField(max_length=255, blank=True, default="")
    parent_contact = models.CharField(max_length=50, blank=True, default="")
    address = models.CharField(max_length=255, blank=True, default="")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.admission_number} - {self.full_name}"  # ✅ no "None"

    @property
    def full_name(self) -> str:
        # ✅ skips empty strings automatically
        parts = [self.first_name, self.other_names, self.last_name]
        return " ".join(p.strip() for p in parts if p and p.strip())


class StudentSubject(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    class_subject = models.ForeignKey(
        Subject,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="student_subjects",
    )

    is_optional = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "class_subject")

    def __str__(self):
        # NOTE: your FK is to Subject; your old code used class_subject.subject.name (likely wrong)
        # Adjust based on your Subject model fields.
        return f"{self.student.full_name} → {self.class_subject}"

class ParentGuardian(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="guardians")
    name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=50)
    relationship = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        return f"{self.name} ({self.relationship}) - {self.student.full_name}"