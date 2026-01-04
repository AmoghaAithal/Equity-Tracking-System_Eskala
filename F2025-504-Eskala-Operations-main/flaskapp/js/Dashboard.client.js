// Load user name on page load
async function loadUserName() {
  try {
    const response = await fetch('/api/user/info', {
      credentials: 'include'
    });
    const data = await response.json();
    
    if (data.ok && data.first_name) {
      const welcomeEl = document.getElementById('welcome');
      if (welcomeEl) {
        const fullName = data.last_name ? `${data.first_name} ${data.last_name}` : data.first_name;
        welcomeEl.textContent = `Welcome, ${fullName}!`;
      }
    }
  } catch (error) {
    console.error('Error loading user name:', error);
  }
}

// Run immediately when script loads
setTimeout(loadUserName, 100);
