"""
CERT LDAP Seeding Script (Disabled / Deprecated)
=================================================
LDAP employee seeding has been removed as per system policy.
Use `python scripts/seed_synthetic_300.py` to seed synthetic employee cohorts.
"""
import sys

def seed_ldap_employees():
    print("ℹ️ LDAP employee data feeding is disabled.")
    print("👉 Use `python scripts/seed_synthetic_300.py` to generate 300 synthetic employees with mixed risk criteria.")

if __name__ == "__main__":
    seed_ldap_employees()
