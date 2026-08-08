"""Employee identity directory, sourced from LDAP snapshots."""

from __future__ import annotations

import glob
from functools import lru_cache

import pandas as pd

from config import Config


@lru_cache(maxsize=1)
def get_directory() -> dict[str, dict]:
    """Map user id -> {name, role, department, team}.

    Prefers the generator's directory dump; otherwise falls back to the most
    recent monthly LDAP snapshot, which is what a real r4.2 drop provides.
    """
    direct = Config.RAW_DIR / "employee_directory.csv"
    if direct.exists():
        df = pd.read_csv(direct)
        return df.set_index("user").to_dict(orient="index")

    ldap_files = sorted(glob.glob(str(Config.RAW_DIR / "LDAP" / "*.csv")))
    if not ldap_files:
        return {}

    df = pd.read_csv(ldap_files[-1])
    rename = {"user_id": "user", "employee_name": "name"}
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    keep = [c for c in ["user", "name", "role", "department", "team"] if c in df.columns]
    if "user" not in keep:
        return {}
    return df[keep].drop_duplicates(subset="user").set_index("user").to_dict(orient="index")


def clear_cache():
    get_directory.cache_clear()
