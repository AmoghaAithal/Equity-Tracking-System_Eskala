
# admin.py
"""
Admin routes for user management including:
- List users (with approval status)
- Create users (admin-created users are auto-approved)
- Approve/Reject users
- Delete users
"""

import re
import bcrypt
from flask import Blueprint, request, jsonify
from sqlalchemy import text
from db import SessionLocal, run_query

# Import email sending from auth module
try:
    from auth import send_email, BASE_URL
except ImportError:
    # Fallback if auth module not available
    BASE_URL = "http://localhost:5000"
    def send_email(to_email, subject, html_body, text_body=None):
        print("\n" + "="*60)
        print(f"📧 EMAIL TO: {to_email}")
        print(f"📧 SUBJECT: {subject}")
        
        # Determine preview type from subject
        preview_type = None
        subject_lower = subject.lower()
        if "approved" in subject_lower or "aprobada" in subject_lower:
            preview_type = "approval"
        elif "not approved" in subject_lower or "no aprobada" in subject_lower:
            preview_type = "rejection"
        elif "welcome" in subject_lower or "bienvenido" in subject_lower:
            preview_type = "invite"
        elif "verify" in subject_lower or "verifica" in subject_lower:
            preview_type = "verification"
        elif "reset" in subject_lower or "restablecer" in subject_lower:
            preview_type = "password-reset"
        elif "changed" in subject_lower or "cambiada" in subject_lower:
            preview_type = "password-changed"
        
        if preview_type:
            print(f"📧 PREVIEW: {BASE_URL}/api/admin/email-preview/{preview_type}")
        
        # Extract and display links for easy clicking
        links = re.findall(r'href="([^"]+)"', html_body)
        if links:
            print("📧 LINKS:")
            for link in links:
                if link != "#":
                    print(f"   🔗 {link}")
        
        print("="*60 + "\n")
        return True


def friendly_error(e):
    """Convert technical SQL errors to user-friendly messages"""
    err_str = str(e).lower()
    if "duplicate entry" in err_str or "unique constraint" in err_str:
        if "email" in err_str:
            return "This email address is already registered."
        elif "username" in err_str:
            return "This username is already taken."
        elif "rtn" in err_str:
            return "This routing number is already in use."
        return "This record already exists in the system."
    if "foreign key constraint" in err_str:
        return "Cannot complete this action due to related records in the system."
    if "data too long" in err_str:
        return "One or more fields exceed the maximum length allowed."
    if "cannot delete or update a parent row" in err_str:
        return "Cannot delete this user because they have associated records."
    if "access denied" in err_str:
        return "Database access error. Please contact support."
    return "An unexpected error occurred. Please try again or contact support."


def generate_unique_username(session, base_username):
    """Generate a unique username by appending numbers if needed"""
    from sqlalchemy import text
    
    # First check if base username is available
    exists = session.execute(text(
        "SELECT 1 FROM users WHERE username = :u LIMIT 1"
    ), {"u": base_username}).first()
    
    if not exists:
        return base_username
    
    # Find the next available number
    counter = 2
    while counter < 1000:  # Safety limit
        candidate = f"{base_username}{counter}"
        exists = session.execute(text(
            "SELECT 1 FROM users WHERE username = :u LIMIT 1"
        ), {"u": candidate}).first()
        if not exists:
            return candidate
        counter += 1
    
    # Fallback: use timestamp
    import time
    return f"{base_username}_{int(time.time())}"


