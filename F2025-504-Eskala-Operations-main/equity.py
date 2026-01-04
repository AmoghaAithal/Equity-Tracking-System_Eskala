
import pathlib, time
import csv
from io import StringIO
from flask import Blueprint, request, jsonify, session
from sqlalchemy import text
from db import SessionLocal, run_query

bp = Blueprint("equity", __name__, url_prefix="/api/equity")
UPLOAD_DIR = pathlib.Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

def _save(fsfile, prefix):
    if not fsfile: return None
    ext = (fsfile.filename or "bin").split(".")[-1]
    name = f"{prefix}-{int(time.time()*1000)}.{ext}"
    path = UPLOAD_DIR / name
    fsfile.save(path)
    return f"/uploads/{name}"

def get_user_role(user_id):
    """Get the role name for a given user_id"""
    try:
        result = run_query("""
            SELECT r.role_name 
            FROM user_roles ur
            JOIN roles r ON r.role_id = ur.role_id
            WHERE ur.user_id = :uid
            LIMIT 1
        """, uid=user_id).first()
        return result.role_name if result else None
    except:
        return None

def require_auth():
    """Check if user is authenticated, return user_id and role"""

    if not session.get('is_authenticated'):
        # 3 values: user_id, role, auth_error
        return None, None, (jsonify(ok=False, error="Not authenticated"), 401)
    
    user_id = session.get('user_id')
    if not user_id:
        # 3 values again
        return None, None, (jsonify(ok=False, error="Invalid session"), 401)
    
    role = get_user_role(user_id)
    # success: no error
    return user_id, role, None


# ============================================
# EQUITY CONVERSION FORM SUBMISSION
# ============================================

@bp.post("/conversion")
def conversion():
    """Handle Equity Conversion form submission"""
    # Check authentication
    user_id, role, auth_error = require_auth()
    if auth_error:
        return auth_error
    
    b = request.form
    f = request.files.get("attachment")
    
    bank_name = (b.get("bank_name") or "").strip()
    rtn_number = (b.get("rtn_number") or "").strip()
    representative_name = (b.get("representative_name") or "").strip()
    phone_number = (b.get("phone_number") or "").strip()
    loan_id = (b.get("loan_id") or "").strip()
    
    # Convert string amounts to float or None
    original_loan_amount = b.get("original_loan_amount", "").strip()
    original_loan_amount = float(original_loan_amount) if original_loan_amount else None
    
    interest_paid = b.get("interest_paid", "").strip()
    interest_paid = float(interest_paid) if interest_paid else None
    
    loan_amount_remaining = b.get("loan_amount_remaining", "").strip()
    loan_amount_remaining = float(loan_amount_remaining) if loan_amount_remaining else None
    
    proposed_conversion_amount = b.get("proposed_conversion_amount", "").strip()
    proposed_conversion_amount = float(proposed_conversion_amount) if proposed_conversion_amount else None
    
    proposed_equity_percentage = b.get("proposed_equity_percentage", "").strip()
    proposed_equity_percentage = float(proposed_equity_percentage) if proposed_equity_percentage else None
    
    loan_approval_date = b.get("loan_approval_date", "").strip() or None
    repayment_frequency = (b.get("repayment_frequency") or "").strip()
    proposed_conversion_ratio = (b.get("proposed_conversion_ratio") or "").strip()
    desired_conversion_date = b.get("desired_conversion_date", "").strip() or None
    comments = (b.get("comments") or "").strip()
    confirmed = b.get("confirmed", "false").lower() == "true"
    
    # Save file if present
    attachment_path = None
    if f:
        attachment_path = _save(f, f'conversion-{int(time.time())}')

    try:
        with SessionLocal() as s, s.begin():
            s.execute(text("""
                INSERT INTO equity_conversion_form_submissions
                (bank_name, rtn_number, representative_name, phone_number,
                 loan_id, original_loan_amount, loan_approval_date, interest_paid,
                 loan_amount_remaining, repayment_frequency, proposed_conversion_amount,
                 proposed_conversion_ratio, proposed_equity_percentage, 
                 desired_conversion_date, comments, attachment_path, confirmed, status, submitted_by)
                VALUES (:bank_name, :rtn, :rep_name, :phone, :loan_id, 
                        :orig_amount, :approval_date, :interest, :remaining,
                        :frequency, :conv_amount, :conv_ratio, :equity_pct,
                        :desired_date, :comments, :attachment, :confirmed, 'SUBMITTED', :user_id)
            """), {
                "bank_name": bank_name,
                "rtn": rtn_number,
                "rep_name": representative_name,
                "phone": phone_number,
                "loan_id": loan_id,
                "orig_amount": original_loan_amount,
                "approval_date": loan_approval_date,
                "interest": interest_paid,
                "remaining": loan_amount_remaining,
                "frequency": repayment_frequency,
                "conv_amount": proposed_conversion_amount,
                "conv_ratio": proposed_conversion_ratio,
                "equity_pct": proposed_equity_percentage,
                "desired_date": desired_conversion_date,
                "comments": comments,
                "attachment": attachment_path,
                "confirmed": confirmed,
                "user_id": user_id
            })
            
        return jsonify(ok=True, message="Conversion request submitted successfully"), 201
    except Exception as e:
        print(f"❌ Error in profit bulk upload: {e}")
        import traceback
        traceback.print_exc()
        # Don't expose SQL errors to users - show friendly message instead
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading your CSV file. Please check that your file follows the template format and all required fields are filled in correctly. If the problem persists, contact support.'
        }), 500

# ============================================
# DIVIDEND PAYOUT FORM SUBMISSION
# ============================================

@bp.post("/entry")
def entry():
    """Handle Dividend Payout form submission"""
    # Check authentication
    user_id, role, auth_error = require_auth()
    if auth_error:
        return auth_error
    
    b = request.form
    f = request.files.get("payment_proof")

    bank_id = (b.get("bank_id") or "").strip()  # RTN Number
    partner_name = (b.get("partner_name") or "").strip()
    
    # Convert string amounts to float or None
    reported_shares = b.get("shares", "").strip()
    reported_shares = float(reported_shares) if reported_shares else None
    
    investment_hnl = b.get("investment_hnl", "").strip()
    investment_hnl = float(investment_hnl) if investment_hnl else None
    
    investment_usd = b.get("investment_usd", "").strip()
    investment_usd = float(investment_usd) if investment_usd else None
    
    amount_paid = b.get("amount_paid", "").strip()
    amount_paid = float(amount_paid) if amount_paid else None
    
    payout_date = b.get("payout_date", "").strip() or None
    payment_method = (b.get("payment_method") or "").strip()
    comments = (b.get("comments") or "").strip()
    confirmed = b.get("confirmed", "false").lower() == "true"
    
    # Save file if present
    proof_path = None
    if f:
        proof_path = _save(f, f'proof-{int(time.time())}')

    try:
        with SessionLocal() as s, s.begin():
            s.execute(text("""
                INSERT INTO dividend_payout_form_submissions
                (bank_id, partner_name, reported_shares, investment_hnl, investment_usd,
                 payout_date, amount_paid, payment_method, payment_proof_path,
                 comments, confirmed, status, submitted_by)
                VALUES (:bank_id, :partner, :shares, :inv_hnl, :inv_usd,
                        :payout_dt, :amount, :method, :proof,
                        :comments, :confirmed, 'SUBMITTED', :user_id)
            """), {
                "bank_id": bank_id,
                "partner": partner_name,
                "shares": reported_shares,
                "inv_hnl": investment_hnl,
                "inv_usd": investment_usd,
                "payout_dt": payout_date,
                "amount": amount_paid,
                "method": payment_method,
                "proof": proof_path,
                "comments": comments,
                "confirmed": confirmed,
                "user_id": user_id
            })
            
        return jsonify(ok=True, message="Dividend payout entry submitted successfully"), 201
    except Exception as e:
        print(f"❌ Error in profit bulk upload: {e}")
        import traceback
        traceback.print_exc()
        # Don't expose SQL errors to users - show friendly message instead
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading your CSV file. Please check that your file follows the template format and all required fields are filled in correctly. If the problem persists, contact support.'
        }), 500

@bp.get("/entry/submissions")
def get_entry_submissions():
    """Get dividend payout form submissions - filtered by user role"""
    # Check authentication
    user_id, role, auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        with SessionLocal() as s:
            # Base query
            query = """
                SELECT 
                    d.submission_id, d.bank_id, d.partner_name, d.reported_shares,
                    d.investment_hnl, d.investment_usd, d.payout_date, d.amount_paid,
                    d.payment_method, d.payment_proof_path, d.comments, d.confirmed, d.status,
                    d.created_at, d.updated_at, d.edited_at, d.submitted_by,
                    u.username as edited_by
                FROM dividend_payout_form_submissions d
                LEFT JOIN users u ON d.edited_by = u.user_id
            """
            
            # Filter by user for community reps (banking partners)
            if role == "COMMUNITY_REP":
                query += " WHERE d.submitted_by = :user_id"
                params = {"user_id": user_id}
            else:
                # STAFF sees all submissions
                params = {}
            
            query += " ORDER BY d.created_at DESC"
            
            rows = s.execute(text(query), params).fetchall()
            
            entries = []
            for row in rows:
                entries.append({
                    'submission_id': row.submission_id,
                    'bank_id': row.bank_id,
                    'partner_name': row.partner_name,
                    'reported_shares': float(row.reported_shares) if row.reported_shares else None,
                    'investment_hnl': float(row.investment_hnl) if row.investment_hnl else None,
                    'investment_usd': float(row.investment_usd) if row.investment_usd else None,
                    'payout_date': row.payout_date.isoformat() if row.payout_date else None,
                    'amount_paid': float(row.amount_paid) if row.amount_paid else None,
                    'payment_method': row.payment_method,
                    'payment_proof_path': row.payment_proof_path,
                    'comments': row.comments,
                    'confirmed': row.confirmed,
                    'status': row.status,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                    'edited_at': row.edited_at.isoformat() if row.edited_at else None,
                    'edited_by': row.edited_by
                })
            
            return jsonify(ok=True, submissions=entries), 200
            
    except Exception as e:
        print(f"❌ Error in profit bulk upload: {e}")
        import traceback
        traceback.print_exc()
        # Don't expose SQL errors to users - show friendly message instead
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading your CSV file. Please check that your file follows the template format and all required fields are filled in correctly. If the problem persists, contact support.'
        }), 500

@bp.get("/entry/submission/<int:submission_id>")
def get_entry_submission(submission_id):
    """Get a single dividend payout submission by ID"""
    try:
        with SessionLocal() as s:
            row = s.execute(text("""
                SELECT 
                    d.submission_id, d.bank_id, d.partner_name, d.reported_shares,
                    d.investment_hnl, d.investment_usd, d.payout_date, d.amount_paid,
                    d.payment_method, d.payment_proof_path, d.comments, d.confirmed, d.status,
                    d.created_at, d.updated_at, d.edited_at,
                    u.username as edited_by
                FROM dividend_payout_form_submissions d
                LEFT JOIN users u ON d.edited_by = u.user_id
                WHERE d.submission_id = :id
            """), {"id": submission_id}).fetchone()
            
            if not row:
                return jsonify(ok=False, error="Submission not found"), 404
            
            submission = {
                'submission_id': row.submission_id,
                'bank_id': row.bank_id,
                'partner_name': row.partner_name,
                'reported_shares': float(row.reported_shares) if row.reported_shares else None,
                'investment_hnl': float(row.investment_hnl) if row.investment_hnl else None,
                'investment_usd': float(row.investment_usd) if row.investment_usd else None,
                'payout_date': row.payout_date.isoformat() if row.payout_date else None,
                'amount_paid': float(row.amount_paid) if row.amount_paid else None,
                'payment_method': row.payment_method,
                'payment_proof_path': row.payment_proof_path,
                'comments': row.comments,
                'confirmed': row.confirmed,
                'status': row.status,
                'created_at': row.created_at.isoformat() if row.created_at else None,
                'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                'edited_at': row.edited_at.isoformat() if row.edited_at else None,
                'edited_by': row.edited_by
            }
            
            return jsonify(ok=True, submission=submission), 200
            
    except Exception as e:
        print(f"❌ Error in profit bulk upload: {e}")
        import traceback
        traceback.print_exc()
        # Don't expose SQL errors to users - show friendly message instead
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading your CSV file. Please check that your file follows the template format and all required fields are filled in correctly. If the problem persists, contact support.'
        }), 500

@bp.put("/entry/submission/<int:submission_id>")
def update_entry_submission(submission_id):
    """Update a dividend payout submission"""
    try:
        data = request.get_json()
        username = session.get('username', 'System')
        
        # Get the user_id from username
        with SessionLocal() as s:
            user_row = s.execute(text("SELECT user_id FROM users WHERE username = :username"), 
                                {"username": username}).fetchone()
            user_id = user_row.user_id if user_row else None
        
        with SessionLocal() as s, s.begin():
            s.execute(text("""
                UPDATE dividend_payout_form_submissions
                SET bank_id = :bank_id,
                    partner_name = :partner_name,
                    reported_shares = :reported_shares,
                    investment_hnl = :investment_hnl,
                    investment_usd = :investment_usd,
                    payout_date = :payout_date,
                    amount_paid = :amount_paid,
                    payment_method = :payment_method,
                    status = :status,
                    comments = :comments,
                    edited_by = :edited_by,
                    edited_at = NOW()
                WHERE submission_id = :submission_id
            """), {
                "submission_id": submission_id,
                "bank_id": data.get("bank_id"),
                "partner_name": data.get("partner_name"),
                "reported_shares": data.get("reported_shares"),
                "investment_hnl": data.get("investment_hnl"),
                "investment_usd": data.get("investment_usd"),
                "payout_date": data.get("payout_date"),
                "amount_paid": data.get("amount_paid"),
                "payment_method": data.get("payment_method"),
                "status": data.get("status"),
                "comments": data.get("comments"),
                "edited_by": user_id
            })
        
        return jsonify(ok=True, message="Submission updated successfully"), 200
        
    except Exception as e:
        print(f"❌ Error in profit bulk upload: {e}")
        import traceback
        traceback.print_exc()
        # Don't expose SQL errors to users - show friendly message instead
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading your CSV file. Please check that your file follows the template format and all required fields are filled in correctly. If the problem persists, contact support.'
        }), 500

