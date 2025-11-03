"""Utility to create an admin user in the Clipador backend."""

import asyncio

from sqlalchemy import select

from clipador_backend.db import session_scope
from clipador_backend.models import UserAccount
from clipador_backend.security.auth import hash_password


async def create_admin(username: str, password: str) -> None:
    async with session_scope() as session:
        result = await session.execute(select(UserAccount).where(UserAccount.username == username))
        existing = result.scalar_one_or_none()
        if existing:
            print("User already exists.")
            return
        user = UserAccount(username=username, hashed_password=hash_password(password))
        session.add(user)
        await session.flush()
        print(f"Created admin user '{username}'.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create admin user")
    parser.add_argument("username")
    parser.add_argument("password")
    args = parser.parse_args()

    asyncio.run(create_admin(args.username, args.password))
