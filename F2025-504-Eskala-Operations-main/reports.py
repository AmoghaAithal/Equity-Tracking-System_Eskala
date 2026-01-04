# backend/reports.py
import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify

bp = Blueprint("reports", __name__)

# --- Load environment variables ---
# Try both project root .env and backend/.env so it works in clones too
BASE_DIR = Path(__file__).resolve().parent  # backend/
load_dotenv(BASE_DIR.parent / ".env")       # ../.env
load_dotenv(BASE_DIR / ".env")              # ./backend/.env (if present)

# ---- Canonical proposal states (always show these, even if count = 0) ----
PROPOSAL_STATES = (
    "Accepted",
    "Rejected",
    "Executed",
    "Presented",
    "To Pitch",
)

# ---- DB helpers ----
def _db_conn():
    """
    Open a MySQL connection and pin the session charset/collation so that
    Python string literals compare safely to view columns that use utf8mb4.
    """

    # Build connection args from environment
    conn_args = {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "user_management"),
        "autocommit": True,
        "charset": "utf8mb4",     # client <-> server bytes
        "use_unicode": True,
        "use_pure": True,
    }

    # Support either TCP or Unix socket based on env
    db_socket = os.getenv("DB_SOCKET")
    if db_socket:
        conn_args["unix_socket"] = db_socket
    else:
        conn_args["port"] = int(os.getenv("DB_PORT", "3306"))

    cn = mysql.connector.connect(**conn_args)

    # Pin session collation consistently (match DB: utf8mb4_general_ci)
    cur = cn.cursor()
    cur.execute("SET NAMES utf8mb4 COLLATE utf8mb4_general_ci")
    cur.execute("SET collation_connection = utf8mb4_general_ci")
    # These are belt-and-suspenders; harmless if already utf8mb4
    cur.execute("SET character_set_client = utf8mb4")
    cur.execute("SET character_set_connection = utf8mb4")
    cur.execute("SET character_set_results = utf8mb4")
    cur.close()
    return cn


def _rows(sql, params=None):
    cn = _db_conn()
    try:
        cur = cn.cursor(dictionary=True)
        cur.execute(sql, params or {})
        return cur.fetchall()
    finally:
        cn.close()


# Validate source quickly
def _source():
    s = request.args.get("source", "MATCHING").upper()
    return "PROFIT" if s == "PROFIT" else "MATCHING"

# ---- Endpoints ----

@bp.get("/api/reports/summary")
def summary():
    """Total proposals + per-state counts (for header widgets / quick stats)."""
    src = _source()

    total_sql = """
        SELECT COUNT(*) AS total
        FROM vw_equity_pipeline_norm
        WHERE source COLLATE utf8mb4_general_ci = %(src)s
    """
    total = _rows(total_sql, {"src": src})[0]["total"]

    # Get whatever states actually appear in data…
    breakdown_sql = """
        SELECT proposal_state AS label, COUNT(*) AS value
        FROM vw_equity_pipeline_norm
        WHERE source COLLATE utf8mb4_general_ci = %(src)s
          AND proposal_state IN ('Accepted','Rejected','Executed','Presented','To Pitch')
        GROUP BY proposal_state
    """
    rows = _rows(breakdown_sql, {"src": src})

    # …then map to dict and fill in missing ones with 0
    counts = {r["label"]: int(r["value"]) for r in rows if r["label"]}

    breakdown = [
        {"label": st, "value": counts.get(st, 0)}
        for st in PROPOSAL_STATES
    ]

    return jsonify({"source": src, "total": total, "breakdown": breakdown})


@bp.get("/api/reports/proposal-state")
def proposal_state():
    """Counts by proposal state (line chart)."""
    src = _source()
    sql = """
        SELECT proposal_state AS label, COUNT(*) AS value
        FROM vw_equity_pipeline_norm
        WHERE source COLLATE utf8mb4_general_ci = %(src)s
          AND proposal_state IN ('Accepted','Rejected','Executed','Presented','To Pitch')
        GROUP BY proposal_state
    """
    rows = _rows(sql, {"src": src})

    # Build lookup dict from DB (only the states that exist)
    counts = {r["label"]: int(r["value"]) for r in rows if r["label"]}

    # Always return all 5 canonical states in fixed order
    labels = list(PROPOSAL_STATES)
    data = [counts.get(st, 0) for st in PROPOSAL_STATES]

    return jsonify({"source": src, "labels": labels, "data": data})