@bp.delete("/entry/submission/<int:submission_id>")
def delete_entry_submission(submission_id):
    """Delete a dividend payout submission"""
    try:
        username = session.get('username', 'System')
        print(f"🗑️ Deleting dividend payout submission {submission_id} by: {username}")
        
        # Optional: Get proof path to delete file
        with SessionLocal() as s:
            row = s.execute(text("""
                SELECT payment_proof_path 
                FROM dividend_payout_form_submissions 
                WHERE submission_id = :id
            """), {"id": submission_id}).fetchone()
            
            if row and row.payment_proof_path:
                # Delete the file if it exists
                import os
                file_path = str(UPLOAD_DIR / row.payment_proof_path.split('/')[-1])
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"✅ Deleted proof file: {file_path}")
                    except Exception as file_err:
                        print(f"⚠️ Error deleting file: {file_err}")
        
        # Delete the submission
        with SessionLocal() as s, s.begin():
            s.execute(text("""
                DELETE FROM dividend_payout_form_submissions
                WHERE submission_id = :id
            """), {"id": submission_id})
        
        print(f"✅ Submission {submission_id} deleted successfully")
        return jsonify(ok=True, message="Submission deleted successfully"), 200
        
    except Exception as e:
        print(f"❌ Error in profit bulk upload: {e}")
        import traceback
        traceback.print_exc()
        # Don't expose SQL errors to users - show friendly message instead
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading your CSV file. Please check that your file follows the template format and all required fields are filled in correctly. If the problem persists, contact support.'
        }), 500

@bp.get("/conversion/submissions")
def get_conversion_submissions():
    """Get equity conversion form submissions - filtered by user role"""
    # Check authentication
    user_id, role, auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        with SessionLocal() as s:
            # Base query
            query = """
                SELECT 
                    e.submission_id, e.bank_name, e.rtn_number, e.representative_name, e.phone_number,
                    e.loan_id, e.original_loan_amount, e.loan_approval_date, e.interest_paid,
                    e.loan_amount_remaining, e.repayment_frequency, e.proposed_conversion_amount,
                    e.proposed_conversion_ratio, e.proposed_equity_percentage, 
                    e.desired_conversion_date, e.comments, e.attachment_path, e.confirmed, e.status,
                    e.created_at, e.updated_at, e.edited_at, e.submitted_by,
                    u.username as edited_by
                FROM equity_conversion_form_submissions e
                LEFT JOIN users u ON e.edited_by = u.user_id
            """
            
            # Filter by user for community reps (banking partners)
            if role == "COMMUNITY_REP":
                query += " WHERE e.submitted_by = :user_id"
                params = {"user_id": user_id}
            else:
                # STAFF sees all submissions
                params = {}
            
            query += " ORDER BY e.created_at DESC"
            
            rows = s.execute(text(query), params).fetchall()
            
            entries = []
            for row in rows:
                entries.append({
                    'submission_id': row.submission_id,
                    'bank_name': row.bank_name,
                    'rtn_number': row.rtn_number,
                    'representative_name': row.representative_name,
                    'phone_number': row.phone_number,
                    'loan_id': row.loan_id,
                    'original_loan_amount': float(row.original_loan_amount) if row.original_loan_amount else None,
                    'loan_approval_date': row.loan_approval_date.isoformat() if row.loan_approval_date else None,
                    'interest_paid': float(row.interest_paid) if row.interest_paid else None,
                    'loan_amount_remaining': float(row.loan_amount_remaining) if row.loan_amount_remaining else None,
                    'repayment_frequency': row.repayment_frequency,
                    'proposed_conversion_amount': float(row.proposed_conversion_amount) if row.proposed_conversion_amount else None,
                    'proposed_conversion_ratio': row.proposed_conversion_ratio,
                    'proposed_equity_percentage': float(row.proposed_equity_percentage) if row.proposed_equity_percentage else None,
                    'desired_conversion_date': row.desired_conversion_date.isoformat() if row.desired_conversion_date else None,
                    'comments': row.comments,
                    'attachment_path': row.attachment_path,
                    'confirmed': row.confirmed,
                    'status': row.status,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                    'edited_at': row.edited_at.isoformat() if row.edited_at else None,
                    'edited_by': row.edited_by
                })
            
            return jsonify(ok=True, submissions=entries), 200
            
    except Exception as e:
        print(f"❌ Error in profit bulk upload: {e}")
        import traceback
        traceback.print_exc()
        # Don't expose SQL errors to users - show friendly message instead
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading your CSV file. Please check that your file follows the template format and all required fields are filled in correctly. If the problem persists, contact support.'
        }), 500

@bp.get("/conversion/submission/<int:submission_id>")
def get_conversion_submission(submission_id):
    """Get a single equity conversion submission by ID"""
    try:
        with SessionLocal() as s:
            row = s.execute(text("""
                SELECT 
                    e.submission_id, e.bank_name, e.rtn_number, e.representative_name, e.phone_number,
                    e.loan_id, e.original_loan_amount, e.loan_approval_date, e.interest_paid,
                    e.loan_amount_remaining, e.repayment_frequency, e.proposed_conversion_amount,
                    e.proposed_conversion_ratio, e.proposed_equity_percentage, 
                    e.desired_conversion_date, e.comments, e.attachment_path, e.confirmed, e.status,
                    e.created_at, e.updated_at, e.edited_at,
                    u.username as edited_by
                FROM equity_conversion_form_submissions e
                LEFT JOIN users u ON e.edited_by = u.user_id
                WHERE e.submission_id = :id
            """), {"id": submission_id}).fetchone()
            
            if not row:
                return jsonify(ok=False, error="Submission not found"), 404
            
            submission = {
                'submission_id': row.submission_id,
                'bank_name': row.bank_name,
                'rtn_number': row.rtn_number,
                'representative_name': row.representative_name,
                'phone_number': row.phone_number,
                'loan_id': row.loan_id,
                'original_loan_amount': float(row.original_loan_amount) if row.original_loan_amount else None,
                'loan_approval_date': row.loan_approval_date.isoformat() if row.loan_approval_date else None,
                'interest_paid': float(row.interest_paid) if row.interest_paid else None,
                'loan_amount_remaining': float(row.loan_amount_remaining) if row.loan_amount_remaining else None,
                'repayment_frequency': row.repayment_frequency,
                'proposed_conversion_amount': float(row.proposed_conversion_amount) if row.proposed_conversion_amount else None,
                'proposed_conversion_ratio': row.proposed_conversion_ratio,
                'proposed_equity_percentage': float(row.proposed_equity_percentage) if row.proposed_equity_percentage else None,
                'desired_conversion_date': row.desired_conversion_date.isoformat() if row.desired_conversion_date else None,
                'comments': row.comments,
                'attachment_path': row.attachment_path,
                'confirmed': row.confirmed,
                'status': row.status,
                'created_at': row.created_at.isoformat() if row.created_at else None,
                'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                'edited_at': row.edited_at.isoformat() if row.edited_at else None,
                'edited_by': row.edited_by
            }
            
            return jsonify(ok=True, submission=submission), 200
            
    except Exception as e:
        print(f"❌ Error in profit bulk upload: {e}")
        import traceback
        traceback.print_exc()
        # Don't expose SQL errors to users - show friendly message instead
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading your CSV file. Please check that your file follows the template format and all required fields are filled in correctly. If the problem persists, contact support.'
        }), 500

@bp.put("/conversion/submission/<int:submission_id>")
def update_conversion_submission(submission_id):
    """Update an equity conversion submission"""
    try:
        data = request.get_json()
        username = session.get('username', 'System')
        
        # Get the user_id from username
        with SessionLocal() as s:
            user_row = s.execute(text("SELECT user_id FROM users WHERE username = :username"), 
                                {"username": username}).fetchone()
            user_id = user_row.user_id if user_row else None
        
        with SessionLocal() as s, s.begin():
            s.execute(text("""
                UPDATE equity_conversion_form_submissions
                SET bank_name = :bank_name,
                    rtn_number = :rtn_number,
                    representative_name = :representative_name,
                    phone_number = :phone_number,
                    loan_id = :loan_id,
                    original_loan_amount = :original_loan_amount,
                    loan_approval_date = :loan_approval_date,
                    interest_paid = :interest_paid,
                    loan_amount_remaining = :loan_amount_remaining,
                    repayment_frequency = :repayment_frequency,
                    proposed_conversion_amount = :proposed_conversion_amount,
                    proposed_conversion_ratio = :proposed_conversion_ratio,
                    proposed_equity_percentage = :proposed_equity_percentage,
                    desired_conversion_date = :desired_conversion_date,
                    status = :status,
                    comments = :comments,
                    edited_by = :edited_by,
                    edited_at = NOW()
                WHERE submission_id = :submission_id
            """), {
                "submission_id": submission_id,
                "bank_name": data.get("bank_name"),
                "rtn_number": data.get("rtn_number"),
                "representative_name": data.get("representative_name"),
                "phone_number": data.get("phone_number"),
                "loan_id": data.get("loan_id"),
                "original_loan_amount": data.get("original_loan_amount"),
                "loan_approval_date": data.get("loan_approval_date"),
                "interest_paid": data.get("interest_paid"),
                "loan_amount_remaining": data.get("loan_amount_remaining"),
                "repayment_frequency": data.get("repayment_frequency"),
                "proposed_conversion_amount": data.get("proposed_conversion_amount"),
                "proposed_conversion_ratio": data.get("proposed_conversion_ratio"),
                "proposed_equity_percentage": data.get("proposed_equity_percentage"),
                "desired_conversion_date": data.get("desired_conversion_date"),
                "status": data.get("status"),
                "comments": data.get("comments"),
                "edited_by": user_id
            })
        
        return jsonify(ok=True, message="Submission updated successfully"), 200
        
    except Exception as e:
        print(f"❌ Error in profit bulk upload: {e}")
        import traceback
        traceback.print_exc()
        # Don't expose SQL errors to users - show friendly message instead
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading your CSV file. Please check that your file follows the template format and all required fields are filled in correctly. If the problem persists, contact support.'
        }), 500

@bp.delete("/conversion/submission/<int:submission_id>")
def delete_conversion_submission(submission_id):
    """Delete an equity conversion submission"""
    try:
        username = session.get('username', 'System')
        print(f"🗑️ Deleting conversion submission {submission_id} by: {username}")
        
        # Optional: Get attachment path to delete file
        with SessionLocal() as s:
            row = s.execute(text("""
                SELECT attachment_path 
                FROM equity_conversion_form_submissions 
                WHERE submission_id = :id
            """), {"id": submission_id}).fetchone()
            
            if row and row.attachment_path:
                # Delete the file if it exists
                import os
                file_path = str(UPLOAD_DIR / row.attachment_path.split('/')[-1])
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"✅ Deleted attachment file: {file_path}")
                    except Exception as file_err:
                        print(f"⚠️ Error deleting file: {file_err}")
        
        # Delete the submission
        with SessionLocal() as s, s.begin():
            s.execute(text("""
                DELETE FROM equity_conversion_form_submissions
                WHERE submission_id = :id
            """), {"id": submission_id})
        
        print(f"✅ Submission {submission_id} deleted successfully")
        return jsonify(ok=True, message="Submission deleted successfully"), 200
        
    except Exception as e:
        print(f"❌ Error in profit bulk upload: {e}")
        import traceback
        traceback.print_exc()
        # Don't expose SQL errors to users - show friendly message instead
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading your CSV file. Please check that your file follows the template format and all required fields are filled in correctly. If the problem persists, contact support.'
        }), 500

# ============================================
# INVESTMENT VS LOAN ENDPOINTS
# ============================================

@bp.post("/investment-loan")
def investment_loan():
    """Handle investment vs loan form submission"""
    b = request.form
    f = request.files.get("supporting_file")  # Changed from "attachment" to match HTML form
    
    # Get actual form fields that match ivl_form_entries table
    partner_name = (b.get("partner_name") or "").strip()
    expected_profit_pct = b.get("expected_profit_pct", "").strip()
    expected_profit_pct = float(expected_profit_pct) if expected_profit_pct else None
    
    investment_amount = b.get("investment_amount", "").strip()
    investment_amount = float(investment_amount) if investment_amount else None
    
    last_loan = b.get("last_loan", "").strip()
    last_loan = float(last_loan) if last_loan else None
    
    comments = (b.get("comments") or "").strip()
    
    # Calculate difference
    difference = None
    if investment_amount is not None and last_loan is not None:
        difference = investment_amount - last_loan
    
    # Save file if present and store filename in notes
    notes = None
    if f:
        file_path = _save(f, f'ivl-{int(time.time())}')
        # Store the actual saved filename (not the original filename)
        saved_filename = file_path.split('/')[-1] if file_path else f.filename
        notes = f"File: {saved_filename}"
    
    # Get username from session for audit trail
    username = session.get('username', 'System')

    try:
        with SessionLocal() as s, s.begin():
            s.execute(text("""
                INSERT INTO ivl_form_entries
                (partner_name, expected_profit_pct, investment_amount, last_loan, 
                 difference, comments, notes, created_by, updated_by)
                VALUES (:partner_name, :expected_profit_pct, :investment_amount, :last_loan,
                        :difference, :comments, :notes, :created_by, :updated_by)
            """), {
                "partner_name": partner_name,
                "expected_profit_pct": expected_profit_pct,
                "investment_amount": investment_amount,
                "last_loan": last_loan,
                "difference": difference,
                "comments": comments,
                "notes": notes,
                "created_by": username,
                "updated_by": username
            })
            
        return jsonify(ok=True, message="Investment vs Loan form submitted successfully"), 201
    except Exception as e:
        print(f"❌ Error in investment-loan submission: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'ok': False,
            'error': 'Submission failed',
            'message': 'An error occurred while submitting the form. Please try again or contact support.'
        }), 500