def email_template(title, content, button_text=None, button_url=None, button_color="#166534"):
    """Generate consistent email HTML template with Eskala branding - simplified for email clients"""
    button_html = ""
    if button_text and button_url:
        button_html = f'''
        <tr>
          <td align="center" style="padding: 30px 0;">
            <a href="{button_url}" 
               style="background-color: {button_color}; color: white; padding: 14px 36px; 
                      text-decoration: none; border-radius: 8px; display: inline-block;
                      font-weight: 600; font-size: 16px;">
                {button_text}
            </a>
          </td>
        </tr>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 20px; font-family: Arial, sans-serif; background-color: #f5f5f5;">
      <table role="presentation" cellspacing="0" cellpadding="0" align="center" style="max-width: 500px; width: 100%; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden;">
        <!-- Orange Header -->
        <tr>
          <td style="background-color: #f48434; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px; font-weight: 700;">{title}</h1>
          </td>
        </tr>
        <!-- Content -->
        <tr>
          <td style="padding: 40px 30px;">
            {content}
          </td>
        </tr>
        <!-- Button -->
        {button_html}
        <!-- Footer -->
        <tr>
          <td style="background-color: #f9fafb; padding: 20px 30px; text-align: center; border-top: 1px solid #e5e7eb;">
            <p style="color: #9ca3af; font-size: 12px; margin: 0;">© Eskala Operations</p>
          </td>
        </tr>
      </table>
    </body>
    </html>
    '''


bp = Blueprint("admin", __name__, url_prefix="/api/admin")


