
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
        return None, None, jsonify(ok=False, error="Not authenticated"), 401
    
    user_id = session.get('user_id')
    if not user_id:
        return None, None, jsonify(ok=False, error="Invalid session"), 401
    
    role = get_user_role(user_id)
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
        proof_path = _save(f, f'dividend-proof-{int(time.time())}')

    if not partner_name:
        return jsonify(ok=False, error="Partner name is required"), 400

    try:
        with SessionLocal() as s, s.begin():
            s.execute(text("""
                INSERT INTO dividend_payout_form_submissions
                (bank_id, partner_name, reported_shares, investment_hnl,
                 investment_usd, payout_date, amount_paid, payment_method,
                 payment_proof_path, comments, confirmed, status, submitted_by)
                VALUES (:bank_id, :partner, :shares, :inv_hnl, :inv_usd,
                        :payout_date, :amount, :method, :proof, :comments, :confirmed, 'SUBMITTED', :user_id)
            """), {
                "bank_id": bank_id,
                "partner": partner_name,
                "shares": reported_shares,
                "inv_hnl": investment_hnl,
                "inv_usd": investment_usd,
                "payout_date": payout_date,
                "amount": amount_paid,
                "method": payment_method,
                "proof": proof_path,
                "comments": comments,
                "confirmed": confirmed,
                "user_id": user_id
            })
            
        return jsonify(ok=True, message="Dividend entry submitted successfully"), 201
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
# GET FORM SUBMISSIONS
# ============================================

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
        print(f"🗑️ Deleting dividend submission {submission_id} by: {username}")
        
        # Optional: Get payment proof path to delete file
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
                        print(f"✅ Deleted payment proof file: {file_path}")
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

# ============================================
# INVESTMENT VS LOAN ENDPOINTS
# ============================================

@bp.post("/investment-loan")
def investment_loan():
    """Handle investment vs loan form submission"""
    b = request.form
    f = request.files.get("attachment")
    
    bank_name = (b.get("bank_name") or "").strip()
    rtn_number = (b.get("rtn_number") or "").strip()
    representative_name = (b.get("representative_name") or "").strip()
    phone_number = (b.get("phone_number") or "").strip()
    funding_type = (b.get("funding_type") or "").strip()  # 'investment' or 'loan'
    
    # Amount fields
    proposed_amount = b.get("proposed_amount", "").strip()
    proposed_amount = float(proposed_amount) if proposed_amount else None
    
    proposed_equity_percentage = b.get("proposed_equity_percentage", "").strip()
    proposed_equity_percentage = float(proposed_equity_percentage) if proposed_equity_percentage else None
    
    interest_rate = b.get("interest_rate", "").strip()
    interest_rate = float(interest_rate) if interest_rate else None
    
    # Date fields
    desired_funding_date = b.get("desired_funding_date", "").strip() or None
    repayment_period_months = b.get("repayment_period_months", "").strip()
    repayment_period_months = int(repayment_period_months) if repayment_period_months else None
    
    # Other fields
    business_description = (b.get("business_description") or "").strip()
    use_of_funds = (b.get("use_of_funds") or "").strip()
    expected_roi = b.get("expected_roi", "").strip()
    expected_roi = float(expected_roi) if expected_roi else None
    
    comments = (b.get("comments") or "").strip()
    confirmed = b.get("confirmed", "false").lower() == "true"
    
    # Save file if present
    attachment_path = None
    if f:
        attachment_path = _save(f, f'investment-loan-{int(time.time())}')

    try:
        with SessionLocal() as s, s.begin():
            s.execute(text("""
                INSERT INTO investment_vs_loan_submissions
                (bank_name, rtn_number, representative_name, phone_number, funding_type,
                 proposed_amount, proposed_equity_percentage, interest_rate,
                 desired_funding_date, repayment_period_months,
                 business_description, use_of_funds, expected_roi,
                 comments, attachment_path, confirmed, status)
                VALUES (:bank_name, :rtn, :rep_name, :phone, :funding_type,
                        :amount, :equity_pct, :interest_rate,
                        :funding_date, :repayment_months,
                        :business_desc, :use_funds, :expected_roi,
                        :comments, :attachment, :confirmed, 'SUBMITTED')
            """), {
                "bank_name": bank_name,
                "rtn": rtn_number,
                "rep_name": representative_name,
                "phone": phone_number,
                "funding_type": funding_type,
                "amount": proposed_amount,
                "equity_pct": proposed_equity_percentage,
                "interest_rate": interest_rate,
                "funding_date": desired_funding_date,
                "repayment_months": repayment_period_months,
                "business_desc": business_description,
                "use_funds": use_of_funds,
                "expected_roi": expected_roi,
                "comments": comments,
                "attachment": attachment_path,
                "confirmed": confirmed
            })
            
        return jsonify(ok=True, message="Investment vs Loan form submitted successfully"), 201
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
        if 'file' not in request.files:
            return jsonify(ok=False, error='No file provided'), 400
        
        file = request.files['file']
        
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
                        :reported_shares, :share_capital_multiplied, :expected_profit_pct,
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
                    "share_capital_multiplied": record['share_capital_multiplied'],
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
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading your CSV file. Please check that your file follows the template format and all required fields are filled in correctly. If the problem persists, contact support.'
        }), 500