@bp.get("/investment-loan/submissions")
def get_investment_loan_submissions():
    """Get all investment vs loan form submissions"""
    try:
        with SessionLocal() as s:
            rows = s.execute(text("""
                SELECT 
                    submission_id, bank_name, rtn_number, representative_name, phone_number,
                    funding_type, proposed_amount, proposed_equity_percentage, interest_rate,
                    desired_funding_date, repayment_period_months,
                    business_description, use_of_funds, expected_roi,
                    comments, attachment_path, confirmed, status,
                    created_at, updated_at
                FROM investment_vs_loan_submissions
                ORDER BY created_at DESC
            """)).fetchall()
            
            entries = []
            for row in rows:
                entries.append({
                    'submission_id': row.submission_id,
                    'bank_name': row.bank_name,
                    'rtn_number': row.rtn_number,
                    'representative_name': row.representative_name,
                    'phone_number': row.phone_number,
                    'funding_type': row.funding_type,
                    'proposed_amount': float(row.proposed_amount) if row.proposed_amount else None,
                    'proposed_equity_percentage': float(row.proposed_equity_percentage) if row.proposed_equity_percentage else None,
                    'interest_rate': float(row.interest_rate) if row.interest_rate else None,
                    'desired_funding_date': row.desired_funding_date.isoformat() if row.desired_funding_date else None,
                    'repayment_period_months': row.repayment_period_months,
                    'business_description': row.business_description,
                    'use_of_funds': row.use_of_funds,
                    'expected_roi': float(row.expected_roi) if row.expected_roi else None,
                    'comments': row.comments,
                    'attachment_path': row.attachment_path,
                    'confirmed': row.confirmed,
                    'status': row.status,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None
                })
            
            return jsonify(ok=True, entries=entries), 200
            
    except Exception as e:
        print(f"❌ Error in profit bulk upload: {e}")
        import traceback
        traceback.print_exc()
        # Don't expose SQL errors to users - show friendly message instead
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading your CSV file. Please check that your file follows the template format and all required fields are filled in correctly. If the problem persists, contact support.'
        }), 500

# ============================================
# INVESTMENT VS LOAN - IVL ENDPOINTS
# These endpoints match the frontend URL structure
# ============================================

@bp.get("/ivl/entries")
def get_ivl_entries():
    """Get all investment vs loan entries from ivl_form_entries table"""
    try:
        with SessionLocal() as s:
            rows = s.execute(text("""
                SELECT 
                    ivl.investment_id as id,
                    ivl.partner_name,
                    ivl.expected_profit_pct,
                    ivl.investment_amount,
                    ivl.last_loan,
                    ivl.difference,
                    ivl.comments,
                    ivl.notes,
                    ivl.start_date,
                    ivl.created_at,
                    ivl.updated_at,
                    ivl.created_by,
                    ivl.updated_by
                FROM ivl_form_entries ivl
                ORDER BY ivl.created_at DESC
            """)).fetchall()
            
            entries = []
            for row in rows:
                entries.append({
                    'id': row.id,
                    'investment_id': row.id,  # Also include this in case frontend uses this field name
                    'partner_name': row.partner_name,
                    'expected_profit_pct': float(row.expected_profit_pct) if row.expected_profit_pct else None,
                    'investment_amount': float(row.investment_amount) if row.investment_amount else None,
                    'last_loan': float(row.last_loan) if row.last_loan else None,
                    'difference': float(row.difference) if row.difference else None,
                    'comments': row.comments,
                    'notes': row.notes,
                    'start_date': row.start_date.isoformat() if row.start_date else None,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                    'created_by': row.created_by,
                    'updated_by': row.updated_by
                })
            
            return jsonify(ok=True, entries=entries), 200
            
    except Exception as e:
        print(f"❌ Error loading IVL entries: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'ok': False,
            'error': 'Failed to load entries',
            'message': 'An error occurred while loading investment vs loan entries.'
        }), 500

@bp.get("/ivl/summary")
def get_ivl_summary():
    """Get summary statistics from ivl_form_entries table"""
    try:
        with SessionLocal() as s:
            row = s.execute(text("""
                SELECT 
                    COUNT(*) as total_entries,
                    SUM(investment_amount) as total_investment,
                    SUM(last_loan) as total_last_loan,
                    SUM(difference) as total_difference
                FROM ivl_form_entries
            """)).fetchone()
            
            summary = {
                'total_entries': row.total_entries or 0,
                'total_investment': float(row.total_investment) if row.total_investment else 0,
                'total_last_loan': float(row.total_last_loan) if row.total_last_loan else 0,
                'total_difference': float(row.total_difference) if row.total_difference else 0
            }
            
            return jsonify(ok=True, summary=summary), 200
            
    except Exception as e:
        print(f"❌ Error loading IVL summary: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'ok': False,
            'error': 'Failed to load summary',
            'message': 'An error occurred while loading summary statistics.'
        }), 500