# ============================================
# EMAIL PREVIEW (for development)
# ============================================
@bp.get("/email-preview/<email_type>")
def email_preview(email_type: str):
    """Preview email templates in browser (dev only)"""
    from flask import Response
    
    previews = {
        "approval": email_template(
            title="Account Approved! / ¡Cuenta aprobada!",
            content='''
            <div style="text-align: center;">
              <div style="background: #dcfce7; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 40px; color: #16a34a;">✓</span>
              </div>
              <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 16px 0;">
                <strong>Great news!</strong> Your Eskala account has been reviewed and approved. You now have full access to the platform.
              </p>
              <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0;">
                <strong>¡Excelentes noticias!</strong> Tu cuenta de Eskala ha sido revisada y aprobada. Ahora tienes acceso completo a la plataforma.
              </p>
            </div>
            ''',
            button_text="Log In to Your Account / Iniciar sesión",
            button_url="/web/staff-login.html",
            button_color="#166534"
        ),
        "rejection": email_template(
            title="Application Not Approved / Solicitud no aprobada",
            content='''
            <div style="text-align: center;">
              <div style="background: #fee2e2; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 40px; color: #dc2626;">✗</span>
              </div>
              <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 16px 0;">
                We're sorry, but your account application was not approved at this time.
              </p>
              <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0;">
                Lo sentimos, pero tu solicitud de cuenta no fue aprobada en este momento.
              </p>
              <div style="background: #fef2f2; border-left: 4px solid #dc2626; padding: 16px; margin: 20px 0; border-radius: 4px;">
                <p style="color: #991b1b; margin: 0 0 8px 0; font-weight: 600;">Reason / Razón:</p>
                <p style="color: #7f1d1d; margin: 0;">Example rejection reason here.</p>
              </div>
              <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
                If you believe this is an error, please contact support.<br>
                Si crees que esto es un error, por favor contacta a soporte.
              </p>
            </div>
            '''
        ),
        "invite": email_template(
            title="Welcome to Eskala! / ¡Bienvenido a Eskala!",
            content='''
            <div style="text-align: center;">
              <div style="background: #dbeafe; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 40px;">👋</span>
              </div>
              <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 16px 0;">
                An account has been created for you. Please click the button below to set your password and activate your account.
              </p>
              <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                Se ha creado una cuenta para ti. Haz clic en el botón para establecer tu contraseña y activar tu cuenta.
              </p>
              <div style="background: #fef3c7; border-radius: 8px; padding: 12px; margin-top: 20px;">
                <p style="color: #92400e; font-size: 14px; margin: 0;">
                  ⏰ This link expires in 72 hours / Este enlace expira en 72 horas
                </p>
              </div>
            </div>
            ''',
            button_text="Set Your Password / Establecer contraseña",
            button_url="/web/reset-password.html?token=preview-token"
        ),
        "verification": email_template(
            title="Verify Your Email / Verifica tu correo",
            content='''
            <div style="text-align: center;">
              <div style="background: #dbeafe; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 40px;">✉️</span>
              </div>
              <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 16px 0;">
                Thank you for signing up! Please verify your email address by clicking the button below.
              </p>
              <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                ¡Gracias por registrarte! Por favor verifica tu correo electrónico haciendo clic en el botón.
              </p>
              <div style="background: #fef3c7; border-radius: 8px; padding: 12px; margin: 20px 0;">
                <p style="color: #92400e; font-size: 14px; margin: 0;">
                  ⏰ This link expires in 24 hours / Este enlace expira en 24 horas
                </p>
              </div>
              <div style="background: #f0f9ff; border-left: 4px solid #2563eb; padding: 16px; margin-top: 20px; text-align: left; border-radius: 4px;">
                <p style="color: #1e40af; font-size: 14px; margin: 0;">
                  <strong>Note:</strong> After verifying your email, an administrator will need to approve your account before you can log in.<br><br>
                  <strong>Nota:</strong> Después de verificar tu correo, un administrador deberá aprobar tu cuenta antes de que puedas iniciar sesión.
                </p>
              </div>
            </div>
            ''',
            button_text="Verify Email / Verificar correo",
            button_url="/web/verify-email.html?token=preview-token"
        ),
        "password-reset": email_template(
            title="Password Reset / Restablecer contraseña",
            content='''
            <div style="text-align: center;">
              <div style="background: #fef3c7; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 40px;">🔑</span>
              </div>
              <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 16px 0;">
                You requested a password reset for your Eskala account. Click the button below to create a new password.
              </p>
              <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                Solicitaste restablecer tu contraseña de Eskala. Haz clic en el botón para crear una nueva contraseña.
              </p>
              <div style="background: #fef3c7; border-radius: 8px; padding: 12px; margin: 20px 0;">
                <p style="color: #92400e; font-size: 14px; margin: 0;">
                  ⏰ This link expires in 1 hour / Este enlace expira en 1 hora
                </p>
              </div>
              <p style="color: #9ca3af; font-size: 12px; margin-top: 20px;">
                If you didn't request this, please ignore this email. Your password will remain unchanged.<br>
                Si no solicitaste esto, ignora este correo. Tu contraseña no cambiará.
              </p>
            </div>
            ''',
            button_text="Reset Password / Restablecer contraseña",
            button_url="/web/reset-password.html?token=preview-token"
        ),
        "password-changed": email_template(
            title="Password Changed / Contraseña cambiada",
            content='''
            <div style="text-align: center;">
              <div style="background: #dcfce7; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 40px;">🔒</span>
              </div>
              <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 16px 0;">
                Your password has been successfully changed. You can now log in with your new password.
              </p>
              <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                Tu contraseña ha sido cambiada exitosamente. Ahora puedes iniciar sesión con tu nueva contraseña.
              </p>
              <div style="background: #fef2f2; border-left: 4px solid #dc2626; padding: 16px; margin-top: 20px; text-align: left; border-radius: 4px;">
                <p style="color: #991b1b; font-size: 14px; margin: 0;">
                  <strong>⚠️ Security Notice:</strong> If you didn't make this change, contact support immediately.<br><br>
                  <strong>⚠️ Aviso de seguridad:</strong> Si no realizaste este cambio, contacta a soporte inmediatamente.
                </p>
              </div>
            </div>
            '''
        )
    }
    
    if email_type not in previews:
        return jsonify(ok=False, error=f"Unknown email type. Available: {', '.join(previews.keys())}"), 404
    
    return Response(previews[email_type], mimetype='text/html')