@bp.put("/matching/entry/<int:investment_id>")
def update_matching_entry(investment_id):
    """Update a micro equity matching entry with audit tracking"""
    
    print("=" * 70)
    print(f"📝 UPDATE MATCHING ENTRY - ID: {investment_id}")
    print("=" * 70)
    
    # Get data
    data = request.get_json()
    
    partner_name = (data.get("partner_name") or "").strip()
    if not partner_name:
        return jsonify(ok=False, error="Partner name is required"), 400
    
    # Get user_id (integer) instead of username (string)
    user_id = session.get('user_id', 1)
    username = session.get('username', 'System')
    print(f"👤 Updating as: {username} (ID: {user_id})")
    print("=" * 70)
    
    try:
        with SessionLocal() as s, s.begin():
            result = s.execute(text("""
                UPDATE matching_equity_entries SET
                    bank_id = :bank_id,
                    partner_name = :partner_name,
                    year = :year,
                    technician = :technician,
                    comments = :comments,
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
                    updated_by = :updated_by,
                    updated_at = CURRENT_TIMESTAMP
                WHERE investment_id = :investment_id
            """), {
                "investment_id": investment_id,
                "bank_id": data.get("bank_id"),
                "partner_name": partner_name,
                "year": data.get("year"),
                "technician": data.get("technician"),
                "comments": data.get("comments"),
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
                "updated_by": username
            })
            
            if result.rowcount == 0:
                return jsonify(ok=False, error="Entry not found"), 404
        
        print(f"✅ Entry {investment_id} updated by {username} (ID: {user_id})")
        print("=" * 70)
        return jsonify(ok=True, message="Entry updated successfully"), 200
        
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


