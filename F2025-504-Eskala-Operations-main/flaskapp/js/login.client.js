// web/js/login.client.js
(function () {
  const { qs, postJSON } = window.api || {};
  const LANG_KEY = 'eskala_lang';

  function getLang() {
    try { return localStorage.getItem(LANG_KEY) || 'en'; }
    catch { return 'en'; }
  }

  function toast(msg) { alert(msg); }
  const isPartnerPage = () => !!qs("#rtn-number");

  // ---- Status message display ----
  function showStatus(message, type) {
    // type: 'error', 'info', 'success'
    let status = document.querySelector('.login-status');
    if (!status) {
      status = document.createElement('div');
      status.className = 'login-status';
      status.style.cssText = `
        padding: 12px 16px;
        margin: 16px 0;
        border-radius: 6px;
        font-size: 14px;
        text-align: center;
      `;
      const form = document.getElementById('login-form');
      if (form) {
        form.parentNode.insertBefore(status, form.nextSibling);
      }
    }
    
    if (type === 'error') {
      status.style.background = '#fee2e2';
      status.style.color = '#991b1b';
    } else if (type === 'info') {
      status.style.background = '#fef3c7';
      status.style.color = '#92400e';
    } else {
      status.style.background = '#dcfce7';
      status.style.color = '#166534';
    }
    
    status.style.display = 'block';
    status.innerHTML = message;
  }

  function clearStatus() {
    const status = document.querySelector('.login-status');
    if (status) status.style.display = 'none';
  }

  function getEls() {
    if (isPartnerPage()) {
      return {
        type: "partner",
        submitBtn: qs(".login-button") || qs(".sign-in-button"),
        rtn: qs("#rtn-number"),
        password: qs("#password"),
      };
    }
    return {
      type: "staff",
      submitBtn: qs(".sign-in-button") || qs(".login-button"),
      email: qs("#email"),
      password: qs("#password"),
    };
  }

  async function partnerLogin({ rtn, password }) {
    const rtnVal = (rtn?.value || "").trim();
    const pw = password?.value || "";
    if (!rtnVal || !pw) throw new Error("Please enter RTN and password.");
    // Use the partner login endpoint directly
    return postJSON("/api/auth/login-partner", { rtn: rtnVal, password: pw });
  }

  async function staffLogin({ email, password }) {
    const mail = (email?.value || "").trim();
    const pw = password?.value || "";
    if (!mail || !pw) throw new Error("Please enter email and password.");
    return postJSON("/api/auth/login", { email_or_username: mail, password: pw });
  }

  // Redirect to Dashboard after successful login
  function routeAfterLogin(role) {
    // Both staff and partners go to the same dashboard
    // The dashboard handles showing/hiding features based on role
    window.location.href = '/web/Dashboard.html';
  }

  // ---- Add forgot password link ----
  function addForgotPasswordLink() {
    const form = document.getElementById('login-form');
    if (!form) return;

    // Check if link already exists
    if (document.querySelector('.forgot-password-link')) return;

    const lang = getLang();
    
    // Determine which login page we're on
    const isPartner = isPartnerPage();
    const fromParam = isPartner ? 'partner' : 'staff';
    
    const link = document.createElement('p');
    link.className = 'forgot-password-link';
    link.style.cssText = 'text-align: center; margin-top: 16px; font-size: 14px;';
    link.innerHTML = `
      <a href="/web/forgot-password.html?from=${fromParam}" style="color: #2563eb; text-decoration: none;">
        ${lang === 'es' ? '¿Olvidaste tu contraseña?' : 'Forgot your password?'}
      </a>
    `;

    // Insert after the auth-helper div or after form
    const authHelper = form.parentNode.querySelector('.auth-helper');
    if (authHelper) {
      authHelper.parentNode.insertBefore(link, authHelper.nextSibling);
    } else {
      form.parentNode.insertBefore(link, form.nextSibling);
    }
  }

  // ---- Resend verification email ----
  window.resendVerification = async function () {
    const lang = getLang();
    const email = prompt(lang === 'es' ? 'Ingresa tu correo electrónico:' : 'Enter your email address:');
    
    if (!email) return;

    try {
      const res = await postJSON('/api/auth/resend-verification', { email: email.trim().toLowerCase() });
      
      alert(res?.message || (lang === 'es' 
        ? 'Si el correo está registrado, recibirás un enlace de verificación.'
        : 'If the email is registered, you will receive a verification link.'));
    } catch (err) {
      console.error('Resend verification error:', err);
      alert(lang === 'es' ? 'Error al enviar correo.' : 'Failed to send email.');
    }
  };

  function wireLogin() {
    if (!window.api) return;
    const els = getEls();
    if (!els.submitBtn) return;

    // Add forgot password link
    addForgotPasswordLink();

    let busy = false;
    els.submitBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      if (busy) return;
      busy = true;
      clearStatus();

      const lang = getLang();

      try {
        const data = (els.type === "partner")
          ? await partnerLogin(els)
          : await staffLogin(els);

        if (!data || data.ok !== true) {
          // Handle specific error cases
          if (data?.needs_verification) {
            showStatus(`
              ${lang === 'es' 
                ? 'Por favor verifica tu correo electrónico primero.' 
                : 'Please verify your email address first.'}
              <br><br>
              <a href="#" onclick="resendVerification(); return false;" style="color: #92400e; text-decoration: underline;">
                ${lang === 'es' ? 'Reenviar correo de verificación' : 'Resend verification email'}
              </a>
            `, 'info');
            return;
          } else if (data?.pending_approval) {
            showStatus(
              lang === 'es'
                ? 'Tu cuenta está pendiente de aprobación. Un administrador la revisará pronto.'
                : 'Your account is pending approval. An administrator will review it shortly.',
              'info'
            );
            return;
          } else if (data?.needs_password_setup) {
            showStatus(
              lang === 'es'
                ? 'Por favor revisa tu correo electrónico y establece tu contraseña primero.'
                : 'Please check your email and set your password first.',
              'info'
            );
            return;
          }
          throw new Error(data?.error || "Invalid credentials");
        }

        // Redirect based on user role from response
        const userRole = data.user?.role || (els.type === "partner" ? "COMMUNITY_REP" : "STAFF");
        routeAfterLogin(userRole);
      } catch (err) {
        console.error(err);
        showStatus(err.message || "Login failed", 'error');
      } finally {
        busy = false;
      }
    });
  }

  document.addEventListener("DOMContentLoaded", wireLogin);
})();