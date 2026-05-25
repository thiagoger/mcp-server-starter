"""Self-contained synthetic-data generator with a referential-integrity check.

Kept dependency-free and in a single module so the MCP server stays easy to
read and run. (A fuller version lives in the synthetic-data-forge project.)
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

_INDUSTRIES = ("Construction", "Healthcare", "Manufacturing", "Professional Services",
               "Retail", "Logistics", "Technology", "Hospitality")
_FIRST = ("Ana", "Bruno", "Carla", "Diego", "Elena", "Felipe", "Grace", "Hugo",
          "Iris", "Joao", "Karen", "Lucas", "Maya", "Noah", "Olivia", "Pedro")
_LAST = ("Silva", "Costa", "Nguyen", "Patel", "Garcia", "Rossi", "Khan", "Mueller",
         "Santos", "Oliveira", "Tanaka", "Lopez", "Novak", "Reis")
_PLANS = (("Starter", 49.0), ("Growth", 199.0), ("Scale", 599.0), ("Enterprise", 1999.0))
_FOREIGN_KEYS = {
    ("users", "company_id"): "companies",
    ("subscriptions", "company_id"): "companies",
    ("subscriptions", "owner_user_id"): "users",
    ("invoices", "company_id"): "companies",
    ("invoices", "subscription_id"): "subscriptions",
    ("invoice_line_items", "invoice_id"): "invoices",
}


@dataclass
class DatasetSpec:
    companies: int = 8
    users_per_company: tuple[int, int] = (3, 25)
    months_of_history: int = 18
    invoice_paid_rate: float = 0.82
    seed: int = 42
    start_date: date = field(default_factory=lambda: date(2024, 1, 1))


@dataclass
class IntegrityReport:
    row_counts: dict[str, int] = field(default_factory=dict)
    violations: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations


def generate(spec: DatasetSpec) -> dict[str, list[dict[str, Any]]]:
    rng = random.Random(spec.seed)
    companies, users, subs, invoices, items = [], [], [], [], []
    uid = sid = iid = lid = 1

    for cid in range(1, spec.companies + 1):
        industry = rng.choice(_INDUSTRIES)
        companies.append({"id": cid, "name": f"{rng.choice(_LAST)} {industry.split()[0]} Co.",
                          "industry": industry, "country": rng.choice(("US", "BR", "CA", "UK", "DE"))})
        company_users = []
        lo, hi = spec.users_per_company
        for _ in range(rng.randint(lo, hi)):
            users.append({"id": uid, "company_id": cid, "name": f"{rng.choice(_FIRST)} {rng.choice(_LAST)}",
                         "role": rng.choice(("admin", "member", "viewer")), "is_active": rng.random() > 0.1})
            company_users.append(uid)
            uid += 1
        plan, price = rng.choice(_PLANS)
        subs.append({"id": sid, "company_id": cid, "owner_user_id": rng.choice(company_users),
                    "plan": plan, "monthly_price": price, "status": "active"})
        for m in range(spec.months_of_history):
            issued = spec.start_date + timedelta(days=30 * m)
            paid = rng.random() < spec.invoice_paid_rate
            total = 0.0
            for _ in range(rng.randint(1, 3)):
                qty = rng.randint(1, 5)
                unit = round(price * rng.uniform(0.2, 1.0), 2)
                amount = round(unit * qty, 2)
                total += amount
                items.append({"id": lid, "invoice_id": iid, "quantity": qty,
                             "unit_price": unit, "amount": amount})
                lid += 1
            invoices.append({"id": iid, "company_id": cid, "subscription_id": sid,
                            "issued_date": issued.isoformat(), "total": round(total, 2),
                            "status": "paid" if paid else "open"})
            iid += 1
        sid += 1

    return {"companies": companies, "users": users, "subscriptions": subs,
            "invoices": invoices, "invoice_line_items": items}


def validate_integrity(data: dict[str, list[dict[str, Any]]]) -> IntegrityReport:
    report = IntegrityReport(row_counts={t: len(r) for t, r in data.items()})
    id_sets = {t: {row["id"] for row in rows} for t, rows in data.items()}
    for (child, col), parent in _FOREIGN_KEYS.items():
        parents = id_sets.get(parent, set())
        for row in data.get(child, []):
            val = row.get(col)
            if val is not None and val not in parents:
                report.violations.append(f"{child}.{col}={val} -> missing {parent}.id")
    return report