@bp.get("/matching/entries")
def get_matching_entries():
    """Get all micro equity matching entries with audit data"""
    try:
        with SessionLocal() as s:
            # Added LEFT JOINs to get actual usernames
            rows = s.execute(text("""
                SELECT 
                    m.investment_id, m.bank_id, m.partner_name, m.year, m.technician,
                    m.reported_shares, m.share_capital_multiplied, m.expected_profit_pct,
                    m.investment_l, m.investment_usd, m.exchange_rate,
                    m.proposal_state, m.transaction_type,
                    m.business_category, m.company_type, m.community, m.municipality, m.state,
                    m.january_l, m.february_l, m.march_l, m.april_l, m.may_l, m.june_l,
                    m.july_l, m.august_l, m.september_l, m.october_l, m.november_l, m.december_l,
                    m.comments, m.start_date, 
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
                    'start_date': row.start_date.isoformat() if row.start_date else None,
                    # Return actual usernames from JOIN, not IDs
                    'created_by': row.created_by_name if row.created_by_name else 'System',
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_by': row.updated_by_name if row.updated_by_name else 'System',
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
        print(f"❌ Error in profit bulk upload: {e}")
        import traceback
        traceback.print_exc()
        # Don't expose SQL errors to users - show friendly message instead
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading your CSV file. Please check that your file follows the template format and all required fields are filled in correctly. If the problem persists, contact support.'
        }), 500

@bp.delete("/matching/entry/<int:investment_id>")
def delete_matching_entry(investment_id):
    """Delete a micro equity matching entry"""
    username = session.get('username', 'System')
    print(f"👤 Deleting entry {investment_id} by: {username}")
    
    try:
        with SessionLocal() as s, s.begin():
            result = s.execute(text("""
                DELETE FROM matching_equity_entries WHERE investment_id = :iid
            """), {"iid": investment_id})
            
            if result.rowcount == 0:
                return jsonify(ok=False, error="Entry not found"), 404
        
        print(f"✅ Entry {investment_id} deleted by {username}")
        return jsonify(ok=True, message="Entry deleted successfully"), 200
        
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
# TEST SESSION ENDPOINT (TEMPORARY - FOR DEBUGGING)
# ============================================

@bp.get("/test-session")
def test_session():
    """Test if session is working properly"""
    from flask import session
    
    return jsonify({
        "ok": True,
        "session_exists": bool(session),
        "session_data": {
            "username": session.get('username', 'NOT FOUND'),
            "user_id": session.get('user_id', 'NOT FOUND'),
            "email": session.get('email', 'NOT FOUND'),
            "is_authenticated": session.get('is_authenticated', False)
        },
        "all_session_keys": list(session.keys())
    })
# ============================================
# FORMULA MANAGEMENT ENDPOINTS
# ============================================

@bp.get("/formulas")
def get_formulas():
    """Get all active formulas (effective_to IS NULL)"""
    try:
        with SessionLocal() as s:
            rows = s.execute(text("""
                SELECT 
                    formula_id,
                    formula_key,
                    expression,
                    version,
                    effective_from,
                    effective_to,
                    description
                FROM formulas
                WHERE effective_to IS NULL
                ORDER BY formula_key
            """)).fetchall()
            
            formulas = []
            for row in rows:
                # Parse formula_key and description
                parts = row.formula_key.split('_', 1)
                form_type = parts[0] if len(parts) > 0 else 'unknown'
                field_name = parts[1] if len(parts) > 1 else row.formula_key
                
                # Parse description (format: FieldLabel|FormName|ChangeReason)
                desc_parts = (row.description or '||').split('|')
                field_label = desc_parts[0] if len(desc_parts) > 0 else field_name
                form_name = desc_parts[1] if len(desc_parts) > 1 else ''
                
                formulas.append({
                    'formula_id': row.formula_id,
                    'formula_key': row.formula_key,
                    'field_name': field_name,
                    'field_label': field_label,
                    'form_name': form_name,
                    'form_type': form_type,
                    'expression': row.expression,
                    'version': row.version,
                    'effective_from': row.effective_from.isoformat() if row.effective_from else None,
                    'effective_to': row.effective_to.isoformat() if row.effective_to else None
                })
            
            return jsonify(ok=True, formulas=formulas), 200
            
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

@bp.get("/formulas/history/<formula_key>")
def get_formula_history(formula_key):
    """Get version history for a specific formula"""
    try:
        with SessionLocal() as s:
            rows = s.execute(text("""
                SELECT 
                    formula_id,
                    formula_key,
                    expression,
                    version,
                    effective_from,
                    effective_to,
                    description
                FROM formulas
                WHERE formula_key = :key
                ORDER BY version DESC
            """), {"key": formula_key}).fetchall()
            
            history = []
            for row in rows:
                # Parse description for change reason
                desc_parts = (row.description or '').split('|')
                explanation = desc_parts[2] if len(desc_parts) > 2 else row.description
                
                history.append({
                    'formula_id': row.formula_id,
                    'formula_key': row.formula_key,
                    'expression': row.expression,
                    'version': row.version,
                    'effective_from': row.effective_from.isoformat() if row.effective_from else None,
                    'effective_to': row.effective_to.isoformat() if row.effective_to else None,
                    'description': explanation
                })
            
            return jsonify(ok=True, history=history), 200
            
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

@bp.get("/formulas/all-history")
def get_all_formula_history():
    """Get complete history of all formula changes with comparison"""
    try:
        with SessionLocal() as s:
            rows = s.execute(text("""
                SELECT 
                    f1.formula_id,
                    f1.formula_key,
                    f1.expression as new_expression,
                    f1.version as new_version,
                    f1.effective_from,
                    f1.effective_to,
                    f1.description,
                    f2.expression as old_expression,
                    f2.version as old_version
                FROM formulas f1
                LEFT JOIN formulas f2 ON f1.formula_key = f2.formula_key 
                    AND f2.version = f1.version - 1
                WHERE f1.version > 1
                ORDER BY f1.formula_key, f1.version DESC
            """)).fetchall()
            
            history = []
            for row in rows:
                # Parse formula_key and description
                parts = row.formula_key.split('_', 1)
                form_type = parts[0] if len(parts) > 0 else 'unknown'
                field_name = parts[1] if len(parts) > 1 else row.formula_key
                
                desc_parts = (row.description or '||').split('|')
                field_label = desc_parts[0] if len(desc_parts) > 0 else field_name
                explanation = desc_parts[2] if len(desc_parts) > 2 else ''
                
                history.append({
                    'formula_id': row.formula_id,
                    'formula_key': row.formula_key,
                    'field_name': field_name,
                    'field_label': field_label,
                    'form_type': form_type,
                    'old_expression': row.old_expression,
                    'old_version': row.old_version,
                    'new_expression': row.new_expression,
                    'new_version': row.new_version,
                    'effective_from': row.effective_from.isoformat() if row.effective_from else None,
                    'effective_to': row.effective_to.isoformat() if row.effective_to else None,
                    'reason': explanation
                })
            
            return jsonify(ok=True, history=history), 200
            
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

@bp.put("/formulas/update/<formula_key>")
def update_formula(formula_key):
    """Update a formula by creating a new version"""
    data = request.get_json()
    
    new_expression = data.get("expression", "").strip()
    new_description_text = data.get("description", "").strip()
    reason = data.get("reason", "").strip()
    
    if not new_expression:
        return jsonify(ok=False, error="Expression is required"), 400
    
    if not reason:
        return jsonify(ok=False, error="Reason for change is required"), 400
    
    try:
        with SessionLocal() as s, s.begin():
            # Get current version
            current = s.execute(text("""
                SELECT formula_id, version, expression, description
                FROM formulas
                WHERE formula_key = :key
                AND effective_to IS NULL
                LIMIT 1
            """), {"key": formula_key}).fetchone()
            
            if not current:
                return jsonify(ok=False, error="Formula not found"), 404
            
            old_expression = current.expression
            current_version = current.version
            
            # Parse current description to get form name
            desc_parts = (current.description or '||').split('|')
            old_field_label = desc_parts[0] if len(desc_parts) > 0 else ''
            form_name = desc_parts[1] if len(desc_parts) > 1 else ''
            
            # Use new description if provided, otherwise keep old field label
            field_label = new_description_text if new_description_text else old_field_label
            
            # Close out the current version
            s.execute(text("""
                UPDATE formulas
                SET effective_to = NOW()
                WHERE formula_key = :key
                AND effective_to IS NULL
            """), {"key": formula_key})
            
            # Build new description preserving format: FieldLabel|FormName|Reason
            new_description = f"{field_label}|{form_name}|{reason}"
            
            # Create new version
            s.execute(text("""
                INSERT INTO formulas (formula_key, expression, version, effective_from, effective_to, description)
                VALUES (:key, :expr, :ver, NOW(), NULL, :desc)
            """), {
                "key": formula_key,
                "expr": new_expression,
                "ver": current_version + 1,
                "desc": new_description
            })
            
        return jsonify(
            ok=True, 
            message="Formula updated successfully",
            old_version=current_version,
            new_version=current_version + 1,
            old_expression=old_expression,
            new_expression=new_expression
        ), 200
        
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

@bp.get("/formulas/for-form/<form_type>")
def get_formulas_for_form(form_type):
    """Get active formulas for a specific form (profit, matching)"""
    try:
        with SessionLocal() as s:
            rows = s.execute(text("""
                SELECT 
                    formula_key,
                    expression
                FROM formulas
                WHERE effective_to IS NULL
                AND formula_key LIKE :pattern
                ORDER BY formula_key
            """), {"pattern": f"{form_type}_%"}).fetchall()
            
            formulas = {}
            for row in rows:
                # Extract field_name from formula_key (remove form_type prefix)
                field_name = row.formula_key.replace(f"{form_type}_", "", 1)
                formulas[field_name] = {
                    'formula_key': row.formula_key,
                    'expression': row.expression
                }
            
            return jsonify(ok=True, formulas=formulas), 200
            
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
# INVESTMENT VS LOANS (IVL) ENDPOINTS WITH AUDIT TRACKING
# ============================================

@bp.get("/ivl/entries")
def get_ivl_entries():
    """
    Get all Investment vs Loans entries with audit tracking info
    Returns: updated_by, updated_at, created_by, created_at
    """
    try:
        with SessionLocal() as s:
            rows = s.execute(text("""
                SELECT 
                    investment_id,
                    partner_name,
                    expected_profit_pct,
                    investment_amount,
                    last_loan,
                    difference,
                    comments,
                    notes,
                    start_date,
                    created_by,
                    created_at,
                    updated_at,
                    updated_by
                FROM ivl_form_entries
                ORDER BY investment_id DESC
            """)).fetchall()

            entries = []
            for row in rows:
                entries.append({
                    'investment_id': row.investment_id,
                    'partner_name': row.partner_name,
                    'expected_profit_pct': float(row.expected_profit_pct) if row.expected_profit_pct is not None else None,
                    'investment_amount': float(row.investment_amount) if row.investment_amount is not None else None,
                    'last_loan': float(row.last_loan) if row.last_loan is not None else None,
                    'difference': float(row.difference) if row.difference is not None else None,
                    'comments': row.comments,
                    'notes': row.notes,
                    'start_date': row.start_date.isoformat() if row.start_date else None,
                    'created_by': row.created_by,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                    'updated_by': row.updated_by
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


@bp.put("/ivl/entry/<int:investment_id>")
def update_ivl_entry(investment_id):
    """
    Update an IVL entry and track who made the change
    Captures username from session for audit tracking
    """
    try:
        # Get username from session for audit tracking
        username = session.get('username', 'Unknown')
        print(f"🔍 DEBUG IVL UPDATE - Username: '{username}' from session: {dict(session)}")

        data = request.get_json()

        # Validate required fields
        partner_name = (data.get('partner_name') or "").strip()
        expected_profit_pct = data.get('expected_profit_pct')
        
        if not partner_name or expected_profit_pct is None:
            return jsonify(ok=False, error='Partner name and expected profit percentage are required'), 400

        with SessionLocal() as s, s.begin():
            result = s.execute(text("""
                UPDATE ivl_form_entries
                SET
                    partner_name = :partner_name,
                    expected_profit_pct = :expected_profit_pct,
                    investment_amount = :investment_amount,
                    last_loan = :last_loan,
                    difference = :difference,
                    comments = :comments,
                    updated_by = :updated_by
                WHERE investment_id = :investment_id
            """), {
                'partner_name': partner_name,
                'expected_profit_pct': expected_profit_pct,
                'investment_amount': data.get('investment_amount'),
                'last_loan': data.get('last_loan'),
                'difference': data.get('difference'),
                'comments': data.get('comments'),
                'updated_by': username,
                'investment_id': investment_id
            })

            if result.rowcount == 0:
                return jsonify(ok=False, error='Entry not found'), 404

        print(f"✅ IVL Entry {investment_id} updated by {username}")
        return jsonify(ok=True, message='Entry updated successfully', updated_by=username), 200

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


@bp.get("/ivl/summary")
def get_ivl_summary():
    """
    Calculate and return summary totals for IVL entries
    """
    try:
        with SessionLocal() as s:
            row = s.execute(text("""
                SELECT 
                    COALESCE(SUM(investment_amount), 0) as total_investment,
                    COALESCE(SUM(last_loan), 0) as total_last_loan,
                    COALESCE(SUM(difference), 0) as total_difference
                FROM ivl_form_entries
            """)).fetchone()

            summary = {
                'total_investment': float(row.total_investment),
                'total_last_loan': float(row.total_last_loan),
                'total_difference': float(row.total_difference)
            }

            return jsonify(ok=True, summary=summary), 200

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


@bp.post("/ivl/entry")
def create_ivl_entry():
    """
    Create a new IVL entry with created_by tracking
    """
    try:
        # Get username from session for created_by
        username = session.get('username', 'Unknown')

        # Get form data
        partner_name = (request.form.get('partner_name') or "").strip()
        expected_profit_pct = request.form.get('expected_profit_pct')
        investment_amount = request.form.get('investment_amount_l')
        last_loan = request.form.get('last_loan_l')
        comments = request.form.get('comments')

        # Validate required fields
        if not partner_name or not expected_profit_pct:
            return jsonify(ok=False, error='Partner name and expected profit percentage are required'), 400

        # Calculate difference
        inv_amt = float(investment_amount) if investment_amount else 0
        loan_amt = float(last_loan) if last_loan else 0
        difference = inv_amt - loan_amt

        with SessionLocal() as s, s.begin():
            s.execute(text("""
                INSERT INTO ivl_form_entries (
                    partner_name,
                    expected_profit_pct,
                    investment_amount,
                    last_loan,
                    difference,
                    comments,
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
                    CURRENT_DATE,
                    :created_by,
                    :updated_by
                )
            """), {
                'partner_name': partner_name,
                'expected_profit_pct': expected_profit_pct,
                'investment_amount': investment_amount,
                'last_loan': last_loan,
                'difference': difference,
                'comments': comments,
                'created_by': username,
                'updated_by': username
            })

        return jsonify(ok=True, message='Entry created successfully'), 201

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


@bp.delete("/ivl/entry/<int:investment_id>")
def delete_ivl_entry(investment_id):
    """
    Delete an IVL entry
    """
    try:
        with SessionLocal() as s, s.begin():
            result = s.execute(text("""
                DELETE FROM ivl_form_entries WHERE investment_id = :investment_id
            """), {'investment_id': investment_id})

            if result.rowcount == 0:
                return jsonify(ok=False, error='Entry not found'), 404

        return jsonify(ok=True, message='Entry deleted successfully'), 200

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
# IVL BULK CSV UPLOAD - USER-FRIENDLY ERRORS
# ============================================


# ============================================
# IVL BULK CSV UPLOAD - ALL OR NOTHING VALIDATION
# ============================================

def validate_ivl_csv_record(row, row_num):
    """
    Validate a single IVL CSV record
    Returns: (is_valid: bool, error_message: str or None)
    """
    errors = []
    
    # Check required: Partner Name
    partner_name = (row.get('Partner Name') or "").strip()
    if not partner_name:
        errors.append("Partner Name is required")
    
    # Check required: Expected Profit %
    expected_profit = (row.get('Expected Profit %') or "").strip()
    if not expected_profit:
        errors.append("Expected Profit % is required")
    else:
        try:
            profit_val = float(expected_profit)
            if profit_val < 0 or profit_val > 100:
                errors.append(f"Expected Profit % must be between 0 and 100 (got {profit_val})")
        except ValueError:
            errors.append(f"Expected Profit % must be a valid number (got '{expected_profit}')")
    
    # Check optional: Investment Amount
    investment_amount = (row.get('Investment Amount (L.)') or "").strip()
    if investment_amount:
        try:
            inv_val = float(investment_amount)
            if inv_val < 0:
                errors.append(f"Investment Amount cannot be negative (got {inv_val})")
        except ValueError:
            errors.append(f"Investment Amount must be a valid number (got '{investment_amount}')")
    
    # Check optional: Last Loan
    last_loan = (row.get('Last Loan (L.)') or "").strip()
    if last_loan:
        try:
            loan_val = float(last_loan)
            if loan_val < 0:
                errors.append(f"Last Loan cannot be negative (got {loan_val})")
        except ValueError:
            errors.append(f"Last Loan must be a valid number (got '{last_loan}')")
    
    # Return validation result
    if errors:
        return False, '; '.join(errors)
    return True, None


def parse_and_validate_ivl_csv(content):
    """
    Parse CSV and validate ALL records before inserting ANY
    Returns: (valid_records: list, validation_errors: list)
    """
    valid_records = []
    validation_errors = []
    
    try:
        csv_reader = csv.DictReader(StringIO(content))
        
        # Check for required headers
        required_headers = {'Partner Name', 'Expected Profit %'}
        csv_headers = set(csv_reader.fieldnames or [])
        
        missing_headers = required_headers - csv_headers
        if missing_headers:
            validation_errors.append({
                'row': 'Header',
                'error': f"Missing required columns: {', '.join(missing_headers)}"
            })
            return [], validation_errors
        
        # Validate each row
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (row 1 is header)
            # Skip completely empty rows
            if all(not str(v).strip() for v in row.values()):
                continue
            
            # Validate the record
            is_valid, error_msg = validate_ivl_csv_record(row, row_num)
            
            if not is_valid:
                validation_errors.append({
                    'row': row_num,
                    'error': error_msg
                })
            else:
                # Store validated record
                partner_name = (row.get('Partner Name') or "").strip()
                expected_profit_pct = float((row.get('Expected Profit %') or "").strip())
                investment_amount = (row.get('Investment Amount (L.)') or "").strip()
                last_loan = (row.get('Last Loan (L.)') or "").strip()
                comments = (row.get('Comments') or "").strip()
                
                # Convert to float or None
                investment_amount_float = float(investment_amount) if investment_amount else None
                last_loan_float = float(last_loan) if last_loan else None
                
                # Calculate difference
                inv_amt = investment_amount_float if investment_amount_float else 0
                loan_amt = last_loan_float if last_loan_float else 0
                difference = inv_amt - loan_amt
                
                valid_records.append({
                    'partner_name': partner_name,
                    'expected_profit_pct': expected_profit_pct,
                    'investment_amount': investment_amount_float,
                    'last_loan': last_loan_float,
                    'difference': difference,
                    'comments': comments or None
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
        print(f"❌ Error in profit bulk upload: {e}")
        import traceback
        traceback.print_exc()
        # Don't expose SQL errors to users - show friendly message instead
        return jsonify({
            'ok': False,
            'error': 'Upload failed',
            'message': 'An error occurred while uploading your CSV file. Please check that your file follows the template format and all required fields are filled in correctly. If the problem persists, contact support.'
        }), 500
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
# PROFIT FORM ENDPOINTS
# ============================================

@bp.get("/profit/entries")
def get_profit_entries():
    """
    Get all profit form entries with audit tracking info
    Returns: updated_by, updated_at, created_by, created_at (with usernames)
    """
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
                    u1.username as created_by_name, u2.username as updated_by_name
                FROM profit_form_entries p
                LEFT JOIN users u1 ON p.created_by = u1.user_id
                LEFT JOIN users u2 ON p.updated_by = u2.username
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
                    'profit_l': float(row.profit_l) if row.profit_l is not None else None,
                    'company_value_l': float(row.company_value_l) if row.company_value_l is not None else None,
                    'expected_profit_pct': float(row.expected_profit_pct) if row.expected_profit_pct is not None else None,
                    'investment_l': float(row.investment_l) if row.investment_l is not None else None,
                    'investment_usd': float(row.investment_usd) if row.investment_usd is not None else None,
                    'exchange_rate': float(row.exchange_rate) if row.exchange_rate is not None else None,
                    'proposal_state': row.proposal_state,
                    'transaction_type': row.transaction_type,
                    'january_l': float(row.january_l) if row.january_l is not None else 0,
                    'february_l': float(row.february_l) if row.february_l is not None else 0,
                    'march_l': float(row.march_l) if row.march_l is not None else 0,
                    'april_l': float(row.april_l) if row.april_l is not None else 0,
                    'may_l': float(row.may_l) if row.may_l is not None else 0,
                    'june_l': float(row.june_l) if row.june_l is not None else 0,
                    'july_l': float(row.july_l) if row.july_l is not None else 0,
                    'august_l': float(row.august_l) if row.august_l is not None else 0,
                    'september_l': float(row.september_l) if row.september_l is not None else 0,
                    'october_l': float(row.october_l) if row.october_l is not None else 0,
                    'november_l': float(row.november_l) if row.november_l is not None else 0,
                    'december_l': float(row.december_l) if row.december_l is not None else 0,
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
        print(f"ERROR in get_profit_entries: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error=str(e)), 500



@bp.put("/profit/entry/<int:investment_id>")
def update_profit_entry(investment_id):
    """
    Update a profit entry and track who made the change
    Captures username from session for audit tracking
    """
    try:
        # Get username from session for audit tracking
        username = session.get('username', 'System')
        print(f"👤 Updating profit entry {investment_id} as: {username}")
        
        data = request.get_json()
        
        with SessionLocal() as s, s.begin():
            s.execute(text("""
                UPDATE profit_form_entries
                SET
                    bank_id = :bank_id,
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
                    updated_at = CURRENT_TIMESTAMP,
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
                "updated_by": username
            })

        print(f"✅ Profit entry {investment_id} updated successfully by {username}")
        return jsonify(ok=True, message="Entry updated successfully"), 200

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


