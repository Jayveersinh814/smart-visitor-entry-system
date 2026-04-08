from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
import pandas as pd
from accounts.permissions import is_org_admin, role_required
from .forms import ApprovalForm, ScanForm, VisitorPassForm
from .models import ScanEvent, VisitorPass, Watchlist
from .mail import send_visitor_pass_email
from .utils import create_qr_token, generate_qr_image, refresh_expired_passes, validate_qr_token


@login_required
def landing(request):
    return render(request, "visitors/landing.html")


@login_required
def dashboard(request):
    refresh_expired_passes()
    passes = VisitorPass.objects.select_related("host", "check_in_gate")
    if getattr(request.user.profile, "role", "") == "host" and not is_org_admin(request.user):
        passes = passes.filter(host=request.user)

    today = timezone.localdate()
    context = {
        "total_today": passes.filter(created_at__date=today).count(),
        "inside_count": sum(1 for p in passes if p.is_inside),
        "pending_count": passes.filter(status="pending").count(),
        "top_hosts": VisitorPass.objects.values("host__username").annotate(total=Count("id")).order_by("-total")[:5],
        "recent_passes": passes[:10],
    }
    return render(request, "visitors/dashboard.html", context)


@login_required
@role_required("admin", "host")
def register_visitor(request):
    if request.method == "POST":
        form = VisitorPassForm(request.POST, request.FILES)
        if form.is_valid():
            visitor_pass = form.save(commit=False)
            visitor_pass.created_by = request.user
            if request.user.profile.role == "host" and not is_org_admin(request.user):
                visitor_pass.host = request.user
            visitor_pass.save()
            messages.success(request, "Visitor registration submitted.")
            return redirect("pass_detail", pk=visitor_pass.pk)
    else:
        form = VisitorPassForm()
    return render(request, "visitors/register.html", {"form": form})


@login_required
def pass_detail(request, pk):
    visitor_pass = get_object_or_404(VisitorPass.objects.select_related("host"), pk=pk)
    if (
        request.user.profile.role == "host"
        and not is_org_admin(request.user)
        and visitor_pass.host_id != request.user.id
    ):
        return HttpResponse("Access denied", status=403)
    return render(request, "visitors/pass_detail.html", {"pass": visitor_pass})


@login_required
@role_required("admin", "host")
def approval_queue(request):
    qs = VisitorPass.objects.filter(status="pending").select_related("host")
    if request.user.profile.role == "host" and not is_org_admin(request.user):
        qs = qs.filter(host=request.user)
    return render(request, "visitors/approval_queue.html", {"passes": qs})


@login_required
@role_required("admin", "host")
def review_pass(request, pk):
    visitor_pass = get_object_or_404(VisitorPass, pk=pk, status="pending")
    if (
        request.user.profile.role == "host"
        and not is_org_admin(request.user)
        and visitor_pass.host_id != request.user.id
    ):
        return HttpResponse("Access denied", status=403)
    if request.method == "POST":
        form = ApprovalForm(request.POST)
        if form.is_valid():
            decision = form.cleaned_data["decision"]
            visitor_pass.approval_note = form.cleaned_data["note"]
            visitor_pass.approved_by = request.user
            visitor_pass.approved_at = timezone.now()
            if decision == "approved":
                visitor_pass.status = "approved"
                visitor_pass.qr_token = create_qr_token(visitor_pass)
                generate_qr_image(visitor_pass)
            else:
                visitor_pass.status = "rejected"
            visitor_pass.save()
            if decision == "approved":
                sent, err = send_visitor_pass_email(visitor_pass)
                if sent:
                    messages.success(
                        request,
                        "Pass approved. QR and invite email sent to the visitor.",
                    )
                elif err == "no_email":
                    messages.warning(
                        request,
                        "Pass approved, but visitor has no email — QR was not emailed.",
                    )
                else:
                    messages.warning(
                        request,
                        f"Pass approved, but email could not be sent: {err}",
                    )
            else:
                messages.success(request, "Pass rejected.")
            return redirect("pass_detail", pk=visitor_pass.pk)
    else:
        form = ApprovalForm()
    return render(request, "visitors/review_pass.html", {"form": form, "pass": visitor_pass})


@login_required
@role_required("admin", "guard")
def scan_qr(request):
    result = None
    if request.method == "POST":
        form = ScanForm(request.POST)
        if form.is_valid():
            gate = form.cleaned_data["gate"]
            action = form.cleaned_data["action"]
            pass_id, err = validate_qr_token(form.cleaned_data["qr_token"].strip())
            if err:
                result = {"status": "error", "message": err}
            else:
                visitor_pass = get_object_or_404(VisitorPass, pk=pass_id)
                watch_match = Watchlist.objects.filter(
                    is_active=True, phone_number=visitor_pass.phone_number
                ).exists()
                if visitor_pass.is_expired:
                    visitor_pass.status = "expired"
                    visitor_pass.save(update_fields=["status"])
                    result = {"status": "error", "message": "Pass expired"}
                elif visitor_pass.status not in ["approved", "checked_in"]:
                    result = {"status": "error", "message": f"Pass not valid ({visitor_pass.status})"}
                elif action == "entry":
                    if visitor_pass.is_used and not visitor_pass.is_multi_entry:
                        result = {"status": "error", "message": "Pass already used"}
                    else:
                        visitor_pass.is_used = True
                        visitor_pass.status = "checked_in"
                        visitor_pass.check_in_at = timezone.now()
                        visitor_pass.check_in_gate = gate
                        visitor_pass.save()
                        result = {"status": "ok", "message": "Entry allowed", "watch_alert": watch_match}
                else:
                    visitor_pass.status = "checked_out"
                    visitor_pass.check_out_at = timezone.now()
                    visitor_pass.check_out_gate = gate
                    visitor_pass.save()
                    result = {"status": "ok", "message": "Exit recorded", "watch_alert": watch_match}

                if pass_id:
                    ScanEvent.objects.create(
                        visitor_pass=visitor_pass,
                        gate=gate,
                        scanned_by=request.user,
                        action=action,
                        result=result["message"],
                    )
    else:
        form = ScanForm()
    return render(request, "visitors/scan.html", {"form": form, "result": result})


@login_required
@role_required("admin", "guard", "host")
def visitor_logs(request):
    qs = VisitorPass.objects.select_related("host").all()
    if getattr(request.user.profile, "role", "") == "host" and not is_org_admin(request.user):
        qs = qs.filter(host=request.user)
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    host_id = request.GET.get("host")
    visitor_type = request.GET.get("visitor_type")
    if date_from:
        qs = qs.filter(valid_from__date__gte=date_from)
    if date_to:
        qs = qs.filter(valid_until__date__lte=date_to)
    if host_id:
        qs = qs.filter(host_id=host_id)
    if visitor_type:
        qs = qs.filter(visitor_type=visitor_type)
    return render(request, "visitors/logs.html", {"passes": qs[:200]})


@login_required
@role_required("admin")
def export_logs_csv(request):
    data = VisitorPass.objects.values(
        "id",
        "visitor_name",
        "phone_number",
        "email",
        "purpose",
        "host__username",
        "reference_by",
        "visitor_type",
        "status",
        "valid_from",
        "valid_until",
        "check_in_at",
        "check_out_at",
    )
    df = pd.DataFrame(list(data))
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=visitor_logs.csv"
    response.write(df.to_csv(index=False))
    return response
