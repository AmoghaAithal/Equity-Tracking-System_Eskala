
"""
Exchange Rate API - Flask Blueprint
Manages exchange rates for HNL to USD conversions with version control and audit trail
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import text
from db import SessionLocal
from datetime import datetime
import json

bp = Blueprint("fx_rates", __name__, url_prefix="/api/fx-rates")

# ============================================
# GET CURRENT EXCHANGE RATE
# ============================================

@bp.get("/current")
def get_current_rate():
    """Get the current active exchange rate for HNL to USD"""
    try:
        with SessionLocal() as s:
            row = s.execute(text("""
                SELECT 
                    fx_rate_id,
                    from_currency,
                    to_currency,
                    rate,
                    valid_from,
                    valid_to
                FROM fx_rates
                WHERE from_currency = 'HNL'
                  AND to_currency = 'USD'
                  AND valid_to IS NULL
                ORDER BY valid_from DESC
                LIMIT 1
            """)).fetchone()
            
            if not row:
                # Return default rate if none exists
                return jsonify(
                    success=True,
                    rate={
                        'from_currency': 'HNL',
                        'to_currency': 'USD',
                        'rate': '25.2500',
                        'valid_from': datetime.now().isoformat(),
                        'valid_to': None
                    }
                ), 200
            
            return jsonify(
                success=True,
                rate={
                    'fx_rate_id': row.fx_rate_id,
                    'from_currency': row.from_currency,
                    'to_currency': row.to_currency,
                    'rate': str(row.rate),
                    'valid_from': row.valid_from.isoformat() if row.valid_from else None,
                    'valid_to': row.valid_to.isoformat() if row.valid_to else None
                }
            ), 200
            
    except Exception as e:
        print(f"ERROR in get_current_rate: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(success=False, error=str(e)), 500


# ============================================
# GET ALL EXCHANGE RATES (CURRENT & HISTORICAL)
# ============================================

@bp.get("/all")
def get_all_rates():
    """Get all exchange rates (current and historical) for HNL to USD"""
    try:
        with SessionLocal() as s:
            rows = s.execute(text("""
                SELECT 
                    fx_rate_id,
                    from_currency,
                    to_currency,
                    rate,
                    valid_from,
                    valid_to
                FROM fx_rates
                WHERE from_currency = 'HNL' AND to_currency = 'USD'
                ORDER BY valid_from DESC
            """)).fetchall()
            
            rates = []
            for row in rows:
                rates.append({
                    'fx_rate_id': row.fx_rate_id,
                    'from_currency': row.from_currency,
                    'to_currency': row.to_currency,
                    'rate': str(row.rate),
                    'valid_from': row.valid_from.isoformat() if row.valid_from else None,
                    'valid_to': row.valid_to.isoformat() if row.valid_to else None
                })
            
            return jsonify(success=True, rates=rates), 200
            
    except Exception as e:
        print(f"ERROR in get_all_rates: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(success=False, error=str(e)), 500


# ============================================
# GET EXCHANGE RATE CHANGE HISTORY
# ============================================

@bp.get("/history")
def get_history():
    """Get exchange rate change history with audit information"""
    try:
        with SessionLocal() as s:
            rows = s.execute(text("""
                SELECT 
                    curr.fx_rate_id,
                    curr.from_currency,
                    curr.to_currency,
                    prev.rate as old_rate,
                    curr.rate as new_rate,
                    curr.valid_from as effective_date,
                    al.changed_by,
                    al.changed_at,
                    al.diff_json,
                    JSON_UNQUOTE(JSON_EXTRACT(al.diff_json, '$.reason')) as reason,
                    JSON_UNQUOTE(JSON_EXTRACT(al.diff_json, '$.changed_by_username')) as changed_by_username
                FROM fx_rates curr
                LEFT JOIN fx_rates prev ON 
                    curr.from_currency = prev.from_currency
                    AND curr.to_currency = prev.to_currency
                    AND prev.valid_to = curr.valid_from
                LEFT JOIN audit_log al ON 
                    al.table_name = 'fx_rates'
                    AND CAST(al.row_pk AS CHAR) = CAST(curr.fx_rate_id AS CHAR)
                    AND al.action = 'INSERT'
                WHERE curr.from_currency = 'HNL' 
                  AND curr.to_currency = 'USD'
                ORDER BY curr.valid_from DESC
            """)).fetchall()
            
            # Get user names for those who made changes (fallback for older records)
            user_ids = list(set([row.changed_by for row in rows if row.changed_by and not row.changed_by_username]))
            user_map = {}
            
            if user_ids:
                placeholders = ','.join([':uid' + str(i) for i in range(len(user_ids))])
                user_params = {f'uid{i}': uid for i, uid in enumerate(user_ids)}
                
                users = s.execute(text(f"""
                    SELECT user_id, username, email 
                    FROM users 
                    WHERE user_id IN ({placeholders})
                """), user_params).fetchall()
                
                for user in users:
                    user_map[user.user_id] = user.username or user.email
            
            # Build history with user names
            history = []
            for row in rows:
                # Prefer username from diff_json, fallback to user lookup
                if row.changed_by_username:
                    display_name = row.changed_by_username
                elif row.changed_by:
                    display_name = user_map.get(row.changed_by, f'User #{row.changed_by}')
                else:
                    display_name = None
                    
                history.append({
                    'fx_rate_id': row.fx_rate_id,
                    'from_currency': row.from_currency,
                    'to_currency': row.to_currency,
                    'old_rate': str(row.old_rate) if row.old_rate else None,
                    'new_rate': str(row.new_rate),
                    'effective_date': row.effective_date.isoformat() if row.effective_date else None,
                    'changed_by': display_name,
                    'changed_at': row.changed_at.isoformat() if row.changed_at else None,
                    'reason': row.reason
                })
            
            return jsonify(success=True, history=history), 200
            
    except Exception as e:
        print(f"ERROR in get_history: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(success=False, error=str(e)), 500


# ============================================
# UPDATE EXCHANGE RATE
# ============================================

@bp.post("/update")
def update_rate():
    """Update the exchange rate (creates new version with history tracking)"""
    from flask import session
    
    data = request.get_json()
    
    from_currency = data.get('from_currency', 'HNL')
    to_currency = data.get('to_currency', 'USD')
    rate = data.get('rate')
    effective_date = data.get('effective_date')
    reason = data.get('reason', '').strip()
    
    # Get user from session (secure - set during login)
    user_id = session.get('user_id')
    username = session.get('username') or session.get('email') or 'Unknown'
    
    print(f"🔍 Exchange rate update by user_id={user_id}, username={username}")
    
    # Validation
    if not rate or float(rate) <= 0:
        return jsonify(success=False, message='Invalid exchange rate'), 400
    
    if not effective_date:
        return jsonify(success=False, message='Effective date is required'), 400
    
    if not reason:
        return jsonify(success=False, message='Reason for change is required'), 400
    
    try:
        rate = float(rate)
    except (ValueError, TypeError):
        return jsonify(success=False, message='Rate must be a valid number'), 400
    
    try:
        with SessionLocal() as s, s.begin():
            # Get the current active rate
            current_rate = s.execute(text("""
                SELECT fx_rate_id, rate
                FROM fx_rates
                WHERE from_currency = :from_curr 
                  AND to_currency = :to_curr
                  AND valid_to IS NULL
                FOR UPDATE
            """), {
                "from_curr": from_currency,
                "to_curr": to_currency
            }).fetchone()
            
            # Parse effective date
            try:
                if 'T' in effective_date:
                    effective_datetime = datetime.fromisoformat(effective_date.replace('Z', '+00:00'))
                else:
                    effective_datetime = datetime.strptime(effective_date, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                effective_datetime = datetime.now()
            
            # Close out the current rate
            if current_rate:
                s.execute(text("""
                    UPDATE fx_rates
                    SET valid_to = :valid_to
                    WHERE fx_rate_id = :rate_id
                """), {
                    "valid_to": effective_datetime,
                    "rate_id": current_rate.fx_rate_id
                })
            
            # Insert new rate
            result = s.execute(text("""
                INSERT INTO fx_rates (from_currency, to_currency, rate, valid_from, valid_to)
                VALUES (:from_curr, :to_curr, :rate, :valid_from, NULL)
            """), {
                "from_curr": from_currency,
                "to_curr": to_currency,
                "rate": rate,
                "valid_from": effective_datetime
            })
            
            new_rate_id = result.lastrowid
            
            # Create audit log entry with username in diff_json
            audit_diff = {
                'old_rate': str(current_rate.rate) if current_rate else None,
                'new_rate': str(rate),
                'reason': reason,
                'effective_date': effective_datetime.isoformat(),
                'changed_by_username': username
            }
            
            s.execute(text("""
                INSERT INTO audit_log (table_name, row_pk, action, diff_json, changed_by, changed_at)
                VALUES ('fx_rates', :row_pk, 'INSERT', :diff_json, :changed_by, NOW())
            """), {
                "row_pk": str(new_rate_id),
                "diff_json": json.dumps(audit_diff),
                "changed_by": user_id
            })
            
        return jsonify(
            success=True,
            message='Exchange rate updated successfully',
            rate={
                'fx_rate_id': new_rate_id,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'rate': str(rate),
                'valid_from': effective_datetime.isoformat(),
                'valid_to': None
            }
        ), 200
        
    except Exception as e:
        print(f"ERROR in update_rate: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(success=False, error=str(e)), 500


# ============================================
# GET EXCHANGE RATE AT SPECIFIC DATE
# ============================================

@bp.get("/rate-at-date")
def get_rate_at_date():
    """Get the exchange rate that was valid at a specific date"""
    from_curr = request.args.get('from', 'HNL')
    to_curr = request.args.get('to', 'USD')
    date_str = request.args.get('date')
    
    if not date_str:
        return jsonify(success=False, message='Date parameter is required'), 400
    
    try:
        if 'T' in date_str:
            query_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            query_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify(success=False, message='Invalid date format'), 400
    
    try:
        with SessionLocal() as s:
            row = s.execute(text("""
                SELECT 
                    fx_rate_id,
                    from_currency,
                    to_currency,
                    rate,
                    valid_from,
                    valid_to
                FROM fx_rates
                WHERE from_currency = :from_curr
                  AND to_currency = :to_curr
                  AND valid_from <= :query_date
                  AND (valid_to IS NULL OR valid_to > :query_date)
                ORDER BY valid_from DESC
                LIMIT 1
            """), {
                "from_curr": from_curr,
                "to_curr": to_curr,
                "query_date": query_date
            }).fetchone()
            
            if not row:
                return jsonify(
                    success=False, 
                    message='No exchange rate found for the specified date'
                ), 404
            
            return jsonify(
                success=True,
                rate={
                    'fx_rate_id': row.fx_rate_id,
                    'from_currency': row.from_currency,
                    'to_currency': row.to_currency,
                    'rate': str(row.rate),
                    'valid_from': row.valid_from.isoformat() if row.valid_from else None,
                    'valid_to': row.valid_to.isoformat() if row.valid_to else None
                }
            ), 200
            
    except Exception as e:
        print(f"ERROR in get_rate_at_date: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(success=False, error=str(e)), 500