@bp.get("/api/reports/geography")
def geography():
    """Geographic poll by State (line chart)."""
    src = _source()

    # Show ALL states that exist anywhere in the view,
    # with counts for the selected source (0 if none).
    sql = """
        WITH all_states AS (
            SELECT DISTINCT state
            FROM vw_equity_pipeline_norm
            WHERE state IS NOT NULL AND state <> ''
        ),
        counts AS (
            SELECT state, COUNT(*) AS value
            FROM vw_equity_pipeline_norm
            WHERE source COLLATE utf8mb4_general_ci = %(src)s
              AND state IS NOT NULL AND state <> ''
            GROUP BY state
        )
        SELECT a.state AS label, COALESCE(c.value, 0) AS value
        FROM all_states a
        LEFT JOIN counts c ON c.state = a.state
        ORDER BY value DESC, label ASC
    """
    rows = _rows(sql, {"src": src})
    labels = [r["label"] for r in rows]
    data = [int(r["value"]) for r in rows]
    return jsonify({"source": src, "labels": labels, "data": data})


@bp.get("/api/reports/categories")
def categories():
    """Influence Zone / Business Category (bar chart)."""
    src = _source()

    # Show ALL categories that exist anywhere in the view,
    # with counts for the selected source (0 if none).
    sql = """
        WITH all_categories AS (
            SELECT DISTINCT business_category
            FROM vw_equity_pipeline_norm
            WHERE business_category IS NOT NULL
              AND business_category <> ''
        ),
        counts AS (
            SELECT business_category, COUNT(*) AS value
            FROM vw_equity_pipeline_norm
            WHERE source COLLATE utf8mb4_general_ci = %(src)s
              AND business_category IS NOT NULL
              AND business_category <> ''
            GROUP BY business_category
        )
        SELECT a.business_category AS label, COALESCE(c.value, 0) AS value
        FROM all_categories a
        LEFT JOIN counts c ON c.business_category = a.business_category
        ORDER BY value DESC, label ASC
    """
    rows = _rows(sql, {"src": src})
    labels = [r["label"] for r in rows]
    data = [int(r["value"]) for r in rows]
    return jsonify({"source": src, "labels": labels, "data": data})


@bp.get("/api/reports/disbursement")
def disbursement():
    """Monthly Tentative Disbursement (bar chart)."""
    src = _source()
    sql = """
        SELECT 'January'   AS month, COALESCE(SUM(january_l),0)   AS amount
        FROM vw_equity_pipeline_norm
        WHERE source COLLATE utf8mb4_general_ci = %(src)s UNION ALL

        SELECT 'February', COALESCE(SUM(february_l),0)
        FROM vw_equity_pipeline_norm
        WHERE source COLLATE utf8mb4_general_ci = %(src)s UNION ALL

        SELECT 'March',    COALESCE(SUM(march_l),0)
        FROM vw_equity_pipeline_norm
        WHERE source COLLATE utf8mb4_general_ci = %(src)s UNION ALL

        SELECT 'April',    COALESCE(SUM(april_l),0)
        FROM vw_equity_pipeline_norm
        WHERE source COLLATE utf8mb4_general_ci = %(src)s UNION ALL

        SELECT 'May',      COALESCE(SUM(may_l),0)
        FROM vw_equity_pipeline_norm
        WHERE source COLLATE utf8mb4_general_ci = %(src)s UNION ALL

        SELECT 'June',     COALESCE(SUM(june_l),0)
        FROM vw_equity_pipeline_norm
        WHERE source COLLATE utf8mb4_general_ci = %(src)s UNION ALL

        SELECT 'July',     COALESCE(SUM(july_l),0)
        FROM vw_equity_pipeline_norm
        WHERE source COLLATE utf8mb4_general_ci = %(src)s UNION ALL

        SELECT 'August',   COALESCE(SUM(august_l),0)
        FROM vw_equity_pipeline_norm
        WHERE source COLLATE utf8mb4_general_ci = %(src)s UNION ALL

        SELECT 'September',COALESCE(SUM(september_l),0)
        FROM vw_equity_pipeline_norm
        WHERE source COLLATE utf8mb4_general_ci = %(src)s UNION ALL

        SELECT 'October',  COALESCE(SUM(october_l),0)
        FROM vw_equity_pipeline_norm
        WHERE source COLLATE utf8mb4_general_ci = %(src)s UNION ALL

        SELECT 'November', COALESCE(SUM(november_l),0)
        FROM vw_equity_pipeline_norm
        WHERE source COLLATE utf8mb4_general_ci = %(src)s UNION ALL

        SELECT 'December', COALESCE(SUM(december_l),0)
        FROM vw_equity_pipeline_norm
        WHERE source COLLATE utf8mb4_general_ci = %(src)s
    """
    rows = _rows(sql, {"src": src})
    labels = [r["month"] for r in rows]
    data = [float(r["amount"] or 0) for r in rows]
    return jsonify({"source": src, "labels": labels, "data": data})