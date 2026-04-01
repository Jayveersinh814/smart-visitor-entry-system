from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Gate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class VisitorPass(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHECKED_IN = "checked_in"
    STATUS_CHECKED_OUT = "checked_out"
    STATUS_EXPIRED = "expired"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_CHECKED_IN, "Checked-In"),
        (STATUS_CHECKED_OUT, "Checked-Out"),
        (STATUS_EXPIRED, "Expired"),
    ]

    visitor_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    id_proof = models.FileField(upload_to="id_proofs/", blank=True, null=True)
    purpose = models.TextField()
    host = models.ForeignKey(User, on_delete=models.PROTECT, related_name="hosted_visits")
    reference_by = models.CharField(max_length=200, blank=True)
    visitor_type = models.CharField(max_length=100, blank=True, default="General")
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_multi_entry = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    approval_note = models.CharField(max_length=255, blank=True)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_visits"
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    qr_token = models.TextField(blank=True)
    qr_image = models.ImageField(upload_to="qr_codes/", blank=True, null=True)
    is_used = models.BooleanField(default=False)
    check_in_at = models.DateTimeField(null=True, blank=True)
    check_out_at = models.DateTimeField(null=True, blank=True)
    check_in_gate = models.ForeignKey(
        Gate, on_delete=models.SET_NULL, null=True, blank=True, related_name="checkin_passes"
    )
    check_out_gate = models.ForeignKey(
        Gate, on_delete=models.SET_NULL, null=True, blank=True, related_name="checkout_passes"
    )

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_visits")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.visitor_name} -> {self.host.get_full_name() or self.host.username}"

    @property
    def is_expired(self):
        return timezone.now() > self.valid_until

    @property
    def is_inside(self):
        return bool(self.check_in_at and not self.check_out_at)


class ScanEvent(models.Model):
    ACTION_ENTRY = "entry"
    ACTION_EXIT = "exit"
    ACTION_CHOICES = [
        (ACTION_ENTRY, "Entry"),
        (ACTION_EXIT, "Exit"),
    ]

    visitor_pass = models.ForeignKey(VisitorPass, on_delete=models.CASCADE, related_name="scan_events")
    gate = models.ForeignKey(Gate, on_delete=models.PROTECT)
    scanned_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="scans")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    result = models.CharField(max_length=120)
    scanned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scanned_at"]

    def __str__(self):
        return f"{self.visitor_pass_id} {self.action} {self.result}"


class Watchlist(models.Model):
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    reason = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# Create your models here.