@bp.get("/ivl/entry/<int:entry_id>")
def get_ivl_entry(entry_id):
    """Get a single IVL entry by ID"""
    try:
        with SessionLocal() as s:
            row = s.execute(text("""
                SELECT 
                    investment_id as id,
                    partner_name,
                    expected_profit_pct,
                    investment_amount,
                    last_loan,
                    difference,
                    comments
                FROM ivl_form_entries
                WHERE investment_id = :id
            """), {"id": entry_id}).fetchone()
            
            if not row:
                return jsonify(ok=False, error='Entry not found'), 404
            
            entry = {
                'id': row.id,
                'partner_name': row.partner_name,
                'expected_profit_pct': float(row.expected_profit_pct) if row.expected_profit_pct else None,
                'investment_amount': float(row.investment_amount) if row.investment_amount else None,
                'last_loan': float(row.last_loan) if row.last_loan else None,
                'difference': float(row.difference) if row.difference else None,
                'comments': row.comments
            }
            
            return jsonify(ok=True, entry=entry), 200
            
    except Exception as e:
        print(f"❌ Error loading IVL entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to load entry'), 500

@bp.put("/ivl/entry/<int:entry_id>")
def update_ivl_entry(entry_id):
    """Update an IVL entry"""
    try:
        data = request.json
        user_id = session.get('user_id', 1)
        
        with SessionLocal() as s, s.begin():
            # Calculate difference
            investment_amount = data.get('investment_amount')
            last_loan = data.get('last_loan')
            difference = None
            if investment_amount is not None and last_loan is not None:
                difference = float(last_loan) - float(investment_amount)
            
            s.execute(text("""
                UPDATE ivl_form_entries
                SET partner_name = :partner_name,
                    expected_profit_pct = :expected_profit_pct,
                    investment_amount = :investment_amount,
                    last_loan = :last_loan,
                    difference = :difference,
                    comments = :comments,
                    updated_by = :updated_by
                WHERE investment_id = :id
            """), {
                "id": entry_id,
                "partner_name": data.get('partner_name'),
                "expected_profit_pct": data.get('expected_profit_pct'),
                "investment_amount": investment_amount,
                "last_loan": last_loan,
                "difference": difference,
                "comments": data.get('comments'),
                "updated_by": user_id
            })
        
        return jsonify(ok=True, message='Entry updated successfully'), 200
        
    except Exception as e:
        print(f"❌ Error updating IVL entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to update entry'), 500

@bp.delete("/ivl/entry/<int:entry_id>")
def delete_ivl_entry(entry_id):
    """Delete an IVL entry"""
    try:
        with SessionLocal() as s, s.begin():
            result = s.execute(text("""
                DELETE FROM ivl_form_entries
                WHERE investment_id = :id
            """), {"id": entry_id})
            
            if result.rowcount == 0:
                return jsonify(ok=False, error='Entry not found'), 404
        
        return jsonify(ok=True, message='Entry deleted successfully'), 200
        
    except Exception as e:
        print(f"❌ Error deleting IVL entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to delete entry'), 500
@bp.post("/ivl/entry")
def create_ivl_entry():
    """
    Create a new IVL entry with created_by tracking
    """
    try:
        # Get username from session for created_by
        username = session.get('username') or session.get('email') or 'Unknown'

        # Get form data
        partner_name = (request.form.get('partner_name') or "").strip()
        expected_profit_pct = request.form.get('expected_profit_pct')
        investment_amount = request.form.get('investment_amount_l')
        last_loan = request.form.get('last_loan_l')
        comments = request.form.get('comments')

        # Handle file upload
        file = request.files.get('supporting_file')
        file_path = None
        if file and file.filename:
            file_path = _save(file, f'ivl-{int(time.time())}')

        # Validate required fields
        if not partner_name:
            return jsonify(ok=False, error='Partner name is required'), 400
        if not expected_profit_pct:
            return jsonify(ok=False, error='Expected profit percentage is required'), 400

        # Calculate difference
        inv_amt = float(investment_amount) if investment_amount else 0
        loan_amt = float(last_loan) if last_loan else 0
        difference = inv_amt - loan_amt

        # Build notes field with file info if present
        notes = None
        if file_path:
            notes = f"File: {file_path}"

        with SessionLocal() as s, s.begin():
            s.execute(text("""
                INSERT INTO ivl_form_entries (
                    partner_name,
                    expected_profit_pct,
                    investment_amount,
                    last_loan,
                    difference,
                    comments,
                    notes,
                    start_date,
                    created_by,
                    updated_by
                ) VALUES (
                    :partner_name,
                    :expected_profit_pct,
                    :investment_amount,
                    :last_loan,
                    :difference,
                    :comments,
                    :notes,
                    CURRENT_DATE,
                    :created_by,
                    :updated_by
                )
            """), {
                'partner_name': partner_name,
                'expected_profit_pct': expected_profit_pct,
                'investment_amount': investment_amount if investment_amount else None,
                'last_loan': last_loan if last_loan else None,
                'difference': difference,
                'comments': comments if comments else None,
                'notes': notes,
                'created_by': username,
                'updated_by': username
            })

        return jsonify(ok=True, message='Entry created successfully'), 201

    except Exception as e:
        print(f"❌ Error creating IVL entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to create entry'), 500
# ============================================
# MICRO EQUITY MATCHING - FILE UPLOAD
# ============================================
# ============================================
# BULK CSV UPLOAD FOR MATCHING EQUITY
# Add this endpoint to your equity.py file
# ============================================


# ============================================
# VALIDATION FUNCTIONS FOR ALL-OR-NOTHING CSV UPLOAD
# ============================================

def validate_matching_equity_record(row, row_num):
    """
    Validate a single matching equity CSV record
    Returns: (is_valid: bool, error_message: str or None, parsed_data: dict or None)
    """
    errors = []
    parsed_data = {}
    
    # Check required: Partner Name
    partner_name = (row.get('partner_name') or "").strip()
    if not partner_name:
        errors.append("Partner Name is required")
    else:
        parsed_data['partner_name'] = partner_name
    
    # Check required: Expected Profit %
    expected_profit_pct_str = (row.get('expected_profit_pct') or "").strip()
    if not expected_profit_pct_str:
        errors.append("Expected Profit % is required")
    else:
        try:
            expected_profit_pct = float(expected_profit_pct_str)
            if expected_profit_pct < 0 or expected_profit_pct > 100:
                errors.append(f"Expected Profit % must be between 0 and 100 (got {expected_profit_pct})")
            else:
                parsed_data['expected_profit_pct'] = expected_profit_pct
        except ValueError:
            errors.append(f"Expected Profit % must be a valid number (got '{expected_profit_pct_str}')")
    
    # Optional: Year
    year_str = (row.get('year') or "").strip()
    if year_str:
        try:
            year = int(year_str)
            if year < 1900 or year > 2100:
                errors.append(f"Year must be between 1900 and 2100 (got {year})")
            else:
                parsed_data['year'] = year
        except ValueError:
            errors.append(f"Year must be a valid integer (got '{year_str}')")
    else:
        parsed_data['year'] = None
    
    # Optional: Reported Shares
    reported_shares_str = (row.get('reported_shares') or "").strip()
    if reported_shares_str:
        try:
            reported_shares = float(reported_shares_str)
            if reported_shares < 0:
                errors.append(f"Reported Shares cannot be negative (got {reported_shares})")
            else:
                parsed_data['reported_shares'] = reported_shares
        except ValueError:
            errors.append(f"Reported Shares must be a valid number (got '{reported_shares_str}')")
    else:
        parsed_data['reported_shares'] = None
    
    # Optional: Share Capital Multiplied
    share_capital_str = (row.get('share_capital_multiplied') or "").strip()
    if share_capital_str:
        try:
            share_capital = float(share_capital_str)
            if share_capital < 0:
                errors.append(f"Share Capital cannot be negative (got {share_capital})")
            else:
                parsed_data['share_capital_multiplied'] = share_capital
        except ValueError:
            errors.append(f"Share Capital must be a valid number (got '{share_capital_str}')")
    else:
        parsed_data['share_capital_multiplied'] = None
    
    # Optional: Investment (L)
    investment_l_str = (row.get('investment_l') or "").strip()
    if investment_l_str:
        try:
            investment_l = float(investment_l_str)
            if investment_l < 0:
                errors.append(f"Investment (L) cannot be negative (got {investment_l})")
            else:
                parsed_data['investment_l'] = investment_l
        except ValueError:
            errors.append(f"Investment (L) must be a valid number (got '{investment_l_str}')")
    else:
        parsed_data['investment_l'] = None
    
    # Optional: Investment (USD)
    investment_usd_str = (row.get('investment_usd') or "").strip()
    if investment_usd_str:
        try:
            investment_usd = float(investment_usd_str)
            if investment_usd < 0:
                errors.append(f"Investment (USD) cannot be negative (got {investment_usd})")
            else:
                parsed_data['investment_usd'] = investment_usd
        except ValueError:
            errors.append(f"Investment (USD) must be a valid number (got '{investment_usd_str}')")
    else:
        parsed_data['investment_usd'] = None
    
    # Optional: Exchange Rate
    exchange_rate_str = (row.get('exchange_rate') or "").strip()
    if exchange_rate_str:
        try:
            exchange_rate = float(exchange_rate_str)
            if exchange_rate <= 0:
                errors.append(f"Exchange Rate must be positive (got {exchange_rate})")
            else:
                parsed_data['exchange_rate'] = exchange_rate
        except ValueError:
            errors.append(f"Exchange Rate must be a valid number (got '{exchange_rate_str}')")
    else:
        parsed_data['exchange_rate'] = None
    
    # Optional text fields
    parsed_data['bank_id'] = (row.get('bank_id') or "").strip() or None
    parsed_data['technician'] = (row.get('technician') or "").strip() or None
    parsed_data['proposal_state'] = (row.get('proposal_state') or "").strip() or None
    parsed_data['transaction_type'] = (row.get('transaction_type') or "").strip() or None
    parsed_data['business_category'] = (row.get('business_category') or "").strip() or None
    parsed_data['company_type'] = (row.get('company_type') or "").strip() or None
    parsed_data['community'] = (row.get('community') or "").strip() or None
    parsed_data['municipality'] = (row.get('municipality') or "").strip() or None
    parsed_data['state'] = (row.get('state') or "").strip() or None
    parsed_data['comments'] = (row.get('comments') or "").strip() or None
    parsed_data['start_date'] = (row.get('start_date') or "").strip() or None
    
    # Monthly distributions (default to 0)
    monthly_fields = ['january_l', 'february_l', 'march_l', 'april_l', 'may_l', 'june_l',
                      'july_l', 'august_l', 'september_l', 'october_l', 'november_l', 'december_l']
    
    for month_field in monthly_fields:
        month_str = (row.get(month_field) or "").strip()
        if month_str:
            try:
                month_val = float(month_str)
                if month_val < 0:
                    errors.append(f"{month_field} cannot be negative (got {month_val})")
                else:
                    parsed_data[month_field] = month_val
            except ValueError:
                errors.append(f"{month_field} must be a valid number (got '{month_str}')")
        else:
            parsed_data[month_field] = 0
    
    # Return validation result
    if errors:
        return False, '; '.join(errors), None
    return True, None, parsed_data


def parse_and_validate_matching_equity_csv(content):
    """
    Parse CSV and validate ALL records before inserting ANY
    Returns: (valid_records: list, validation_errors: list)
    """
    valid_records = []
    validation_errors = []
    
    try:
        csv_reader = csv.DictReader(StringIO(content))
        
        # Check for required headers
        required_headers = {'partner_name', 'expected_profit_pct'}
        csv_headers = set(csv_reader.fieldnames or [])
        
        missing_headers = required_headers - csv_headers
        if missing_headers:
            validation_errors.append({
                'row': 'Header',
                'partner_name': 'N/A',
                'error': f"Missing required columns: {', '.join(missing_headers)}"
            })
            return [], validation_errors
        
        # Validate each row
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (row 1 is header)
            # Skip completely empty rows
            if all(not str(v).strip() for v in row.values()):
                continue
            
            # Validate the record
            is_valid, error_msg, parsed_data = validate_matching_equity_record(row, row_num)
            
            if not is_valid:
                validation_errors.append({
                    'row': row_num,
                    'partner_name': (row.get('partner_name') or '').strip() or 'Unknown',
                    'error': error_msg
                })
            else:
                # Store validated and parsed record
                valid_records.append(parsed_data)
        
        # If no valid records found
        if not valid_records and not validation_errors:
            validation_errors.append({
                'row': 'File',
                'error': 'No valid data rows found in CSV file'
            })
    
    except csv.Error as e:
        validation_errors.append({
            'row': 'File',
            'error': f'CSV parsing error: {str(e)}'
        })
    except Exception as e:
        validation_errors.append({
            'row': 'File',
            'error': f'Unexpected error: {str(e)}'
        })
    
    return valid_records, validation_errors


@bp.post("/matching/bulk-upload")
def matching_bulk_upload():
    """
    Handle bulk CSV upload for matching equity entries
    ALL-OR-NOTHING: Validates all records before inserting any
    """
    try:
        if 'csv_file' not in request.files and 'file' not in request.files:
            return jsonify(ok=False, error='No file provided'), 400
        
        file = request.files.get("csv_file") or request.files.get("file")
        file = request.files.get('csv_file') or request.files.get('file')
        if file.filename == '':
            return jsonify(ok=False, error='No file selected'), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify(ok=False, error='File must be a CSV'), 400
        
        # Get user_id from session
        user_id = session.get('user_id', 1)
        username = session.get('username', 'System')
        print(f"📤 ALL-OR-NOTHING Matching Equity bulk upload initiated by: {username} (ID: {user_id})")
        
        # Read and decode CSV content
        content = file.stream.read().decode("UTF-8")
        
        # STEP 1: Validate ALL records BEFORE inserting ANY
        print("🔍 STEP 1: Validating all records...")
        valid_records, validation_errors = parse_and_validate_matching_equity_csv(content)
        
        # If there are ANY validation errors, reject the ENTIRE upload
        if validation_errors:
            print(f"❌ VALIDATION FAILED: {len(validation_errors)} errors found")
            print(f"   Valid records: {len(valid_records)}")
            print(f"   Invalid records: {len(validation_errors)}")
            
            return jsonify({
                'ok': False,
                'error': 'Validation failed',
                'message': f'Found {len(validation_errors)} validation error(s). No records were uploaded.',
                'validation_errors': validation_errors,
                'valid_count': len(valid_records),
                'invalid_count': len(validation_errors)
            }), 400
        
        # If we get here, ALL records are valid
        if not valid_records:
            return jsonify({
                'ok': False,
                'error': 'No valid records found in CSV file'
            }), 400
        
        print(f"✅ All {len(valid_records)} records validated successfully")
        
        # STEP 2: Insert ALL records in a single transaction
        print("💾 STEP 2: Inserting all records...")
        
        with SessionLocal() as s, s.begin():
            for idx, record in enumerate(valid_records, start=1):
                s.execute(text("""
                    INSERT INTO matching_equity_entries (
                        bank_id, partner_name, year, technician,
                        reported_shares, share_capital_multiplied, expected_profit_pct,
                        investment_l, investment_usd, exchange_rate,
                        proposal_state, transaction_type,
                        january_l, february_l, march_l, april_l, may_l, june_l,
                        july_l, august_l, september_l, october_l, november_l, december_l,
                        business_category, company_type, community, municipality, state,
                        comments, start_date, created_by, updated_by
                    ) VALUES (
                        :bank_id, :partner_name, :year, :technician,
                        :reported_shares, :share_capital, :expected_profit_pct,
                        :investment_l, :investment_usd, :exchange_rate,
                        :proposal_state, :transaction_type,
                        :january_l, :february_l, :march_l, :april_l, :may_l, :june_l,
                        :july_l, :august_l, :september_l, :october_l, :november_l, :december_l,
                        :business_category, :company_type, :community, :municipality, :state,
                        :comments, :start_date, :created_by, :updated_by
                    )
                """), {
                    "bank_id": record['bank_id'],
                    "partner_name": record['partner_name'],
                    "year": record['year'],
                    "technician": record['technician'],
                    "reported_shares": record['reported_shares'],
                    "share_capital": record['share_capital_multiplied'],
                    "expected_profit_pct": record['expected_profit_pct'],
                    "investment_l": record['investment_l'],
                    "investment_usd": record['investment_usd'],
                    "exchange_rate": record['exchange_rate'],
                    "proposal_state": record['proposal_state'],
                    "transaction_type": record['transaction_type'],
                    "january_l": record['january_l'],
                    "february_l": record['february_l'],
                    "march_l": record['march_l'],
                    "april_l": record['april_l'],
                    "may_l": record['may_l'],
                    "june_l": record['june_l'],
                    "july_l": record['july_l'],
                    "august_l": record['august_l'],
                    "september_l": record['september_l'],
                    "october_l": record['october_l'],
                    "november_l": record['november_l'],
                    "december_l": record['december_l'],
                    "business_category": record['business_category'],
                    "company_type": record['company_type'],
                    "community": record['community'],
                    "municipality": record['municipality'],
                    "state": record['state'],
                    "comments": record['comments'],
                    "start_date": record['start_date'],
                    "created_by": user_id,
                    "updated_by": user_id
                })
                print(f"  ✅ Inserted {idx}/{len(valid_records)}: {record['partner_name']}")
        
        print(f"🎉 SUCCESS: All {len(valid_records)} records uploaded by {username}")
        
        return jsonify({
            'ok': True,
            'message': f'Successfully uploaded all {len(valid_records)} records',
            'uploaded_count': len(valid_records),
            'uploaded_by': username
        }), 201
        
    except Exception as e:
        print(f"❌ Error in matching equity bulk upload: {e}")
        import traceback
        traceback.print_exc()
        # Don't expose SQL errors to users - show friendly message instead
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading your CSV file. Please check that your file follows the template format and all required fields are filled in correctly. If the problem persists, contact support.'
        }), 500

# ============================================
# PROFIT TRACKING BULK UPLOAD
# ============================================

def safe_float(value, default=None):
    """Safely convert a value to float, return default if empty/invalid"""
    if value is None:
        return default
    val_str = str(value).strip()
    if not val_str:
        return default
    try:
        return float(val_str)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=None):
    """Safely convert a value to int, return default if empty/invalid"""
    if value is None:
        return default
    val_str = str(value).strip()
    if not val_str:
        return default
    try:
        return int(val_str)
    except (ValueError, TypeError):
        return default

def safe_date(value):
    """Safely convert a value to date string, return None if empty"""
    if value is None:
        return None
    val_str = str(value).strip()
    return val_str if val_str else None

def validate_profit_record(row, row_num):
    """
    Validate a single profit CSV record
    Returns: (is_valid: bool, error_message: str or None, parsed_data: dict or None)
    """
    errors = []
    parsed_data = {}
    
    # Check required: Partner Name
    partner_name = (row.get('partner_name') or "").strip()
    if not partner_name:
        errors.append("Partner Name is required")
    else:
        parsed_data['partner_name'] = partner_name
    
    # Check required: Year
    year_str = (row.get('year') or "").strip()
    if not year_str:
        errors.append("Year is required")
    else:
        try:
            year = int(year_str)
            if year < 1900 or year > 2100:
                errors.append(f"Year must be between 1900 and 2100 (got {year})")
            else:
                parsed_data['year'] = year
        except ValueError:
            errors.append(f"Year must be a valid integer (got '{year_str}')")
    
    # Optional numeric fields with validation
    profit_l = safe_float(row.get('profit_l'))
    if profit_l is not None and profit_l < 0:
        errors.append(f"Profit (L) cannot be negative (got {profit_l})")
    parsed_data['profit_l'] = profit_l
    
    company_value_l = safe_float(row.get('company_value_l'))
    if company_value_l is not None and company_value_l < 0:
        errors.append(f"Company Value (L) cannot be negative (got {company_value_l})")
    parsed_data['company_value_l'] = company_value_l
    
    expected_profit_pct = safe_float(row.get('expected_profit_pct'))
    if expected_profit_pct is not None and (expected_profit_pct < 0 or expected_profit_pct > 100):
        errors.append(f"Expected Profit % must be between 0 and 100 (got {expected_profit_pct})")
    parsed_data['expected_profit_pct'] = expected_profit_pct
    
    investment_l = safe_float(row.get('investment_l'))
    if investment_l is not None and investment_l < 0:
        errors.append(f"Investment (L) cannot be negative (got {investment_l})")
    parsed_data['investment_l'] = investment_l
    
    investment_usd = safe_float(row.get('investment_usd'))
    if investment_usd is not None and investment_usd < 0:
        errors.append(f"Investment (USD) cannot be negative (got {investment_usd})")
    parsed_data['investment_usd'] = investment_usd
    
    exchange_rate = safe_float(row.get('exchange_rate'))
    if exchange_rate is not None and exchange_rate <= 0:
        errors.append(f"Exchange Rate must be positive (got {exchange_rate})")
    parsed_data['exchange_rate'] = exchange_rate
    
    # Optional text fields
    parsed_data['bank_id'] = (row.get('bank_id') or "").strip() or None
    parsed_data['technician'] = (row.get('technician') or "").strip() or None
    parsed_data['proposal_state'] = (row.get('proposal_state') or "").strip() or None
    parsed_data['transaction_type'] = (row.get('transaction_type') or "").strip() or None
    parsed_data['business_category'] = (row.get('business_category') or "").strip() or None
    parsed_data['company_type'] = (row.get('company_type') or "").strip() or None
    parsed_data['community'] = (row.get('community') or "").strip() or None
    parsed_data['municipality'] = (row.get('municipality') or "").strip() or None
    parsed_data['state'] = (row.get('state') or "").strip() or None
    parsed_data['comments'] = (row.get('comments') or "").strip() or None
    parsed_data['start_date'] = safe_date(row.get('start_date'))
    
    # Monthly distributions (default to 0)
    monthly_fields = ['january_l', 'february_l', 'march_l', 'april_l', 'may_l', 'june_l',
                      'july_l', 'august_l', 'september_l', 'october_l', 'november_l', 'december_l']
    
    for month_field in monthly_fields:
        month_val = safe_float(row.get(month_field), 0)
        if month_val < 0:
            errors.append(f"{month_field} cannot be negative (got {month_val})")
        parsed_data[month_field] = month_val
    
    # Return validation result
    if errors:
        return False, '; '.join(errors), None
    return True, None, parsed_data


def parse_and_validate_profit_csv(content):
    """
    Parse CSV and validate ALL records before inserting ANY
    Returns: (valid_records: list, validation_errors: list)
    """
    valid_records = []
    validation_errors = []
    
    try:
        csv_reader = csv.DictReader(StringIO(content))
        
        # Check for required headers
        required_headers = {'partner_name', 'year'}
        csv_headers = set(csv_reader.fieldnames or [])
        
        missing_headers = required_headers - csv_headers
        if missing_headers:
            validation_errors.append({
                'row': 'Header',
                'partner_name': 'N/A',
                'error': f"Missing required columns: {', '.join(missing_headers)}"
            })
            return [], validation_errors
        
        # Validate each row
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (row 1 is header)
            # Skip completely empty rows
            if all(not str(v).strip() for v in row.values()):
                continue
            
            # Validate the record
            is_valid, error_msg, parsed_data = validate_profit_record(row, row_num)
            
            if not is_valid:
                validation_errors.append({
                    'row': row_num,
                    'partner_name': (row.get('partner_name') or '').strip() or 'Unknown',
                    'error': error_msg
                })
            else:
                # Store validated and parsed record
                valid_records.append({
                    'bank_id': parsed_data['bank_id'],
                    'partner_name': parsed_data['partner_name'],
                    'year': parsed_data['year'],
                    'technician': parsed_data['technician'],
                    'profit_l': parsed_data['profit_l'],
                    'company_value_l': parsed_data['company_value_l'],
                    'expected_profit_pct': parsed_data['expected_profit_pct'],
                    'investment_l': parsed_data['investment_l'],
                    'investment_usd': parsed_data['investment_usd'],
                    'exchange_rate': parsed_data['exchange_rate'],
                    'proposal_state': parsed_data['proposal_state'],
                    'transaction_type': (row.get('transaction_type') or "").strip() or None,
                    'january_l': safe_float(row.get('january_l'), 0),
                    'february_l': safe_float(row.get('february_l'), 0),
                    'march_l': safe_float(row.get('march_l'), 0),
                    'april_l': safe_float(row.get('april_l'), 0),
                    'may_l': safe_float(row.get('may_l'), 0),
                    'june_l': safe_float(row.get('june_l'), 0),
                    'july_l': safe_float(row.get('july_l'), 0),
                    'august_l': safe_float(row.get('august_l'), 0),
                    'september_l': safe_float(row.get('september_l'), 0),
                    'october_l': safe_float(row.get('october_l'), 0),
                    'november_l': safe_float(row.get('november_l'), 0),
                    'december_l': safe_float(row.get('december_l'), 0),
                    'business_category': (row.get('business_category') or "").strip() or None,
                    'company_type': (row.get('company_type') or "").strip() or None,
                    'community': (row.get('community') or "").strip() or None,
                    'municipality': (row.get('municipality') or "").strip() or None,
                    'state': (row.get('state') or "").strip() or None,
                    'comments': (row.get('comments') or "").strip() or None,
                    'start_date': safe_date(row.get('start_date'))
                })
        
        # If no valid records found
        if not valid_records and not validation_errors:
            validation_errors.append({
                'row': 'File',
                'error': 'No valid data rows found in CSV file'
            })
    
    except csv.Error as e:
        validation_errors.append({
            'row': 'File',
            'error': f'CSV parsing error: {str(e)}'
        })
    except Exception as e:
        validation_errors.append({
            'row': 'File',
            'error': f'Unexpected error: {str(e)}'
        })
    
    return valid_records, validation_errors


@bp.post("/profit/bulk-upload")
def profit_bulk_upload():
    """
    Handle bulk CSV upload for profit entries
    ALL-OR-NOTHING: Validates all records before inserting any
    """
    try:
        if 'csv_file' not in request.files and 'file' not in request.files:
            return jsonify(ok=False, error='No file provided'), 400
        
        file = request.files.get("csv_file") or request.files.get("file")
        file = request.files.get('csv_file') or request.files.get('file')
        if file.filename == '':
            return jsonify(ok=False, error='No file selected'), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify(ok=False, error='File must be a CSV'), 400
        
        # Get user_id from session
        user_id = session.get('user_id', 1)
        username = session.get('username', 'System')
        print(f"📤 ALL-OR-NOTHING Profit bulk upload initiated by: {username} (ID: {user_id})")
        
        # Read and decode CSV content
        content = file.stream.read().decode("UTF-8")
        
        # STEP 1: Validate ALL records BEFORE inserting ANY
        print("🔍 STEP 1: Validating all records...")
        valid_records, validation_errors = parse_and_validate_profit_csv(content)
        
        # If there are ANY validation errors, reject the ENTIRE upload
        if validation_errors:
            print(f"❌ VALIDATION FAILED: {len(validation_errors)} errors found")
            print(f"   Valid records: {len(valid_records)}")
            print(f"   Invalid records: {len(validation_errors)}")
            
            return jsonify({
                'ok': False,
                'error': 'Validation failed',
                'message': f'Found {len(validation_errors)} validation error(s). No records were uploaded.',
                'validation_errors': validation_errors,
                'valid_count': len(valid_records),
                'invalid_count': len(validation_errors)
            }), 400
        
        # If we get here, ALL records are valid
        if not valid_records:
            return jsonify({
                'ok': False,
                'error': 'No valid records found in CSV file'
            }), 400
        
        print(f"✅ All {len(valid_records)} records validated successfully")
        
        # STEP 2: Insert ALL records in a single transaction
        print("💾 STEP 2: Inserting all records...")
        
        with SessionLocal() as s, s.begin():
            for idx, record in enumerate(valid_records, start=1):
                s.execute(text("""
                    INSERT INTO profit_form_entries (
                        bank_id, partner_name, year, technician,
                        profit_l, company_value_l, expected_profit_pct,
                        investment_l, investment_usd, exchange_rate,
                        proposal_state, transaction_type,
                        january_l, february_l, march_l, april_l, may_l, june_l,
                        july_l, august_l, september_l, october_l, november_l, december_l,
                        business_category, company_type, community, municipality, state,
                        comments, start_date, created_by, updated_by
                    ) VALUES (
                        :bank_id, :partner_name, :year, :technician,
                        :profit_l, :company_value_l, :expected_profit_pct,
                        :investment_l, :investment_usd, :exchange_rate,
                        :proposal_state, :transaction_type,
                        :january_l, :february_l, :march_l, :april_l, :may_l, :june_l,
                        :july_l, :august_l, :september_l, :october_l, :november_l, :december_l,
                        :business_category, :company_type, :community, :municipality, :state,
                        :comments, :start_date, :created_by, :updated_by
                    )
                """), {
                    "bank_id": record['bank_id'],
                    "partner_name": record['partner_name'],
                    "year": record['year'],
                    "technician": record['technician'],
                    "profit_l": record['profit_l'],
                    "company_value_l": record['company_value_l'],
                    "expected_profit_pct": record['expected_profit_pct'],
                    "investment_l": record['investment_l'],
                    "investment_usd": record['investment_usd'],
                    "exchange_rate": record['exchange_rate'],
                    "proposal_state": record['proposal_state'],
                    "transaction_type": record['transaction_type'],
                    "january_l": record['january_l'],
                    "february_l": record['february_l'],
                    "march_l": record['march_l'],
                    "april_l": record['april_l'],
                    "may_l": record['may_l'],
                    "june_l": record['june_l'],
                    "july_l": record['july_l'],
                    "august_l": record['august_l'],
                    "september_l": record['september_l'],
                    "october_l": record['october_l'],
                    "november_l": record['november_l'],
                    "december_l": record['december_l'],
                    "business_category": record['business_category'],
                    "company_type": record['company_type'],
                    "community": record['community'],
                    "municipality": record['municipality'],
                    "state": record['state'],
                    "comments": record['comments'],
                    "start_date": record['start_date'],
                    "created_by": user_id,
                    "updated_by": user_id
                })
                print(f"  ✅ Inserted {idx}/{len(valid_records)}: {record['partner_name']}")
        
        print(f"🎉 SUCCESS: All {len(valid_records)} records uploaded by {username}")
        
        return jsonify({
            'ok': True,
            'message': f'Successfully uploaded all {len(valid_records)} records',
            'uploaded_count': len(valid_records),
            'uploaded_by': username
        }), 201
        
    except Exception as e:
        print(f"❌ Error in profit bulk upload: {e}")
        import traceback
        traceback.print_exc()
        # Don't expose SQL errors to users - show friendly message instead
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading your CSV file. Please check that your file follows the template format and all required fields are filled in correctly. If the problem persists, contact support.'
        }), 500

