'use strict';

const App = {

  currentUser: null,
  currentPage: 'auth',
  currentDay:  null,

  settings: {
    theme:    'light',
    textSize: 16   // px — numeric, clamped 12–22
  },

  TEXT_MIN: 12,
  TEXT_MAX: 22,
  TEXT_STEP: 1,

  pages: {
    auth:      'page-auth',
    dashboard: 'page-dashboard',
    meals:     'page-meals',
    shopping:  'page-shopping'
  },

  init() {
    this.loadSettings();
    this.applySettings();
    this.initNav();
    this.initSettings();
    this.initModals();
    this.checkAuth();
  },

  /* ── Storage ── */
  getUsers() {
    try { return JSON.parse(localStorage.getItem('hn_users') || '[]'); } catch { return []; }
  },
  saveUsers(u) { localStorage.setItem('hn_users', JSON.stringify(u)); },

  getCurrentUser() {
    const id = localStorage.getItem('hn_current');
    if (!id) return null;
    return this.getUsers().find(u => u.id === id) || null;
  },
  saveCurrentUser(user) {
    const users = this.getUsers();
    const idx   = users.findIndex(u => u.id === user.id);
    if (idx >= 0) users[idx] = user; else users.push(user);
    this.saveUsers(users);
    this.currentUser = user;
  },

  getMeals(uid) {
    try { return JSON.parse(localStorage.getItem(`hn_meals_${uid}`) || '{}'); } catch { return {}; }
  },
  saveMeals(uid, m) { localStorage.setItem(`hn_meals_${uid}`, JSON.stringify(m)); },

  getShoppingList(uid) {
    try { return JSON.parse(localStorage.getItem(`hn_shop_${uid}`) || '[]'); } catch { return []; }
  },
  saveShoppingList(uid, l) { localStorage.setItem(`hn_shop_${uid}`, JSON.stringify(l)); },

  loadSettings() {
    try {
      const s = JSON.parse(localStorage.getItem('hn_settings') || '{}');
      this.settings = { ...this.settings, ...s };
      // Ensure numeric
      this.settings.textSize = Number(this.settings.textSize) || 16;
    } catch {}
  },
  saveSettingsStore() { localStorage.setItem('hn_settings', JSON.stringify(this.settings)); },

  /* ── Apply theme + font size ── */
  applySettings() {
    // Theme
    document.body.classList.toggle('dark-theme',  this.settings.theme === 'dark');
    document.body.classList.toggle('light-theme', this.settings.theme !== 'dark');

    // Font size — set CSS custom property on :root
    const size = Math.min(Math.max(this.settings.textSize, this.TEXT_MIN), this.TEXT_MAX);
    document.documentElement.style.setProperty('--base-font-size', `${size}px`);

    // Sync slider UI
    const slider = document.getElementById('font-size-slider');
    if (slider) slider.value = size;

    // Sync label
    const label = document.getElementById('font-size-label');
    if (label) label.textContent = `${size}px`;

    // Sync theme buttons
    document.querySelectorAll('.theme-option').forEach(b =>
      b.classList.toggle('active', b.dataset.theme === this.settings.theme));

    // Disable step buttons at limits
    const btnDec = document.getElementById('font-dec');
    const btnInc = document.getElementById('font-inc');
    if (btnDec) btnDec.disabled = size <= this.TEXT_MIN;
    if (btnInc) btnInc.disabled = size >= this.TEXT_MAX;
  },

  checkAuth() {
    const user = this.getCurrentUser();
    if (user) { this.currentUser = user; this.navigateTo('dashboard'); }
    else       { this.navigateTo('auth'); }
  },

  /* ── Navigation ── */
  navigateTo(page) {
    Object.values(this.pages).forEach(pid => {
      const el = document.getElementById(pid);
      if (el) { el.classList.add('hidden'); el.classList.remove('active'); }
    });
    const target = document.getElementById(this.pages[page]);
    if (target) { target.classList.remove('hidden'); target.classList.add('active'); }

    this.currentPage = page;
    this._syncNav(page);

    switch (page) {
      case 'dashboard': Dashboard.render();  break;
      case 'meals':     Meals.render();      break;
      case 'shopping':  Shopping.render();   break;
    }

    if (target) {
      const sc = target.querySelector('.dashboard-content,.meals-content,.shopping-content');
      if (sc) sc.scrollTop = 0;
    }
  },

  _syncNav(page) {
    document.querySelectorAll('.nav-item').forEach(item =>
      item.classList.toggle('active', item.dataset.page === page));
  },

  initNav() {
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', () => {
        const p = item.dataset.page;
        if (p === 'meals' && !this.currentDay) {
          this.showToast('Select a day from Home first 📅', '📅'); return;
        }
        this.navigateTo(p);
      });
    });
    document.getElementById('meals-back-btn')
      ?.addEventListener('click', () => this.navigateTo('dashboard'));
    document.getElementById('shopping-back-btn')
      ?.addEventListener('click', () => this.navigateTo('dashboard'));
  },

  /* ── Settings panel ── */
  initSettings() {
    const overlay = document.getElementById('settings-overlay');

    ['dash-settings-btn','meals-settings-btn','shopping-settings-btn'].forEach(id =>
      document.getElementById(id)?.addEventListener('click', () => this.openSettings()));

    document.getElementById('settings-close')
      ?.addEventListener('click', () => this.closeSettings());
    overlay?.addEventListener('click', () => this.closeSettings());

    // Theme
    document.querySelectorAll('.theme-option').forEach(btn =>
      btn.addEventListener('click', () => {
        this.settings.theme = btn.dataset.theme;
        this.saveSettingsStore();
        this.applySettings();
        //this.showToast(this.settings.theme === 'dark' ? '🌙 Dark theme' : '☀️ Light theme');
      }));

    // ── Font size: SLIDER ──
    const slider = document.getElementById('font-size-slider');
    slider?.addEventListener('input', () => {
      this.settings.textSize = Number(slider.value);
      this.saveSettingsStore();
      this.applySettings();
    });

    // ── Font size: STEP buttons ──
    document.getElementById('font-dec')?.addEventListener('click', () => {
      const cur = Math.max(Number(this.settings.textSize) - this.TEXT_STEP, this.TEXT_MIN);
      this.settings.textSize = cur;
      this.saveSettingsStore();
      this.applySettings();
    });
    document.getElementById('font-inc')?.addEventListener('click', () => {
      const cur = Math.min(Number(this.settings.textSize) + this.TEXT_STEP, this.TEXT_MAX);
      this.settings.textSize = cur;
      this.saveSettingsStore();
      this.applySettings();
    });

    // Avatar
    const avatarUpload = document.getElementById('avatar-upload');
    document.getElementById('avatar-edit-btn')
      ?.addEventListener('click', () => avatarUpload?.click());
    document.getElementById('btn-change-photo')
      ?.addEventListener('click', () => avatarUpload?.click());
    avatarUpload?.addEventListener('change', e => {
      const file = e.target.files[0];
      if (!file || !this.currentUser) return;
      const reader = new FileReader();
      reader.onload = ev => {
        this.currentUser.avatar = ev.target.result;
        this.saveCurrentUser(this.currentUser);
        this._refreshAvatars();
        //this.showToast('Profile photo updated ✓');
      };
      reader.readAsDataURL(file);
      e.target.value = '';
    });

    // Change username
    document.getElementById('btn-change-username')?.addEventListener('click', () => {
      document.getElementById('new-username-input').value = '';
      document.getElementById('err-new-username').textContent = '';
      this.openModal('modal-change-username');
    });
    document.getElementById('btn-save-username')?.addEventListener('click', () => {
      const val   = document.getElementById('new-username-input').value.trim();
      const errEl = document.getElementById('err-new-username');
      if (!val)         { errEl.textContent = 'Username cannot be empty.';      return; }
      if (val.length<3) { errEl.textContent = 'Minimum 3 characters required.'; return; }
      if (this.getUsers().some(u => u.username === val && u.id !== this.currentUser.id))
                        { errEl.textContent = 'Username already taken.';         return; }
      this.currentUser.username = val;
      this.saveCurrentUser(this.currentUser);
      this.updateSettingsProfile();
      this.closeModal('modal-change-username');
      //this.showToast('Username updated ✓');
    });

    // Switch account
    document.getElementById('btn-switch-account')?.addEventListener('click', () => {
      localStorage.removeItem('hn_current');
      this.currentUser = null; this.currentDay = null;
      this.closeSettings(); this.navigateTo('auth');
      //this.showToast('Switched account 🔄', '🔄');
    });

    // Delete account
    document.getElementById('btn-delete-account')?.addEventListener('click', () => {
      document.getElementById('delete-confirm-pass').value = '';
      document.getElementById('err-delete-pass').textContent = '';
      this.openModal('modal-delete-account');
    });
    document.getElementById('btn-confirm-delete')?.addEventListener('click', () => {
      const pass  = document.getElementById('delete-confirm-pass').value;
      const errEl = document.getElementById('err-delete-pass');
      if (!pass)                              { errEl.textContent = 'Enter your password.';  return; }
      if (pass !== this.currentUser.password) { errEl.textContent = 'Incorrect password.';  return; }
      let users = this.getUsers().filter(u => u.id !== this.currentUser.id);
      this.saveUsers(users);
      localStorage.removeItem(`hn_meals_${this.currentUser.id}`);
      localStorage.removeItem(`hn_shop_${this.currentUser.id}`);
      localStorage.removeItem('hn_current');
      this.currentUser = null; this.currentDay = null;
      this.closeModal('modal-delete-account');
      this.closeSettings(); this.navigateTo('auth');
      //this.showToast('Account deleted 🗑️', '🗑️');
    });

    // Sign out
    document.getElementById('btn-signout')?.addEventListener('click', () => {
      localStorage.removeItem('hn_current');
      this.currentUser = null; this.currentDay = null;
      this.closeSettings(); this.navigateTo('auth');
      //this.showToast('Signed out ✓');
    });
  },

  openSettings() {
    this.updateSettingsProfile();
    this.applySettings();   // sync slider/buttons to current values
    document.getElementById('settings-overlay')?.classList.remove('hidden');
    const panel = document.getElementById('settings-panel');
    panel?.classList.remove('hidden');
    requestAnimationFrame(() => panel?.classList.add('show'));
  },

  closeSettings() {
    const panel = document.getElementById('settings-panel');
    panel?.classList.remove('show');
    setTimeout(() => {
      panel?.classList.add('hidden');
      document.getElementById('settings-overlay')?.classList.add('hidden');
    }, 380);
  },

  updateSettingsProfile() {
    if (!this.currentUser) return;
    document.getElementById('settings-display-name').textContent  = this.currentUser.name;
    document.getElementById('settings-display-username').textContent = '@' + this.currentUser.username;
    const av = document.getElementById('settings-avatar');
    if (av) av.innerHTML = this.currentUser.avatar
      ? `<img src="${this.currentUser.avatar}" alt="avatar" />`
      : this.currentUser.name.charAt(0).toUpperCase();
  },

  _refreshAvatars() {
    const dashAv = document.getElementById('dash-avatar');
    if (dashAv && this.currentUser) {
      dashAv.innerHTML = this.currentUser.avatar
        ? `<img src="${this.currentUser.avatar}" alt="avatar" />`
        : this.currentUser.name.charAt(0).toUpperCase();
    }
    this.updateSettingsProfile();
  },

  /* ── Modals ── */
  initModals() {
    document.querySelectorAll('.modal .modal-overlay').forEach(ov =>
      ov.addEventListener('click', () => {
        const m = ov.closest('.modal');
        if (m) this.closeModal(m.id);
      }));
    document.querySelectorAll('.modal-close').forEach(btn =>
      btn.addEventListener('click', () => {
        if (btn.dataset.modal) this.closeModal(btn.dataset.modal);
      }));
    document.querySelectorAll('.toggle-pass').forEach(btn =>
      btn.addEventListener('click', () => {
        const inp = document.getElementById(btn.dataset.target);
        if (!inp) return;
        inp.type = inp.type === 'password' ? 'text' : 'password';
        btn.textContent = inp.type === 'password' ? '👁️' : '🙈';
      }));
  },

  openModal(id)  { document.getElementById(id)?.classList.remove('hidden'); },
  closeModal(id) { document.getElementById(id)?.classList.add('hidden'); },

  /* ── Toast ── */
  showToast(msg, icon = '✅') {
    const toast = document.getElementById('toast');
    const msgEl = document.getElementById('toast-message');
    const icEl  = document.getElementById('toast-icon');
    if (!toast) return;
    msgEl.textContent = msg;
    icEl.textContent  = icon;
    toast.classList.remove('hidden');
    requestAnimationFrame(() => toast.classList.add('show'));
    clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.classList.add('hidden'), 320);
    }, 2600);
  },

  showLoading()  { document.getElementById('loading-spinner')?.classList.remove('hidden'); },
  hideLoading()  { document.getElementById('loading-spinner')?.classList.add('hidden'); },
  genId()        { return Date.now().toString(36) + Math.random().toString(36).substr(2,6); }
};

document.addEventListener('DOMContentLoaded', () => App.init());