@bp.delete("/profit/entry/<int:investment_id>")
def delete_profit_entry(investment_id):
    """
    Delete a profit entry
    """
    try:
        username = session.get('username', 'System')
        print(f"🗑️ Deleting profit entry {investment_id} by: {username}")
        
        with SessionLocal() as s, s.begin():
            s.execute(text("""
                DELETE FROM profit_form_entries
                WHERE investment_id = :investment_id
            """), {"investment_id": investment_id})

        print(f"✅ Profit entry {investment_id} deleted successfully")
        return jsonify(ok=True, message="Entry deleted successfully"), 200

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


@bp.get("/profit/summary")
def get_profit_summary():
    """
    Get summary statistics for profit entries
    """
    try:
        with SessionLocal() as s:
            result = s.execute(text("""
                SELECT 
                    COUNT(*) as total_entries,
                    COALESCE(SUM(investment_l), 0) as total_investment_l,
                    COALESCE(SUM(investment_usd), 0) as total_investment_usd,
                    COALESCE(AVG(expected_profit_pct), 0) as avg_expected_profit
                FROM profit_form_entries
            """)).fetchone()

            summary = {
                'total_entries': result.total_entries,
                'total_investment_l': float(result.total_investment_l),
                'total_investment_usd': float(result.total_investment_usd),
                'avg_expected_profit': float(result.avg_expected_profit)
            }

            return jsonify(ok=True, summary=summary), 200

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