# ============================================
# INVESTMENT VS LOAN BULK UPLOAD
# NEW FEATURE - Added Nov 15, 2025
# ============================================

def validate_investment_vs_loan_record(row, row_num):
    """
    Validate a single investment vs loan CSV record
    Returns: (is_valid: bool, error_message: str or None, parsed_data: dict or None)
    
    Expected CSV structure:
    - Partner Name (required)
    - Expected Profit % (optional)
    - Investment Amount (L.) (optional)
    - Last Loan (L.) (optional)
    - Comments (optional)
    """
    errors = []
    parsed_data = {}
    
    # Required: Partner Name
    partner_name = (row.get('partner_name') or "").strip()
    if not partner_name:
        errors.append("Partner Name is required")
    else:
        parsed_data['partner_name'] = partner_name
    
    # Optional: Expected Profit %
    expected_profit_pct = safe_float(row.get('expected_profit_pct'))
    if expected_profit_pct is not None and (expected_profit_pct < 0 or expected_profit_pct > 100):
        errors.append(f"Expected Profit % must be between 0 and 100 (got {expected_profit_pct})")
    parsed_data['expected_profit_pct'] = expected_profit_pct
    
    # Optional: Investment Amount (L.)
    investment_l = safe_float(row.get('investment_l'))
    if investment_l is not None and investment_l < 0:
        errors.append(f"Investment Amount (L.) cannot be negative (got {investment_l})")
    parsed_data['investment_l'] = investment_l
    
    # Optional: Last Loan (L.)
    last_loan_l = safe_float(row.get('last_loan_l'))
    if last_loan_l is not None and last_loan_l < 0:
        errors.append(f"Last Loan (L.) cannot be negative (got {last_loan_l})")
    parsed_data['last_loan_l'] = last_loan_l
    
    # Optional: Comments
    parsed_data['comments'] = (row.get('comments') or "").strip() or None
    
    # Return validation result
    if errors:
        return False, '; '.join(errors), None
    return True, None, parsed_data


def parse_and_validate_investment_vs_loan_csv(content):
    """
    Parse CSV and validate ALL records before inserting ANY
    Returns: (valid_records: list, validation_errors: list)
    
    Expected CSV columns (case-insensitive):
    - partner_name (or "Partner Name") - REQUIRED
    - expected_profit_pct (or "Expected Profit %") - optional
    - investment_l (or "Investment Amount (L.)") - optional
    - last_loan_l (or "Last Loan (L.)") - optional
    - comments (or "Comments") - optional
    """
    valid_records = []
    validation_errors = []
    
    try:
        csv_reader = csv.DictReader(StringIO(content))
        
        # First, check for columns that indicate this is the WRONG CSV file
        wrong_file_indicators = ['year', 'reported shares', 'share capital', 'technician', 
                                  'business category', 'jan (l)', 'feb (l)', 'profit (l.)', 
                                  'transaction type', 'proposal state', 'municipality', 'state']
        
        if csv_reader.fieldnames:
            lower_headers = [h.lower().strip() for h in csv_reader.fieldnames]
            
            # Check if this looks like a Matching Equity or Profit CSV
            found_wrong_columns = [col for col in wrong_file_indicators if col in lower_headers]
            
            if found_wrong_columns:
                validation_errors.append({
                    'row': 'Header',
                    'partner_name': 'N/A',
                    'error': 'Upload failed. The CSV file format does not match the Investment vs Loan template. Please download the correct template, ensure your columns are formatted properly, and try again.'
                })
                return [], validation_errors
        
        # Map CSV headers to our expected field names (case-insensitive)
        header_mapping = {}
        for header in (csv_reader.fieldnames or []):
            lower_header = header.lower().strip()
            if 'partner name' in lower_header or lower_header == 'partner_name':
                header_mapping['partner_name'] = header
            elif 'expected profit' in lower_header or lower_header == 'expected_profit_pct':
                header_mapping['expected_profit_pct'] = header
            elif 'investment amount' in lower_header or lower_header == 'investment_l':
                header_mapping['investment_l'] = header
            elif 'last loan' in lower_header or lower_header == 'last_loan_l':
                header_mapping['last_loan_l'] = header
            elif lower_header == 'comments':
                header_mapping['comments'] = header
        
        # Check for required header
        if 'partner_name' not in header_mapping:
            validation_errors.append({
                'row': 'Header',
                'partner_name': 'N/A',
                'error': 'Missing required column: Partner Name (or partner_name)'
            })
            return [], validation_errors
        
        # Validate each row
        for row_num, raw_row in enumerate(csv_reader, start=2):  # Start at 2 (row 1 is header)
            # Skip completely empty rows
            if all(not str(v).strip() for v in raw_row.values()):
                continue
            
            # Map the row data to our expected field names
            row = {}
            for field_name, csv_header in header_mapping.items():
                row[field_name] = raw_row.get(csv_header, '')
            
            # Validate the record
            is_valid, error_msg, parsed_data = validate_investment_vs_loan_record(row, row_num)
            
            if not is_valid:
                validation_errors.append({
                    'row': row_num,
                    'partner_name': (row.get('partner_name') or '').strip() or 'Unknown',
                    'error': error_msg
                })
            else:
                # Store validated and parsed record
                valid_records.append(parsed_data)
        
        # If no valid records found
        if not valid_records and not validation_errors:
            validation_errors.append({
                'row': 'File',
                'error': 'No valid data rows found in CSV file'
            })
    
    except csv.Error as e:
        validation_errors.append({
            'row': 'File',
            'error': f'CSV parsing error: {str(e)}'
        })
    except Exception as e:
        validation_errors.append({
            'row': 'File',
            'error': f'Unexpected error: {str(e)}'
        })
    
    return valid_records, validation_errors


