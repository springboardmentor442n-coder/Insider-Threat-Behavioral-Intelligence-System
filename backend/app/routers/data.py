"""Employee and dataset endpoints.

Note the RBAC split here, because it is the point of the whole exercise:

  /api/data/employees         - any operator. The roster is not sensitive.
  /api/data/employees/{id}    - MANAGER or ADMIN only. Returns the ground-truth
                                insider flag. An analyst who can read the answer
                                key is not investigating, they are cheating - and
                                any evaluation of "how fast do analysts find
                                insiders" becomes meaningless.
  /api/data/stats             - any operator. Row counts, no personal data.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.dependencies import (
    CAN_VIEW_GROUND_TRUTH,
    CurrentUser,
    require_roles,
)
from backend.app.ingestion import get_counts
from backend.app.models import Employee
from backend.app.schemas import EmployeeDetailResponse, EmployeeResponse

router = APIRouter(prefix="/api/data", tags=["data"])


@router.get(
    "/employees",
    response_model=list[EmployeeResponse],
    summary="List monitored employees",
)
def list_employees(
    current_user: CurrentUser,  # authentication required; any role
    db: Annotated[Session, Depends(get_db)],
    department: str | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Employee]:
    """The monitored employee roster, paginated.

    Pagination is capped at 500 and not optional. An endpoint that will happily
    return every row in a table is a denial-of-service waiting to happen the
    moment the table grows.
    """
    stmt = select(Employee).order_by(Employee.user_id)
    if department:
        stmt = stmt.where(Employee.department == department)
    stmt = stmt.limit(limit).offset(offset)
    return list(db.scalars(stmt).all())


@router.get(
    "/employees/{user_id}",
    response_model=EmployeeDetailResponse,
    dependencies=[Depends(require_roles(*CAN_VIEW_GROUND_TRUTH))],
    summary="Employee detail, including ground-truth labels (manager/admin only)",
)
def get_employee(
    user_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> Employee:
    """Full employee record INCLUDING the insider ground-truth flag.

    Restricted to Security Managers and Administrators - see the module
    docstring. This is enforced server-side by the `dependencies=[...]` above,
    which runs BEFORE this function body. Hiding the route in the UI would not
    be an access control; this is.
    """
    employee = db.get(Employee, user_id)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No employee with user_id '{user_id}'.",
        )
    return employee


@router.get("/stats", summary="Ingested dataset row counts")
def dataset_stats(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, int]:
    """Row counts per ingested table.

    The quickest way to confirm ingestion actually worked. `employees` should be
    1000 and `insiders` should be 70 for a correct r4.2 load - if those numbers
    are off, something went wrong and every downstream metric is suspect.
    """
    return get_counts(db)