@bp.post("/profit/entry")
def create_profit_entry():
    """
    Create a new profit entry
    """
    try:
        user_id = session.get('user_id', 1)
        username = session.get('username', 'System')
        print(f"➕ Creating new profit entry by: {username} (ID: {user_id})")
        
        data = request.get_json()
        
        with SessionLocal() as s, s.begin():
            s.execute(text("""
                INSERT INTO profit_form_entries (
                    bank_id, partner_name, year, technician,
                    profit_l, company_value_l, expected_profit_pct,
                    investment_l, investment_usd, exchange_rate,
                    proposal_state, transaction_type,
                    january_l, february_l, march_l, april_l, may_l, june_l,
                    july_l, august_l, september_l, october_l, november_l, december_l,
                    business_category, company_type, community, municipality, state,
                    comments, start_date, created_by
                ) VALUES (
                    :bank_id, :partner_name, :year, :technician,
                    :profit_l, :company_value_l, :expected_profit_pct,
                    :investment_l, :investment_usd, :exchange_rate,
                    :proposal_state, :transaction_type,
                    :january_l, :february_l, :march_l, :april_l, :may_l, :june_l,
                    :july_l, :august_l, :september_l, :october_l, :november_l, :december_l,
                    :business_category, :company_type, :community, :municipality, :state,
                    :comments, :start_date, :created_by
                )
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
                "start_date": data.get("start_date"),
                "created_by": user_id
            })

        print(f"✅ Profit entry created successfully by {username}")
        return jsonify(ok=True, message="Entry created successfully"), 201

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
# PROFIT ENTRIES - BULK CSV UPLOAD (ALL-OR-NOTHING)
# ============================================

# ============================================
# PROFIT CSV VALIDATION
# ============================================

def parse_and_validate_profit_csv(content):
    """
    Parse and validate profit CSV file
    Returns: (valid_records: list, validation_errors: list)
    """
    valid_records = []
    validation_errors = []
    
    try:
        csv_reader = csv.DictReader(StringIO(content))
        
        # Required headers - matching the actual template format
        required_headers = {'partner_name', 'expected_profit_pct'}
        csv_headers = set(csv_reader.fieldnames or [])
        
        missing_headers = required_headers - csv_headers
        if missing_headers:
            validation_errors.append({
                'row': 'Header',
                'error': f"Missing required columns: {', '.join(missing_headers)}"
            })
            return [], validation_errors
        
        # Validate each row
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (row 1 is header)
            # Skip completely empty rows
            if all(not str(v).strip() for v in row.values()):
                continue
            
            errors = []
            
            # Required fields validation
            partner_name = (row.get('partner_name') or "").strip()
            if not partner_name:
                errors.append("partner_name is required")
            
            # Expected profit %
            expected_profit_str = (row.get('expected_profit_pct') or "").strip()
            if not expected_profit_str:
                errors.append("expected_profit_pct is required")
            else:
                try:
                    expected_profit_pct = float(expected_profit_str)
                except ValueError:
                    errors.append(f"Expected Profit % must be a number, got '{expected_profit_str}'")
            
            # If there are errors for this row, add them
            if errors:
                validation_errors.append({
                    'row': row_num,
                    'error': '; '.join(errors)
                })
                continue
            
            # Helper function to safely parse floats
            def safe_float(val, default=None):
                val_str = (val or "").strip()
                if not val_str:
                    return default
                try:
                    return float(val_str)
                except ValueError:
                    return default
            
            # Helper function to safely parse dates
            def safe_date(val):
                val_str = (val or "").strip()
                if not val_str:
                    return None
                try:
                    # Try parsing common date formats
                    from datetime import datetime
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                        try:
                            return datetime.strptime(val_str, fmt).date()
                        except ValueError:
                            continue
                    return None
                except:
                    return None
            
            # Build the record with all fields - using template headers (lowercase_underscore format)
            valid_records.append({
                'bank_id': (row.get('bank_id') or "").strip() or None,
                'partner_name': partner_name,
                'year': safe_float(row.get('year')),
                'technician': (row.get('technician') or "").strip() or None,
                'profit_l': safe_float(row.get('profit_l')),
                'company_value_l': safe_float(row.get('company_value_l')),
                'expected_profit_pct': expected_profit_pct,
                'investment_l': safe_float(row.get('investment_l')),
                'investment_usd': safe_float(row.get('investment_usd')),
                'exchange_rate': safe_float(row.get('exchange_rate')),
                'proposal_state': (row.get('proposal_state') or "").strip() or None,
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
        if 'file' not in request.files:
            return jsonify(ok=False, error='No file provided'), 400
        
        file = request.files['file']
        
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