@bp.post("/ivl/bulk-upload")
def investment_loan_bulk_upload():
    """
    Handle bulk CSV upload for investment vs loan entries
    ALL-OR-NOTHING: Validates all records before inserting any
    
    Expected CSV structure:
    - Partner Name (required)
    - Expected Profit % (optional)
    - Investment Amount (L.) (optional)
    - Last Loan (L.) (optional)
    - Comments (optional)
    """
    try:
        if 'csv_file' not in request.files:
            return jsonify(ok=False, error='No file provided'), 400
        
        file = request.files['csv_file']
        
        if file.filename == '':
            return jsonify(ok=False, error='No file selected'), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify(ok=False, error='File must be a CSV'), 400
        
        # Get user_id from session
        user_id = session.get('user_id', 1)
        username = session.get('username', 'System')
        print(f"📤 ALL-OR-NOTHING Investment vs Loan bulk upload initiated by: {username} (ID: {user_id})")
        
        # Read and decode CSV content
        content = file.stream.read().decode("UTF-8")
        
        # STEP 1: Validate ALL records BEFORE inserting ANY
        print("🔍 STEP 1: Validating all records...")
        valid_records, validation_errors = parse_and_validate_investment_vs_loan_csv(content)
        
        # If there are ANY validation errors, reject the ENTIRE upload
        if validation_errors:
            print(f"❌ VALIDATION FAILED: {len(validation_errors)} errors found")
            print(f"   Valid records: {len(valid_records)}")
            print(f"   Invalid records: {len(validation_errors)}")
            
            return jsonify({
                'ok': False,
                'error': 'Validation failed',
                'message': f'Found {len(validation_errors)} validation error(s). No records were uploaded.',
                'validation_errors': validation_errors,
                'valid_count': len(valid_records),
                'invalid_count': len(validation_errors)
            }), 400
        
        # If we get here, ALL records are valid
        if not valid_records:
            return jsonify({
                'ok': False,
                'error': 'No valid records found in CSV file'
            }), 400
        
        print(f"✅ All {len(valid_records)} records validated successfully")
        
        # STEP 2: Insert ALL records in a single transaction
        print("💾 STEP 2: Inserting all records...")
        
        with SessionLocal() as s, s.begin():
            for idx, record in enumerate(valid_records, start=1):
                s.execute(text("""
                    INSERT INTO ivl_form_entries (
                        partner_name, expected_profit_pct, investment_amount, last_loan,
                        comments, created_by, updated_by
                    ) VALUES (
                        :partner_name, :expected_profit_pct, :investment_amount, :last_loan,
                        :comments, :created_by, :updated_by
                    )
                """), {
                    "partner_name": record['partner_name'],
                    "expected_profit_pct": record['expected_profit_pct'],
                    "investment_amount": record['investment_l'],
                    "last_loan": record['last_loan_l'],
                    "comments": record['comments'],
                    "created_by": user_id,
                    "updated_by": user_id
                })
                print(f"  ✅ Inserted {idx}/{len(valid_records)}: {record['partner_name']}")
        
        print(f"🎉 SUCCESS: All {len(valid_records)} records uploaded by {username}")
        
        return jsonify({
            'ok': True,
            'message': f'Successfully uploaded all {len(valid_records)} records',
            'uploaded_count': len(valid_records),
            'uploaded_by': username
        }), 201
        
    except Exception as e:
        print(f"❌ Error in investment vs loan bulk upload: {e}")
        import traceback
        traceback.print_exc()
        # Don't expose SQL errors to users - show friendly message instead
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading your CSV file. Please check that your file follows the template format and all required fields are filled in correctly. If the problem persists, contact support.'
        }), 500

# ============================================
# MATCHING EQUITY ENDPOINTS
# ============================================

@bp.post("/matching/manual-entry")
def matching_manual_entry():
    """Handle Matching Equity Form manual entry submission"""
    # Check authentication
    user_id, role, auth_error = require_auth()
    if auth_error:
        return auth_error
    
    # Get form data (sent as FormData, not JSON)
    b = request.form
    f = request.files.get("supporting_file")
    
    # Save file if present and store filename in notes
    notes = None
    if f:
        file_path = _save(f, f'matching-{int(time.time())}')
        # Store the actual saved filename (not the original filename)
        saved_filename = file_path.split('/')[-1] if file_path else f.filename
        notes = f"File: {saved_filename}"
    
    try:
        with SessionLocal() as s, s.begin():
            s.execute(text("""
                INSERT INTO matching_equity_entries
                (bank_id, partner_name, year, technician, reported_shares, share_capital_multiplied,
                 expected_profit_pct, investment_l, investment_usd, exchange_rate,
                 proposal_state, transaction_type, business_category, company_type,
                 community, municipality, state, comments, notes, start_date,
                 january_l, february_l, march_l, april_l, may_l, june_l,
                 july_l, august_l, september_l, october_l, november_l, december_l,
                 created_by, updated_by)
                VALUES (:bank_id, :partner_name, :year, :technician, :reported_shares, :share_capital_multiplied,
                        :expected_profit_pct, :investment_l, :investment_usd, :exchange_rate,
                        :proposal_state, :transaction_type, :business_category, :company_type,
                        :community, :municipality, :state, :comments, :notes, :start_date,
                        :january_l, :february_l, :march_l, :april_l, :may_l, :june_l,
                        :july_l, :august_l, :september_l, :october_l, :november_l, :december_l,
                        :user_id, :user_id)
            """), {
                "bank_id": (b.get("bank_id") or "").strip() or None,
                "partner_name": (b.get("partner_name") or "").strip(),
                "year": int(b.get("year")) if b.get("year") else None,
                "technician": (b.get("technician") or "").strip() or None,
                "reported_shares": float(b.get("reported_shares")) if b.get("reported_shares") else None,
                "share_capital_multiplied": float(b.get("share_capital_multiplied")) if b.get("share_capital_multiplied") else None,
                "expected_profit_pct": float(b.get("expected_profit_pct")) if b.get("expected_profit_pct") else None,
                "investment_l": float(b.get("investment_l")) if b.get("investment_l") else None,
                "investment_usd": float(b.get("investment_usd")) if b.get("investment_usd") else None,
                "exchange_rate": float(b.get("exchange_rate")) if b.get("exchange_rate") else None,
                "proposal_state": (b.get("proposal_state") or "").strip() or None,
                "transaction_type": (b.get("transaction_type") or "").strip() or None,
                "business_category": (b.get("business_category") or "").strip() or None,
                "company_type": (b.get("company_type") or "").strip() or None,
                "community": (b.get("community") or "").strip() or None,
                "municipality": (b.get("municipality") or "").strip() or None,
                "state": (b.get("state") or "").strip() or None,
                "comments": (b.get("comments") or "").strip() or None,
                "notes": notes,
                "start_date": b.get("start_date") or None,
                "january_l": float(b.get("january_l", 0)),
                "february_l": float(b.get("february_l", 0)),
                "march_l": float(b.get("march_l", 0)),
                "april_l": float(b.get("april_l", 0)),
                "may_l": float(b.get("may_l", 0)),
                "june_l": float(b.get("june_l", 0)),
                "july_l": float(b.get("july_l", 0)),
                "august_l": float(b.get("august_l", 0)),
                "september_l": float(b.get("september_l", 0)),
                "october_l": float(b.get("october_l", 0)),
                "november_l": float(b.get("november_l", 0)),
                "december_l": float(b.get("december_l", 0)),
                "user_id": user_id
            })
            
        return jsonify(ok=True, message="Matching equity entry saved successfully"), 201
        
    except Exception as e:
        print(f"❌ Error in matching manual entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'ok': False,
            'error': 'Submission failed',
            'message': 'An error occurred while saving the matching equity entry.'
        }), 500

