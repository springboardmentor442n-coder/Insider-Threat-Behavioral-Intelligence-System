from fastapi import APIRouter
from fastapi import Depends

from backend.utils.roles import require_roles

from backend.services.report_service import (
    get_available_reports,
    get_report,
    get_all_reports,
    download_report,
)

router = APIRouter()


# =============================================================================
# List Available Reports
# =============================================================================

@router.get("/list")
def list_reports(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
            "viewer",
        )
    ),
):
    return get_available_reports()


# =============================================================================
# Get All Reports
# =============================================================================

@router.get("/all")
def all_reports(
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
            "viewer",
        )
    ),
):
    return get_all_reports()


# =============================================================================
# Download Report
# =============================================================================

@router.get("/download/{report_name}")
def download(
    report_name: str,
    format: str = "csv",
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
            "viewer",
        )
    ),
):
    return download_report(report_name, export_format=format)


# =============================================================================
# Get Single Report
# =============================================================================

@router.get("/{report_name}")
def report(
    report_name: str,
    current_user=Depends(
        require_roles(
            "admin",
            "analyst",
            "viewer",
        )
    ),
):
    return get_report(report_name)
