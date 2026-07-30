"""Reports & Export API. Spec Module 12.

One endpoint pattern: GET /api/reports/{slug}.{fmt} streams the report as a file
download. slug is one of the five report types; fmt is pdf or xlsx. The
Content-Disposition header carries a filename so the browser saves it with a
sensible name rather than showing bytes.

ACCESS. Reports are generated from data an operator can already see in the
console, so any authenticated operator may generate the operational ones. The
compliance report is the exception - it is the audit trail, and the audit views
are administrator-only, so the compliance report is too. That single carve-out
keeps the report permissions consistent with the views they summarise.
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import CurrentUser, require_roles
from backend.app.models import UserRole
from backend.app.reports_data import REPORTS
from backend.app.reporting import render_pdf, render_xlsx

router = APIRouter(prefix="/api/reports", tags=["reports"])

# Reports that summarise administrator-only views inherit that restriction.
_ADMIN_ONLY = {"compliance"}

_MEDIA = {
    "pdf": "application/pdf",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


@router.get("/catalog", summary="The available reports")
def catalog(current_user: CurrentUser):
    """What reports exist, so the UI can build its menu without hard-coding it."""
    labels = {
        "insider-threat": "Insider Threat Report",
        "behavioral-analytics": "Behavioral Analytics Report",
        "investigation": "Investigation Report",
        "compliance": "Compliance Report",
        "risk-assessment": "Risk Assessment Report",
    }
    is_admin = current_user.role == UserRole.ADMINISTRATOR
    out = []
    for slug, (_fn, needs_user) in REPORTS.items():
        if slug in _ADMIN_ONLY and not is_admin:
            continue
        out.append({
            "slug": slug,
            "label": labels.get(slug, slug),
            "needs_user_id": needs_user,
            "formats": ["pdf", "xlsx"],
        })
    return {"reports": out}


@router.get("/{slug}.{fmt}", summary="Generate and download a report")
def generate_report(
    slug: str,
    fmt: str,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[str | None, Query(description="Required for the investigation report")] = None,
):
    if slug not in REPORTS:
        raise HTTPException(404, f"Unknown report '{slug}'.")
    if fmt not in _MEDIA:
        raise HTTPException(404, f"Unknown format '{fmt}'. Use pdf or xlsx.")

    # admin-only carve-out for the compliance (audit) report
    if slug in _ADMIN_ONLY and current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(403, "This report is available to administrators only.")

    fn, needs_user = REPORTS[slug]
    if needs_user:
        if not user_id:
            raise HTTPException(422, "This report requires a user_id query parameter.")
        doc = fn(db, user_id=user_id)
        if doc is None:
            raise HTTPException(404, f"No such employee '{user_id}'.")
    else:
        doc = fn(db)

    # stamp who generated it, for the report header
    doc.generated_by = current_user.email

    data = render_pdf(doc) if fmt == "pdf" else render_xlsx(doc)

    stem = slug if not (needs_user and user_id) else f"{slug}_{user_id}"
    filename = f"{stem}_{doc.generated_at:%Y%m%d}.{fmt}"
    return Response(
        content=data,
        media_type=_MEDIA[fmt],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