def _hash_pw(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


# ============================================
# LIST USERS (with approval status)
# ============================================
@bp.get("/users")
def list_users():
    """List all users with their approval/verification status"""
    role = (request.args.get("role") or "").strip().upper()
    status = (request.args.get("status") or "").strip().lower()  # pending, approved, all
    
    q = """
      SELECT u.user_id, u.email, u.username, u.is_active, u.is_approved, 
             u.email_verified, u.created_at,
             r.role_name,
             sp.first_name AS staff_first, sp.last_name AS staff_last,
             cr.first_name AS partner_first, cr.last_name AS partner_last, 
             cr.title AS partner_title, cr.bank_name, cr.rtn_number
        FROM users u
        LEFT JOIN user_roles ur ON ur.user_id = u.user_id
        LEFT JOIN roles r ON r.role_id = ur.role_id
        LEFT JOIN staff_profile sp ON sp.user_id = u.user_id
        LEFT JOIN community_rep_profile cr ON cr.user_id = u.user_id
       WHERE 1=1
    """
    params = {}
    
    if role in ("STAFF", "COMMUNITY_REP"):
        q += " AND r.role_name = :role"
        params["role"] = role
    
    if status == "pending":
        q += " AND (u.is_approved = FALSE OR u.email_verified = FALSE)"
    elif status == "approved":
        q += " AND u.is_approved = TRUE AND u.email_verified = TRUE"
    
    q += " ORDER BY u.created_at DESC LIMIT 500"
    
    rows = run_query(q, **params).mappings().all()
    
    out = []
    for row in rows:
        first_name = row.get("staff_first") or row.get("partner_first") or ""
        last_name = row.get("staff_last") or row.get("partner_last") or ""
        title = row.get("partner_title") or ""
        
        # Determine status text
        if not row["email_verified"]:
            status_text = "Unverified"
        elif not row["is_approved"]:
            status_text = "Pending"
        elif not row["is_active"]:
            status_text = "Inactive"
        else:
            status_text = "Active"
        
        out.append({
            "user_id": row["user_id"],
            "email": row["email"],
            "username": row["username"],
            "role": row["role_name"],
            "is_active": int(row["is_active"]),
            "is_approved": int(row["is_approved"]),
            "email_verified": int(row["email_verified"]),
            "status": status_text,
            "created_at": str(row["created_at"]),
            "first_name": first_name,
            "last_name": last_name,
            "title": title,
            "name": (first_name + (" " + last_name if last_name else "")).strip(),
            "bank_name": row.get("bank_name"),
            "rtn_number": row.get("rtn_number")
        })
    
    return jsonify(ok=True, users=out)


# ============================================
# GET PENDING USERS (convenience endpoint)
# ============================================
@bp.get("/users/pending")
def list_pending_users():
    """List users pending approval (email verified but not approved)"""
    q = """
      SELECT u.user_id, u.email, u.username, u.is_active, u.is_approved, 
             u.email_verified, u.created_at,
             r.role_name,
             sp.first_name AS staff_first, sp.last_name AS staff_last,
             cr.first_name AS partner_first, cr.last_name AS partner_last, 
             cr.bank_name, cr.rtn_number
        FROM users u
        LEFT JOIN user_roles ur ON ur.user_id = u.user_id
        LEFT JOIN roles r ON r.role_id = ur.role_id
        LEFT JOIN staff_profile sp ON sp.user_id = u.user_id
        LEFT JOIN community_rep_profile cr ON cr.user_id = u.user_id
       WHERE u.email_verified = TRUE AND u.is_approved = FALSE
       ORDER BY u.created_at ASC
       LIMIT 100
    """
    
    rows = run_query(q).mappings().all()
    
    out = []
    for row in rows:
        name = row.get("staff_first") or row.get("partner_first") or ""
        last = row.get("staff_last") or row.get("partner_last") or ""
        
        out.append({
            "user_id": row["user_id"],
            "email": row["email"],
            "username": row["username"],
            "role": row["role_name"],
            "created_at": str(row["created_at"]),
            "name": (name + (" " + last if last else "")).strip(),
            "bank_name": row.get("bank_name"),
            "rtn_number": row.get("rtn_number")
        })
    
    return jsonify(ok=True, users=out, count=len(out))


# ============================================
# APPROVE USER
# ============================================
@bp.post("/users/<int:uid>/approve")
def approve_user(uid: int):
    """Approve a user account"""
    try:
        with SessionLocal() as s, s.begin():
            # Get user info and role
            user = s.execute(text("""
                SELECT u.email, u.username, u.is_approved, r.role_name
                FROM users u
                LEFT JOIN user_roles ur ON ur.user_id = u.user_id
                LEFT JOIN roles r ON r.role_id = ur.role_id
                WHERE u.user_id = :u
            """), {"u": uid}).first()
            
            if not user:
                return jsonify(ok=False, error="User not found"), 404
            
            if user.is_approved:
                return jsonify(ok=False, error="User is already approved"), 400
            
            # Approve the user
            s.execute(text("""
                UPDATE users SET is_approved = TRUE WHERE user_id = :u
            """), {"u": uid})
        
        # Determine login URL based on role
        print(f"🔍 User role: {user.role_name}")
        if user.role_name == "STAFF":
            login_url = f"{BASE_URL}/web/staff-login.html"
        elif user.role_name == "COMMUNITY_REP":
            login_url = f"{BASE_URL}/web/partner-login.html"
        else:
            # Default to partner login if role is unknown
            print(f"⚠️ Unknown role: {user.role_name}, defaulting to partner login")
            login_url = f"{BASE_URL}/web/partner-login.html"
        
        print(f"📧 Sending approval email to {user.email} with login URL: {login_url}")
        
        # Send approval notification email
        content = '''
        <div style="text-align: center;">
          <div style="background: #dcfce7; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 40px; color: #16a34a;">✓</span>
          </div>
          <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 16px 0;">
            <strong>Great news!</strong> Your Eskala account has been reviewed and approved. You now have full access to the platform.
          </p>
          <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0;">
            <strong>¡Excelentes noticias!</strong> Tu cuenta de Eskala ha sido revisada y aprobada. Ahora tienes acceso completo a la plataforma.
          </p>
        </div>
        '''
        
        send_email(
            to_email=user.email,
            subject="Eskala - Account Approved! / ¡Cuenta aprobada!",
            html_body=email_template(
                title="Account Approved! / ¡Cuenta aprobada!",
                content=content,
                button_text="Log In to Your Account / Iniciar sesión",
                button_url=login_url,
                button_color="#166534"
            )
        )
        
        return jsonify(ok=True, message="User approved successfully")
        
    except Exception as e:
        print(f"❌ Approve user error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error=friendly_error(e)), 500


# ============================================
# REJECT USER
# ============================================
@bp.post("/users/<int:uid>/reject")
def reject_user(uid: int):
    """Reject a user account (deletes the account)"""
    body = request.get_json(silent=True) or {}
    reason = (body.get("reason") or "").strip()
    
    try:
        with SessionLocal() as s, s.begin():
            # Get user info first
            user = s.execute(text("""
                SELECT email, username FROM users WHERE user_id = :u
            """), {"u": uid}).first()
            
            if not user:
                return jsonify(ok=False, error="User not found"), 404
            
            user_email = user.email
            
            # Delete the user and related records
            s.execute(text("DELETE FROM community_rep_profile WHERE user_id = :u"), {"u": uid})
            s.execute(text("DELETE FROM staff_profile WHERE user_id = :u"), {"u": uid})
            s.execute(text("DELETE FROM user_roles WHERE user_id = :u"), {"u": uid})
            s.execute(text("DELETE FROM users WHERE user_id = :u"), {"u": uid})
        
        # Send rejection notification email
        reason_html = ""
        if reason:
            reason_html = f'''
            <div style="background: #fef2f2; border-left: 4px solid #dc2626; padding: 16px; margin: 20px 0; border-radius: 4px;">
              <p style="color: #991b1b; margin: 0 0 8px 0; font-weight: 600;">Reason / Razón:</p>
              <p style="color: #7f1d1d; margin: 0;">{reason}</p>
            </div>
            '''
        
        content = f'''
        <div style="text-align: center;">
          <div style="background: #fee2e2; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 40px; color: #dc2626;">✗</span>
          </div>
          <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 16px 0;">
            We're sorry, but your account application was not approved at this time.
          </p>
          <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0;">
            Lo sentimos, pero tu solicitud de cuenta no fue aprobada en este momento.
          </p>
          {reason_html}
          <p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
            If you believe this is an error, please contact support.<br>
            Si crees que esto es un error, por favor contacta a soporte.
          </p>
        </div>
        '''
        
        send_email(
            to_email=user_email,
            subject="Eskala - Account Application Update / Actualización de solicitud",
            html_body=email_template(
                title="Application Not Approved / Solicitud no aprobada",
                content=content
            )
        )
        
        return jsonify(ok=True, message="User rejected and removed")
        
    except Exception as e:
        print(f"❌ Reject user error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error=friendly_error(e)), 500


# ============================================
# TOGGLE ACTIVE STATUS
# ============================================
@bp.post("/users/<int:uid>/toggle-active")
def toggle_active(uid: int):
    """Toggle a user's active status (activate/deactivate)"""
    try:
        with SessionLocal() as s, s.begin():
            user = s.execute(text("""
                SELECT is_active FROM users WHERE user_id = :u
            """), {"u": uid}).first()
            
            if not user:
                return jsonify(ok=False, error="User not found"), 404
            
            new_status = not user.is_active
            s.execute(text("""
                UPDATE users SET is_active = :status WHERE user_id = :u
            """), {"status": new_status, "u": uid})
        
        return jsonify(ok=True, is_active=new_status, 
                       message=f"User {'activated' if new_status else 'deactivated'}")
        
    except Exception as e:
        print(f"❌ Toggle active error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error=friendly_error(e)), 500


# ============================================
# CREATE USER (admin-created = invite flow)
# ============================================
@bp.post("/users")
def create_user():
    """
    Create a user (admin-created users are auto-approved).
    User receives email with link to set their own password.
    """
    import secrets
    from datetime import datetime, timedelta
    
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    acct = (body.get("account_type") or "COMMUNITY_REP").upper()
    prof = body.get("profile") or {}
    
    if not email:
        return jsonify(ok=False, error="Email is required"), 400
    if acct not in ("STAFF", "COMMUNITY_REP"):
        return jsonify(ok=False, error="account_type must be STAFF or COMMUNITY_REP"), 400
    
    # Check if email already exists
    existing_email = run_query("SELECT 1 FROM users WHERE email = :e LIMIT 1", e=email).first()
    if existing_email:
        return jsonify(ok=False, error="This email address is already registered."), 409
    
    rtn = (prof.get("rtn_number") or "").strip()
    if acct == "COMMUNITY_REP" and rtn:
        if run_query("SELECT 1 FROM community_rep_profile WHERE rtn_number=:r LIMIT 1", r=rtn).first():
            return jsonify(ok=False, error="This RTN number is already in use."), 409
    
    # Generate a "set password" token (like password reset)
    set_password_token = secrets.token_urlsafe(32)
    token_expiry = datetime.utcnow() + timedelta(hours=72)  # 3 days to set password
    
    # Create a placeholder password hash (user cannot log in with this)
    placeholder_hash = "INVITE_PENDING"
    
    # Base username from email
    base_username = email.split("@")[0] if email else ""
    
    try:
        with SessionLocal() as s, s.begin():
            # Generate unique username
            username = generate_unique_username(s, base_username)
            
            # Admin-created users are auto-approved and email-verified, but need to set password
            uid = s.execute(text("""
                INSERT INTO users (email, username, password_hash, is_active, is_approved, email_verified,
                                   reset_token, reset_token_expiry)
                VALUES (:e, :u, :h, TRUE, TRUE, TRUE, :token, :expiry)
            """), {
                "e": email,
                "u": username,
                "h": placeholder_hash,
                "token": set_password_token,
                "expiry": token_expiry
            }).lastrowid
            
            # Role
            rid = s.execute(text("SELECT role_id FROM roles WHERE role_name=:n"),
                            {"n": acct}).scalar_one()
            s.execute(text("INSERT INTO user_roles (user_id, role_id) VALUES (:u,:r)"),
                      {"u": uid, "r": rid})
            
            # Profile
            if acct == "COMMUNITY_REP":
                s.execute(text("""
                    INSERT INTO community_rep_profile
                    (user_id, first_name, last_name, title, bank_name, rtn_number)
                    VALUES (:u, :fn, :ln, :t, :b, :rtn)
                """), {
                    "u": uid,
                    "fn": prof.get("first_name") or None,
                    "ln": prof.get("last_name") or None,
                    "t": prof.get("title") or None,
                    "b": prof.get("bank_name") or None,
                    "rtn": rtn or None
                })
            else:
                s.execute(text("""
                    INSERT INTO staff_profile (user_id, first_name, last_name)
                    VALUES (:u, :fn, :ln)
                """), {
                    "u": uid,
                    "fn": prof.get("first_name") or None,
                    "ln": prof.get("last_name") or None
                })
        
        # Send invite email with "Set Your Password" link
        set_password_url = f"{BASE_URL}/web/reset-password.html?token={set_password_token}"
        
        content = '''
        <div style="text-align: center;">
          <div style="background: #dbeafe; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 40px;">👋</span>
          </div>
          <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 16px 0;">
            An account has been created for you. Please click the button below to set your password and activate your account.
          </p>
          <p style="color: #374151; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
            Se ha creado una cuenta para ti. Haz clic en el botón para establecer tu contraseña y activar tu cuenta.
          </p>
          <div style="background: #fef3c7; border-radius: 8px; padding: 12px; margin-top: 20px;">
            <p style="color: #92400e; font-size: 14px; margin: 0;">
              ⏰ This link expires in 72 hours / Este enlace expira en 72 horas
            </p>
          </div>
        </div>
        '''
        
        send_email(
            to_email=email,
            subject="Eskala - Welcome! Set Up Your Account / ¡Bienvenido! Configura tu cuenta",
            html_body=email_template(
                title="Welcome to Eskala! / ¡Bienvenido a Eskala!",
                content=content,
                button_text="Set Your Password / Establecer contraseña",
                button_url=set_password_url
            )
        )
        
        return jsonify(ok=True, user_id=uid, message="User created. Invite email sent.")
        
    except Exception as e:
        print(f"❌ CREATE USER ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error=friendly_error(e)), 500


# ============================================
# DELETE USER
# ============================================
@bp.delete("/users/<int:uid>")
def delete_user(uid: int):
    """Hard delete a user"""
    try:
        with SessionLocal() as s, s.begin():
            # Remove child rows first
            s.execute(text("DELETE FROM community_rep_profile WHERE user_id=:u"), {"u": uid})
            s.execute(text("DELETE FROM staff_profile WHERE user_id=:u"), {"u": uid})
            s.execute(text("DELETE FROM user_roles WHERE user_id=:u"), {"u": uid})
            # Finally the user
            n = s.execute(text("DELETE FROM users WHERE user_id=:u"), {"u": uid}).rowcount
        
        if n == 0:
            return jsonify(ok=False, error="not found"), 404
        
        return jsonify(ok=True)
        
    except Exception as e:
        print(f"❌ DELETE USER ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(ok=False, error=friendly_error(e)), 500