"""
Promote a user to admin (role=admin) so they can use the Admin resource-management API.

Usage:
    venv/Scripts/python.exe -m scripts.make_admin someone@example.com
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.db.session import SessionLocal  # noqa: E402
from app.models.enums import UserRole  # noqa: E402
from app.models.user import User  # noqa: E402


def main(email: str) -> None:
    db = SessionLocal()
    try:
        user = db.scalars(select(User).where(User.email == email)).first()
        if user is None:
            print(f"No user found with email {email!r}.")
            return
        user.role = UserRole.ADMIN
        db.commit()
        print(f"{email} is now an admin.")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.make_admin <email>")
        sys.exit(1)
    main(sys.argv[1])