@bp.get("/matching/entries")
def get_matching_entries():
    """Get all micro equity matching entries with audit data"""
    try:
        with SessionLocal() as s:
            rows = s.execute(text("""
                SELECT 
                    m.investment_id, m.bank_id, m.partner_name, m.year, m.technician,
                    m.reported_shares, m.share_capital_multiplied, m.expected_profit_pct,
                    m.investment_l, m.investment_usd, m.exchange_rate,
                    m.proposal_state, m.transaction_type,
                    m.business_category, m.company_type, m.community, m.municipality, m.state,
                    m.january_l, m.february_l, m.march_l, m.april_l, m.may_l, m.june_l,
                    m.july_l, m.august_l, m.september_l, m.october_l, m.november_l, m.december_l,
                    m.comments, m.notes, m.start_date, 
                    m.created_by, m.created_at, m.updated_by, m.updated_at,
                    u1.username as created_by_name,
                    u2.username as updated_by_name
                FROM matching_equity_entries m
                LEFT JOIN users u1 ON m.created_by = u1.user_id
                LEFT JOIN users u2 ON m.updated_by = u2.user_id
                ORDER BY m.created_at DESC
            """)).fetchall()
            
            entries = []
            for row in rows:
                entries.append({
                    'investment_id': row.investment_id,
                    'bank_id': row.bank_id,
                    'partner_name': row.partner_name,
                    'year': row.year,
                    'technician': row.technician,
                    'reported_shares': float(row.reported_shares) if row.reported_shares else None,
                    'share_capital_multiplied': float(row.share_capital_multiplied) if row.share_capital_multiplied else None,
                    'expected_profit_pct': float(row.expected_profit_pct) if row.expected_profit_pct else None,
                    'investment_l': float(row.investment_l) if row.investment_l else None,
                    'investment_usd': float(row.investment_usd) if row.investment_usd else None,
                    'exchange_rate': float(row.exchange_rate) if row.exchange_rate else None,
                    'proposal_state': row.proposal_state,
                    'transaction_type': row.transaction_type,
                    'business_category': row.business_category,
                    'company_type': row.company_type,
                    'community': row.community,
                    'municipality': row.municipality,
                    'state': row.state,
                    'january_l': float(row.january_l) if row.january_l else 0,
                    'february_l': float(row.february_l) if row.february_l else 0,
                    'march_l': float(row.march_l) if row.march_l else 0,
                    'april_l': float(row.april_l) if row.april_l else 0,
                    'may_l': float(row.may_l) if row.may_l else 0,
                    'june_l': float(row.june_l) if row.june_l else 0,
                    'july_l': float(row.july_l) if row.july_l else 0,
                    'august_l': float(row.august_l) if row.august_l else 0,
                    'september_l': float(row.september_l) if row.september_l else 0,
                    'october_l': float(row.october_l) if row.october_l else 0,
                    'november_l': float(row.november_l) if row.november_l else 0,
                    'december_l': float(row.december_l) if row.december_l else 0,
                    'comments': row.comments,
                    'notes': row.notes,
                    'start_date': row.start_date.isoformat() if row.start_date else None,
                    'created_by': row.created_by_name if row.created_by_name else 'System',
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_by': row.updated_by_name if row.updated_by_name else 'System',
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None
                })
            
            return jsonify(ok=True, entries=entries), 200
            
    except Exception as e:
        print(f"❌ Error loading matching entries: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to load entries'), 500

@bp.get("/matching/summary")
def get_matching_summary():
    """Get summary statistics for matching entries"""
    try:
        with SessionLocal() as s:
            row = s.execute(text("""
                SELECT 
                    COALESCE(SUM(investment_l), 0) as total_investment_l,
                    COALESCE(SUM(investment_usd), 0) as total_investment_usd,
                    COALESCE(SUM(reported_shares), 0) as total_reported_shares,
                    COUNT(*) as total_entries
                FROM matching_equity_entries
            """)).fetchone()
            
            summary = {
                'total_investment_l': float(row.total_investment_l) if row.total_investment_l else 0,
                'total_investment_usd': float(row.total_investment_usd) if row.total_investment_usd else 0,
                'total_reported_shares': float(row.total_reported_shares) if row.total_reported_shares else 0,
                'total_entries': row.total_entries
            }
            
            return jsonify(ok=True, summary=summary), 200
            
    except Exception as e:
        print(f"❌ Error loading matching summary: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to load summary'), 500

@bp.get("/matching/entry/<int:investment_id>")
def get_matching_entry(investment_id):
    """Get a single matching entry by ID"""
    try:
        with SessionLocal() as s:
            row = s.execute(text("""
                SELECT 
                    investment_id, bank_id, partner_name, year, technician,
                    reported_shares, share_capital_multiplied, expected_profit_pct,
                    investment_l, investment_usd, exchange_rate,
                    proposal_state, transaction_type,
                    business_category, company_type, community, municipality, state,
                    january_l, february_l, march_l, april_l, may_l, june_l,
                    july_l, august_l, september_l, october_l, november_l, december_l,
                    comments, start_date
                FROM matching_equity_entries
                WHERE investment_id = :id
            """), {"id": investment_id}).fetchone()
            
            if not row:
                return jsonify(ok=False, error='Entry not found'), 404
            
            entry = {
                'investment_id': row.investment_id,
                'bank_id': row.bank_id,
                'partner_name': row.partner_name,
                'year': row.year,
                'technician': row.technician,
                'reported_shares': float(row.reported_shares) if row.reported_shares else None,
                'share_capital_multiplied': float(row.share_capital_multiplied) if row.share_capital_multiplied else None,
                'expected_profit_pct': float(row.expected_profit_pct) if row.expected_profit_pct else None,
                'investment_l': float(row.investment_l) if row.investment_l else None,
                'investment_usd': float(row.investment_usd) if row.investment_usd else None,
                'exchange_rate': float(row.exchange_rate) if row.exchange_rate else None,
                'proposal_state': row.proposal_state,
                'transaction_type': row.transaction_type,
                'business_category': row.business_category,
                'company_type': row.company_type,
                'community': row.community,
                'municipality': row.municipality,
                'state': row.state,
                'january_l': float(row.january_l) if row.january_l else 0,
                'february_l': float(row.february_l) if row.february_l else 0,
                'march_l': float(row.march_l) if row.march_l else 0,
                'april_l': float(row.april_l) if row.april_l else 0,
                'may_l': float(row.may_l) if row.may_l else 0,
                'june_l': float(row.june_l) if row.june_l else 0,
                'july_l': float(row.july_l) if row.july_l else 0,
                'august_l': float(row.august_l) if row.august_l else 0,
                'september_l': float(row.september_l) if row.september_l else 0,
                'october_l': float(row.october_l) if row.october_l else 0,
                'november_l': float(row.november_l) if row.november_l else 0,
                'december_l': float(row.december_l) if row.december_l else 0,
                'comments': row.comments,
                'start_date': row.start_date.isoformat() if row.start_date else None
            }
            
            return jsonify(ok=True, entry=entry), 200
            
    except Exception as e:
        print(f"❌ Error loading matching entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to load entry'), 500

@bp.put("/matching/entry/<int:investment_id>")
def update_matching_entry(investment_id):
    """Update a matching entry"""
    try:
        data = request.json
        user_id = session.get('user_id', 1)
        
        with SessionLocal() as s, s.begin():
            s.execute(text("""
                UPDATE matching_equity_entries
                SET bank_id = :bank_id,
                    partner_name = :partner_name,
                    year = :year,
                    technician = :technician,
                    reported_shares = :reported_shares,
                    share_capital_multiplied = :share_capital_multiplied,
                    expected_profit_pct = :expected_profit_pct,
                    investment_l = :investment_l,
                    investment_usd = :investment_usd,
                    exchange_rate = :exchange_rate,
                    proposal_state = :proposal_state,
                    transaction_type = :transaction_type,
                    business_category = :business_category,
                    company_type = :company_type,
                    community = :community,
                    municipality = :municipality,
                    state = :state,
                    january_l = :january_l,
                    february_l = :february_l,
                    march_l = :march_l,
                    april_l = :april_l,
                    may_l = :may_l,
                    june_l = :june_l,
                    july_l = :july_l,
                    august_l = :august_l,
                    september_l = :september_l,
                    october_l = :october_l,
                    november_l = :november_l,
                    december_l = :december_l,
                    comments = :comments,
                    updated_by = :updated_by
                WHERE investment_id = :investment_id
            """), {
                "investment_id": investment_id,
                "bank_id": data.get("bank_id"),
                "partner_name": data.get("partner_name"),
                "year": data.get("year"),
                "technician": data.get("technician"),
                "reported_shares": data.get("reported_shares"),
                "share_capital_multiplied": data.get("share_capital_multiplied"),
                "expected_profit_pct": data.get("expected_profit_pct"),
                "investment_l": data.get("investment_l"),
                "investment_usd": data.get("investment_usd"),
                "exchange_rate": data.get("exchange_rate"),
                "proposal_state": data.get("proposal_state"),
                "transaction_type": data.get("transaction_type"),
                "business_category": data.get("business_category"),
                "company_type": data.get("company_type"),
                "community": data.get("community"),
                "municipality": data.get("municipality"),
                "state": data.get("state"),
                "january_l": data.get("january_l", 0),
                "february_l": data.get("february_l", 0),
                "march_l": data.get("march_l", 0),
                "april_l": data.get("april_l", 0),
                "may_l": data.get("may_l", 0),
                "june_l": data.get("june_l", 0),
                "july_l": data.get("july_l", 0),
                "august_l": data.get("august_l", 0),
                "september_l": data.get("september_l", 0),
                "october_l": data.get("october_l", 0),
                "november_l": data.get("november_l", 0),
                "december_l": data.get("december_l", 0),
                "comments": data.get("comments"),
                "updated_by": user_id
            })
        
        return jsonify(ok=True, message='Entry updated successfully'), 200
        
    except Exception as e:
        print(f"❌ Error updating matching entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to update entry'), 500

@bp.delete("/matching/entry/<int:investment_id>")
def delete_matching_entry(investment_id):
    """Delete a matching entry"""
    try:
        with SessionLocal() as s, s.begin():
            result = s.execute(text("""
                DELETE FROM matching_equity_entries
                WHERE investment_id = :id
            """), {"id": investment_id})
            
            if result.rowcount == 0:
                return jsonify(ok=False, error='Entry not found'), 404
        
        return jsonify(ok=True, message='Entry deleted successfully'), 200
        
    except Exception as e:
        print(f"❌ Error deleting matching entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to delete entry'), 500

# ============================================
# PROFIT ENDPOINTS
# ============================================

@bp.post("/profit/entry")
def profit_entry():
    """Handle Profit Form manual entry submission"""
    # Check authentication
    user_id, role, auth_error = require_auth()
    if auth_error:
        return auth_error
    
    data = request.get_json()
    
    try:
        with SessionLocal() as s, s.begin():
            s.execute(text("""
                INSERT INTO profit_form_entries
                (bank_id, partner_name, year, technician, profit_l, company_value_l,
                 expected_profit_pct, investment_l, investment_usd, exchange_rate,
                 proposal_state, transaction_type, business_category, company_type,
                 community, municipality, state, comments, start_date,
                 january_l, february_l, march_l, april_l, may_l, june_l,
                 july_l, august_l, september_l, october_l, november_l, december_l,
                 created_by, updated_by)
                VALUES (:bank_id, :partner_name, :year, :technician, :profit_l, :company_value_l,
                        :expected_profit_pct, :investment_l, :investment_usd, :exchange_rate,
                        :proposal_state, :transaction_type, :business_category, :company_type,
                        :community, :municipality, :state, :comments, :start_date,
                        :january_l, :february_l, :march_l, :april_l, :may_l, :june_l,
                        :july_l, :august_l, :september_l, :october_l, :november_l, :december_l,
                        :user_id, :user_id)
            """), {
                "bank_id": data.get("bank_id"),
                "partner_name": data.get("partner_name"),
                "year": data.get("year"),
                "technician": data.get("technician"),
                "profit_l": data.get("profit_l"),
                "company_value_l": data.get("company_value_l"),
                "expected_profit_pct": data.get("expected_profit_pct"),
                "investment_l": data.get("investment_l"),
                "investment_usd": data.get("investment_usd"),
                "exchange_rate": data.get("exchange_rate"),
                "proposal_state": data.get("proposal_state"),
                "transaction_type": data.get("transaction_type"),
                "business_category": data.get("business_category"),
                "company_type": data.get("company_type"),
                "community": data.get("community"),
                "municipality": data.get("municipality"),
                "state": data.get("state"),
                "comments": data.get("comments"),
                "start_date": data.get("start_date"),
                "january_l": data.get("january_l", 0),
                "february_l": data.get("february_l", 0),
                "march_l": data.get("march_l", 0),
                "april_l": data.get("april_l", 0),
                "may_l": data.get("may_l", 0),
                "june_l": data.get("june_l", 0),
                "july_l": data.get("july_l", 0),
                "august_l": data.get("august_l", 0),
                "september_l": data.get("september_l", 0),
                "october_l": data.get("october_l", 0),
                "november_l": data.get("november_l", 0),
                "december_l": data.get("december_l", 0),
                "user_id": user_id
            })
            
        return jsonify(ok=True, message="Profit entry saved successfully"), 201
        
    except Exception as e:
        print(f"❌ Error in profit entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'ok': False,
            'error': 'Submission failed',
            'message': 'An error occurred while saving the profit entry.'
        }), 500

@bp.get("/profit/entries")
def get_profit_entries():
    """Get all profit entries with audit data"""
    try:
        with SessionLocal() as s:
            rows = s.execute(text("""
                SELECT 
                    p.investment_id, p.bank_id, p.partner_name, p.year, p.technician,
                    p.profit_l, p.company_value_l, p.expected_profit_pct,
                    p.investment_l, p.investment_usd, p.exchange_rate,
                    p.proposal_state, p.transaction_type,
                    p.january_l, p.february_l, p.march_l, p.april_l, p.may_l, p.june_l,
                    p.july_l, p.august_l, p.september_l, p.october_l, p.november_l, p.december_l,
                    p.business_category, p.company_type, p.community, p.municipality, p.state,
                    p.comments, p.start_date, p.created_by, p.created_at, p.updated_at, p.updated_by,
                    u1.username as created_by_name,
                    u2.username as updated_by_name
                FROM profit_form_entries p
                LEFT JOIN users u1 ON p.created_by = u1.user_id
                LEFT JOIN users u2 ON p.updated_by = u2.user_id
                ORDER BY p.investment_id DESC
            """)).fetchall()
            
            entries = []
            for row in rows:
                entries.append({
                    'investment_id': row.investment_id,
                    'bank_id': row.bank_id,
                    'partner_name': row.partner_name,
                    'year': row.year,
                    'technician': row.technician,
                    'profit_l': float(row.profit_l) if row.profit_l else None,
                    'company_value_l': float(row.company_value_l) if row.company_value_l else None,
                    'expected_profit_pct': float(row.expected_profit_pct) if row.expected_profit_pct else None,
                    'investment_l': float(row.investment_l) if row.investment_l else None,
                    'investment_usd': float(row.investment_usd) if row.investment_usd else None,
                    'exchange_rate': float(row.exchange_rate) if row.exchange_rate else None,
                    'proposal_state': row.proposal_state,
                    'transaction_type': row.transaction_type,
                    'january_l': float(row.january_l) if row.january_l else 0,
                    'february_l': float(row.february_l) if row.february_l else 0,
                    'march_l': float(row.march_l) if row.march_l else 0,
                    'april_l': float(row.april_l) if row.april_l else 0,
                    'may_l': float(row.may_l) if row.may_l else 0,
                    'june_l': float(row.june_l) if row.june_l else 0,
                    'july_l': float(row.july_l) if row.july_l else 0,
                    'august_l': float(row.august_l) if row.august_l else 0,
                    'september_l': float(row.september_l) if row.september_l else 0,
                    'october_l': float(row.october_l) if row.october_l else 0,
                    'november_l': float(row.november_l) if row.november_l else 0,
                    'december_l': float(row.december_l) if row.december_l else 0,
                    'business_category': row.business_category,
                    'company_type': row.company_type,
                    'community': row.community,
                    'municipality': row.municipality,
                    'state': row.state,
                    'comments': row.comments,
                    'start_date': row.start_date.isoformat() if row.start_date else None,
                    'created_by': row.created_by_name if row.created_by_name else 'System',
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_by': row.updated_by_name if row.updated_by_name else 'System',
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None
                })
            
            return jsonify(ok=True, entries=entries), 200
            
    except Exception as e:
        print(f"❌ Error loading profit entries: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to load entries'), 500

@bp.get("/profit/summary")
def get_profit_summary():
    """Get summary statistics for profit entries"""
    try:
        with SessionLocal() as s:
            row = s.execute(text("""
                SELECT 
                    COUNT(*) as total_entries,
                    COALESCE(SUM(investment_l), 0) as total_investment_l,
                    COALESCE(SUM(investment_usd), 0) as total_investment_usd,
                    COALESCE(AVG(expected_profit_pct), 0) as avg_expected_profit
                FROM profit_form_entries
            """)).fetchone()
            
            summary = {
                'total_entries': row.total_entries,
                'total_investment_l': float(row.total_investment_l),
                'total_investment_usd': float(row.total_investment_usd),
                'avg_expected_profit': float(row.avg_expected_profit)
            }
            
            return jsonify(ok=True, summary=summary), 200
            
    except Exception as e:
        print(f"❌ Error loading profit summary: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to load summary'), 500

@bp.get("/profit/entry/<int:investment_id>")
def get_profit_entry(investment_id):
    """Get a single profit entry by ID"""
    try:
        with SessionLocal() as s:
            row = s.execute(text("""
                SELECT 
                    investment_id, bank_id, partner_name, year, technician,
                    profit_l, company_value_l, expected_profit_pct,
                    investment_l, investment_usd, exchange_rate,
                    proposal_state, transaction_type,
                    january_l, february_l, march_l, april_l, may_l, june_l,
                    july_l, august_l, september_l, october_l, november_l, december_l,
                    business_category, company_type, community, municipality, state,
                    comments, start_date
                FROM profit_form_entries
                WHERE investment_id = :id
            """), {"id": investment_id}).fetchone()
            
            if not row:
                return jsonify(ok=False, error='Entry not found'), 404
            
            entry = {
                'investment_id': row.investment_id,
                'bank_id': row.bank_id,
                'partner_name': row.partner_name,
                'year': row.year,
                'technician': row.technician,
                'profit_l': float(row.profit_l) if row.profit_l else None,
                'company_value_l': float(row.company_value_l) if row.company_value_l else None,
                'expected_profit_pct': float(row.expected_profit_pct) if row.expected_profit_pct else None,
                'investment_l': float(row.investment_l) if row.investment_l else None,
                'investment_usd': float(row.investment_usd) if row.investment_usd else None,
                'exchange_rate': float(row.exchange_rate) if row.exchange_rate else None,
                'proposal_state': row.proposal_state,
                'transaction_type': row.transaction_type,
                'january_l': float(row.january_l) if row.january_l else 0,
                'february_l': float(row.february_l) if row.february_l else 0,
                'march_l': float(row.march_l) if row.march_l else 0,
                'april_l': float(row.april_l) if row.april_l else 0,
                'may_l': float(row.may_l) if row.may_l else 0,
                'june_l': float(row.june_l) if row.june_l else 0,
                'july_l': float(row.july_l) if row.july_l else 0,
                'august_l': float(row.august_l) if row.august_l else 0,
                'september_l': float(row.september_l) if row.september_l else 0,
                'october_l': float(row.october_l) if row.october_l else 0,
                'november_l': float(row.november_l) if row.november_l else 0,
                'december_l': float(row.december_l) if row.december_l else 0,
                'business_category': row.business_category,
                'company_type': row.company_type,
                'community': row.community,
                'municipality': row.municipality,
                'state': row.state,
                'comments': row.comments,
                'start_date': row.start_date.isoformat() if row.start_date else None
            }
            
            return jsonify(ok=True, entry=entry), 200
            
    except Exception as e:
        print(f"❌ Error loading profit entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to load entry'), 500

@bp.put("/profit/entry/<int:investment_id>")
def update_profit_entry(investment_id):
    """Update a profit entry"""
    try:
        data = request.json
        user_id = session.get('user_id', 1)
        
        with SessionLocal() as s, s.begin():
            s.execute(text("""
                UPDATE profit_form_entries
                SET bank_id = :bank_id,
                    partner_name = :partner_name,
                    year = :year,
                    technician = :technician,
                    profit_l = :profit_l,
                    company_value_l = :company_value_l,
                    expected_profit_pct = :expected_profit_pct,
                    investment_l = :investment_l,
                    investment_usd = :investment_usd,
                    exchange_rate = :exchange_rate,
                    proposal_state = :proposal_state,
                    transaction_type = :transaction_type,
                    january_l = :january_l,
                    february_l = :february_l,
                    march_l = :march_l,
                    april_l = :april_l,
                    may_l = :may_l,
                    june_l = :june_l,
                    july_l = :july_l,
                    august_l = :august_l,
                    september_l = :september_l,
                    october_l = :october_l,
                    november_l = :november_l,
                    december_l = :december_l,
                    business_category = :business_category,
                    company_type = :company_type,
                    community = :community,
                    municipality = :municipality,
                    state = :state,
                    comments = :comments,
                    updated_by = :updated_by
                WHERE investment_id = :investment_id
            """), {
                "investment_id": investment_id,
                "bank_id": data.get("bank_id"),
                "partner_name": data.get("partner_name"),
                "year": data.get("year"),
                "technician": data.get("technician"),
                "profit_l": data.get("profit_l"),
                "company_value_l": data.get("company_value_l"),
                "expected_profit_pct": data.get("expected_profit_pct"),
                "investment_l": data.get("investment_l"),
                "investment_usd": data.get("investment_usd"),
                "exchange_rate": data.get("exchange_rate"),
                "proposal_state": data.get("proposal_state"),
                "transaction_type": data.get("transaction_type"),
                "january_l": data.get("january_l", 0),
                "february_l": data.get("february_l", 0),
                "march_l": data.get("march_l", 0),
                "april_l": data.get("april_l", 0),
                "may_l": data.get("may_l", 0),
                "june_l": data.get("june_l", 0),
                "july_l": data.get("july_l", 0),
                "august_l": data.get("august_l", 0),
                "september_l": data.get("september_l", 0),
                "october_l": data.get("october_l", 0),
                "november_l": data.get("november_l", 0),
                "december_l": data.get("december_l", 0),
                "business_category": data.get("business_category"),
                "company_type": data.get("company_type"),
                "community": data.get("community"),
                "municipality": data.get("municipality"),
                "state": data.get("state"),
                "comments": data.get("comments"),
                "updated_by": user_id
            })
        
        return jsonify(ok=True, message='Entry updated successfully'), 200
        
    except Exception as e:
        print(f"❌ Error updating profit entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to update entry'), 500

@bp.delete("/profit/entry/<int:investment_id>")
def delete_profit_entry(investment_id):
    """Delete a profit entry"""
    try:
        with SessionLocal() as s, s.begin():
            result = s.execute(text("""
                DELETE FROM profit_form_entries
                WHERE investment_id = :id
            """), {"id": investment_id})
            
            if result.rowcount == 0:
                return jsonify(ok=False, error='Entry not found'), 404
        
        return jsonify(ok=True, message='Entry deleted successfully'), 200
        
    except Exception as e:
        print(f"❌ Error deleting profit entry: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to delete entry'), 500

# ============================================
# FORMULA MANAGEMENT ENDPOINTS
# ============================================

@bp.get("/formulas")
def get_formulas():
    """Get all active formulas"""
    user_id, role, auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        with SessionLocal() as s:
            rows = s.execute(text("""
                SELECT formula_id, formula_key, expression, version, 
                       effective_from, effective_to, description
                FROM formulas
                WHERE effective_to IS NULL
                ORDER BY formula_key
            """)).fetchall()
            
            formulas = []
            for row in rows:
                # Extract form type from formula_key (e.g., profit_investment_usd -> Profit)
                form_type = row.formula_key.split('_')[0].capitalize() if '_' in row.formula_key else 'Unknown'
                # Format status as "Profit - v1" or "Matching - v1"
                status = f"{form_type} - v{row.version}"
                
                formulas.append({
                    'formula_id': row.formula_id,
                    'formula_key': row.formula_key,
                    'field_name': row.formula_key,
                    'field_label': row.formula_key.replace('_', ' ').title(),
                    'expression': row.expression,
                    'description': row.description,
                    'is_active': True,
                    'status': status,
                    'version': row.version,
                    'effective_from': row.effective_from.isoformat() if row.effective_from else None,
                    'updated_at': row.effective_from.isoformat() if row.effective_from else None
                })
            
            return jsonify(ok=True, formulas=formulas), 200
            
    except Exception as e:
        print(f"❌ Error loading formulas: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to load formulas'), 500

@bp.get("/formulas/for-form/<form_type>")
def get_formulas_for_form(form_type):
    """Get active formulas for a specific form type - returns all since form_type doesn't exist in table"""
    user_id, role, auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        with SessionLocal() as s:
            rows = s.execute(text("""
                SELECT formula_key, expression
                FROM formulas
                WHERE effective_to IS NULL
            """)).fetchall()
            
            formulas = {}
            for row in rows:
                # Extract field name from formula_key (e.g., profit_investment_usd -> investment_usd)
                field_name = row.formula_key.split('_', 1)[1] if '_' in row.formula_key else row.formula_key
                formulas[field_name] = {
                    'formula_key': row.formula_key,
                    'expression': row.expression
                }
            
            return jsonify(ok=True, formulas=formulas), 200
            
    except Exception as e:
        print(f"❌ Error loading formulas for form: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to load formulas'), 500

@bp.get("/formulas/all-history")
def get_all_formula_history():
    """Get formula change history from audit_log"""
    user_id, role, auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        with SessionLocal() as s:
            # Get history from audit_log for formulas
            rows = s.execute(text("""
                SELECT 
                    al.audit_id,
                    al.row_pk,
                    al.diff_json,
                    al.changed_by,
                    al.changed_at,
                    JSON_UNQUOTE(JSON_EXTRACT(al.diff_json, '$.old_expression')) as old_expression,
                    JSON_UNQUOTE(JSON_EXTRACT(al.diff_json, '$.new_expression')) as new_expression,
                    JSON_UNQUOTE(JSON_EXTRACT(al.diff_json, '$.old_version')) as old_version,
                    JSON_UNQUOTE(JSON_EXTRACT(al.diff_json, '$.new_version')) as new_version,
                    JSON_UNQUOTE(JSON_EXTRACT(al.diff_json, '$.reason')) as reason,
                    JSON_UNQUOTE(JSON_EXTRACT(al.diff_json, '$.changed_by_username')) as changed_by_username,
                    f.formula_key
                FROM audit_log al
                LEFT JOIN formulas f ON CAST(al.row_pk AS UNSIGNED) = f.formula_id
                WHERE al.table_name = 'formulas'
                ORDER BY al.changed_at DESC
                LIMIT 100
            """)).fetchall()
            
            # Get user names for fallback (older records without username in diff_json)
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
            
            history = []
            for row in rows:
                # Prefer username from diff_json, fallback to user lookup
                if row.changed_by_username:
                    display_name = row.changed_by_username
                elif row.changed_by:
                    display_name = user_map.get(row.changed_by, f'User #{row.changed_by}')
                else:
                    display_name = 'System'
                
                formula_key = row.formula_key or 'unknown'
                
                history.append({
                    'history_id': row.audit_id,
                    'formula_key': formula_key,
                    'field_name': formula_key,
                    'field_label': formula_key.replace('_', ' ').title(),
                    'old_expression': row.old_expression or '-',
                    'new_expression': row.new_expression or '-',
                    'old_version': int(row.old_version) if row.old_version else 0,
                    'new_version': int(row.new_version) if row.new_version else 1,
                    'changed_by': display_name,
                    'changed_at': row.changed_at.isoformat() if row.changed_at else None,
                    'change_reason': row.reason or 'Formula updated'
                })
            
            # If no audit_log entries, fall back to version records
            if not history:
                rows = s.execute(text("""
                    SELECT formula_id, formula_key, expression, version,
                           effective_from, effective_to, description
                    FROM formulas
                    WHERE effective_to IS NOT NULL
                    ORDER BY effective_to DESC
                    LIMIT 100
                """)).fetchall()
                
                for row in rows:
                    history.append({
                        'history_id': row.formula_id,
                        'formula_key': row.formula_key,
                        'field_name': row.formula_key,
                        'field_label': row.formula_key.replace('_', ' ').title(),
                        'old_expression': row.expression,
                        'new_expression': 'See current version',
                        'old_version': row.version,
                        'new_version': row.version + 1,
                        'changed_by': 'System',
                        'changed_at': row.effective_to.isoformat() if row.effective_to else None,
                        'change_reason': 'Formula updated'
                    })
            
            return jsonify(ok=True, history=history), 200
            
    except Exception as e:
        print(f"❌ Error loading formula history: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to load history'), 500

@bp.get("/formulas/history/<formula_key>")
def get_formula_history(formula_key):
    """Get history for a specific formula"""
    user_id, role, auth_error = require_auth()
    if auth_error:
        return auth_error
    
    try:
        with SessionLocal() as s:
            # Get all versions of this formula with audit log info
            rows = s.execute(text("""
                SELECT 
                    f.formula_id, 
                    f.expression, 
                    f.version, 
                    f.effective_from, 
                    f.effective_to, 
                    f.description,
                    JSON_UNQUOTE(JSON_EXTRACT(al.diff_json, '$.reason')) as change_reason,
                    JSON_UNQUOTE(JSON_EXTRACT(al.diff_json, '$.changed_by_username')) as changed_by
                FROM formulas f
                LEFT JOIN audit_log al ON 
                    al.table_name = 'formulas' 
                    AND CAST(al.row_pk AS UNSIGNED) = f.formula_id
                WHERE f.formula_key = :key
                ORDER BY f.version DESC
            """), {"key": formula_key}).fetchall()
            
            history = []
            for row in rows:
                # Use change_reason from audit_log if available, otherwise show version info
                reason = row.change_reason if row.change_reason else f"Version {row.version}"
                changed_by = row.changed_by if row.changed_by else "System"
                
                history.append({
                    'history_id': row.formula_id,
                    'version': row.version,
                    'expression': row.expression,
                    'effective_from': row.effective_from.isoformat() if row.effective_from else None,
                    'effective_to': row.effective_to.isoformat() if row.effective_to else None,
                    'description': reason,
                    'changed_by': changed_by
                })
            
            return jsonify(ok=True, history=history), 200
            
    except Exception as e:
        print(f"❌ Error loading formula history: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to load history'), 500

@bp.put("/formulas/update/<formula_key>")
def update_formula(formula_key):
    """Update a formula with version tracking"""
    user_id, role, auth_error = require_auth()
    if auth_error:
        return auth_error
    
    # Get username from session
    username = session.get('username') or session.get('email') or 'Unknown'
    
    print(f"🔍 Formula update by user_id={user_id}, username={username}")
    
    data = request.get_json()
    new_expression = data.get('expression')
    change_reason = data.get('reason', 'Formula updated')
    
    if not new_expression:
        return jsonify(ok=False, error='Expression is required'), 400
    
    try:
        with SessionLocal() as s, s.begin():
            # Get current formula
            current = s.execute(text("""
                SELECT formula_id, expression, version, description
                FROM formulas
                WHERE formula_key = :key AND effective_to IS NULL
            """), {"key": formula_key}).fetchone()
            
            if not current:
                return jsonify(ok=False, error='Formula not found'), 404
            
            old_version = current.version
            new_version = old_version + 1
            old_expression = current.expression
            
            # Mark current version as expired
            s.execute(text("""
                UPDATE formulas
                SET effective_to = NOW()
                WHERE formula_id = :id
            """), {"id": current.formula_id})
            
            # Insert new version
            result = s.execute(text("""
                INSERT INTO formulas
                (formula_key, expression, version, effective_from, effective_to, description)
                VALUES (:key, :expr, :ver, NOW(), NULL, :desc)
            """), {
                "key": formula_key,
                "expr": new_expression,
                "ver": new_version,
                "desc": current.description
            })
            
            new_formula_id = result.lastrowid
            
            # Create audit log entry with username
            import json
            audit_diff = {
                'old_expression': old_expression,
                'new_expression': new_expression,
                'old_version': old_version,
                'new_version': new_version,
                'reason': change_reason,
                'changed_by_username': username
            }
            
            s.execute(text("""
                INSERT INTO audit_log (table_name, row_pk, action, diff_json, changed_by, changed_at)
                VALUES ('formulas', :row_pk, 'UPDATE', :diff_json, :changed_by, NOW())
            """), {
                "row_pk": str(new_formula_id),
                "diff_json": json.dumps(audit_diff),
                "changed_by": user_id
            })
        
        return jsonify(
            ok=True,
            message='Formula updated successfully',
            old_version=old_version,
            new_version=new_version
        ), 200
        
    except Exception as e:
        print(f"❌ Error updating formula: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error='Failed to update formula'), 500