from app.crud.user import delete_user, get_user_by_email
from app.db.session import SessionLocal


def main() -> None:
    email = input("Email of the disposable test user to delete: ").strip()
    if not email:
        raise ValueError("Email is required")

    with SessionLocal() as db:
        user = get_user_by_email(db, email)
        if user is None:
            print(f"No user found for {email!r}; nothing was deleted.")
            return

        confirmation = input(
            f"Delete {user.email!r} and its assistant sessions? Type 'delete' to confirm: "
        )
        if confirmation != "delete":
            print("Deletion cancelled.")
            return

        delete_user(db, user)
        print(f"Deleted test user {email!r} and its assistant sessions.")


if __name__ == "__main__":
    main()
