from fastapi import HTTPException, status
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.api.v1.dependencies import CurrentUser


def get_department_from_role(role_name: str) -> str | None:
    if role_name == "super_admin":
        return None
    if role_name.startswith("author_"):
        return role_name.split("author_")[-1]
    return None


def ensure_same_department_or_superadmin(current_user: "CurrentUser", target_role_name: str | None) -> None:
    if current_user.role_name == "super_admin":
        return

    current_department = get_department_from_role(current_user.role_name)
    target_department = get_department_from_role(target_role_name or "")

    if not current_department or not target_department or current_department != target_department:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-department access is not allowed"
        )
