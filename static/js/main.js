/**
 * CrimeConnect - Frontend Interactions & Utilities
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Theme Management (Light / Dark Mode)
  initThemeToggle();

  // 2. Mobile Navigation Toggle
  initMobileNav();

  // 3. Flash Alert Dismissal
  initAlertDismissal();

  // 4. Quick Demo Login Credentials
  initDemoCredentials();

  // 5. Copy Reference Number to Clipboard
  initCopyReference();

  // 6. Character Counters for Forms
  initCharacterCounters();

  // 7. Form Submission Loading State
  initFormLoading();
});

function initThemeToggle() {
  const toggleBtn = document.getElementById('themeToggleBtn');
  const themeIcon = document.getElementById('themeIcon');
  const storedTheme = localStorage.getItem('crimeconnect_theme') || 'light';

  document.documentElement.setAttribute('data-theme', storedTheme);
  updateThemeIcon(storedTheme);

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('crimeconnect_theme', newTheme);
      updateThemeIcon(newTheme);
    });
  }

  function updateThemeIcon(theme) {
    if (!themeIcon) return;
    if (theme === 'dark') {
      themeIcon.className = 'fa-solid fa-sun';
      themeIcon.title = 'Switch to Light Mode';
    } else {
      themeIcon.className = 'fa-solid fa-moon';
      themeIcon.title = 'Switch to Dark Mode';
    }
  }
}

function initMobileNav() {
  const toggle = document.querySelector('.mobile-menu-toggle');
  const navLinks = document.querySelector('.nav-links');

  if (toggle && navLinks) {
    toggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      const isOpen = navLinks.classList.contains('open');
      toggle.innerHTML = isOpen ? '<i class="fa-solid fa-xmark"></i>' : '<i class="fa-solid fa-bars"></i>';
    });
  }
}

function initAlertDismissal() {
  const closeBtns = document.querySelectorAll('.alert-close');
  closeBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const alert = e.target.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        alert.style.transition = 'all 0.3s ease';
        setTimeout(() => alert.remove(), 300);
      }
    });
  });

  // Auto-dismiss success alerts after 6 seconds
  const autoAlerts = document.querySelectorAll('.alert-success');
  autoAlerts.forEach(alert => {
    setTimeout(() => {
      if (alert && alert.parentElement) {
        alert.style.opacity = '0';
        alert.style.transition = 'all 0.5s ease';
        setTimeout(() => alert.remove(), 500);
      }
    }, 6000);
  });
}

function initDemoCredentials() {
  const adminBtn = document.getElementById('demoAdminBtn');
  const citizenBtn = document.getElementById('demoCitizenBtn');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');

  if (adminBtn && emailInput && passwordInput) {
    adminBtn.addEventListener('click', () => {
      emailInput.value = 'admin@crimeconnect.local';
      passwordInput.value = 'Admin@123';
      emailInput.focus();
    });
  }

  if (citizenBtn && emailInput && passwordInput) {
    citizenBtn.addEventListener('click', () => {
      emailInput.value = 'citizen@crimeconnect.local';
      passwordInput.value = 'Citizen@123';
      emailInput.focus();
    });
  }
}

function initCopyReference() {
  const copyBtn = document.getElementById('copyRefBtn');
  const refCodeEl = document.getElementById('refCode');

  if (copyBtn && refCodeEl) {
    copyBtn.addEventListener('click', () => {
      const textToCopy = refCodeEl.innerText.trim();
      navigator.clipboard.writeText(textToCopy).then(() => {
        const originalHtml = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
        copyBtn.classList.remove('btn-outline');
        copyBtn.classList.add('btn-primary');

        setTimeout(() => {
          copyBtn.innerHTML = originalHtml;
          copyBtn.classList.remove('btn-primary');
          copyBtn.classList.add('btn-outline');
        }, 2500);
      }).catch(err => {
        console.error('Failed to copy code: ', err);
      });
    });
  }
}

function initCharacterCounters() {
  const descArea = document.getElementById('description');
  const countDisplay = document.getElementById('charCount');

  if (descArea && countDisplay) {
    const updateCount = () => {
      const len = descArea.value.length;
      countDisplay.innerText = `${len} characters (minimum 20)`;
      if (len < 20) {
        countDisplay.style.color = 'var(--crimson-red)';
      } else {
        countDisplay.style.color = 'var(--success-green)';
      }
    };
    descArea.addEventListener('input', updateCount);
    updateCount();
  }
}

function initFormLoading() {
  const forms = document.querySelectorAll('form.needs-loading-feedback');
  forms.forEach(form => {
    form.addEventListener('submit', () => {
      const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
      if (submitBtn && !submitBtn.disabled) {
        submitBtn.setAttribute('data-orig-text', submitBtn.innerHTML || submitBtn.value);
        if (submitBtn.tagName.toLowerCase() === 'input') {
          submitBtn.value = 'Processing...';
        } else {
          submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Processing...';
        }
        submitBtn.style.opacity = '0.7';
      }
    });
  });
}
