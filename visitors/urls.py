from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("register/", views.register_visitor, name="register_visitor"),
    path("pass/<int:pk>/", views.pass_detail, name="pass_detail"),
    path("approvals/", views.approval_queue, name="approval_queue"),
    path("review/<int:pk>/", views.review_pass, name="review_pass"),
    path("scan/", views.scan_qr, name="scan_qr"),
    path("logs/", views.visitor_logs, name="visitor_logs"),
    path("logs/export/csv/", views.export_logs_csv, name="export_logs_csv"),
]
