'use strict';

const Auth = {

  init() {
    this._bindTabs();
    this._bindForms();
  },

  _bindTabs() {
    // Tab buttons and inline "Sign Up / Sign In" links
    document.querySelectorAll('.auth-tab, .auth-link').forEach(el => {
      el.addEventListener('click', () => {
        const tab = el.dataset.tab;
        if (tab) this.switchTab(tab);
      });
    });
  },

  switchTab(tab) {
    document.querySelectorAll('.auth-tab').forEach(t =>
      t.classList.toggle('active', t.dataset.tab === tab));

    const showSignIn = tab === 'signin';
    document.getElementById('signin-form')?.classList.toggle('hidden', !showSignIn);
    document.getElementById('signup-form')?.classList.toggle('hidden',  showSignIn);

    // Clear all validation errors
    document.querySelectorAll('.form-error').forEach(e => { e.textContent = ''; });
  },

  _bindForms() {
    document.getElementById('form-signin')
      ?.addEventListener('submit', e => { e.preventDefault(); this._signIn(); });

    document.getElementById('form-signup')
      ?.addEventListener('submit', e => { e.preventDefault(); this._signUp(); });
  },

  _signIn() {
    const username = document.getElementById('signin-username').value.trim();
    const password = document.getElementById('signin-password').value;

    document.getElementById('err-signin-username').textContent = '';
    document.getElementById('err-signin-password').textContent = '';

    let ok = true;
    if (!username) { document.getElementById('err-signin-username').textContent = 'Username is required.'; ok = false; }
    if (!password) { document.getElementById('err-signin-password').textContent = 'Password is required.';  ok = false; }
    if (!ok) return;

    App.showLoading();
    setTimeout(() => {
      App.hideLoading();
      const user = App.getUsers().find(u => u.username === username && u.password === password);
      if (!user) {
        document.getElementById('err-signin-password').textContent = 'Invalid username or password.';
        return;
      }
      localStorage.setItem('hn_current', user.id);
      App.currentUser = user;
      //App.showToast(`Welcome back, ${user.name}! 👋`);
      App.navigateTo('dashboard');
    }, 700);
  },

  _signUp() {
    const name     = document.getElementById('signup-name').value.trim();
    const username = document.getElementById('signup-username').value.trim();
    const dob      = document.getElementById('signup-dob').value;
    const password = document.getElementById('signup-password').value;
    const confirm  = document.getElementById('signup-confirm').value;

    // Clear errors
    ['name','username','dob','password','confirm'].forEach(f =>
      document.getElementById(`err-signup-${f}`).textContent = '');

    let ok = true;

    if (!name)           { document.getElementById('err-signup-name').textContent     = 'Full name is required.';              ok = false; }
    if (!username)       { document.getElementById('err-signup-username').textContent = 'Username is required.';               ok = false; }
    else if (username.length < 3)
                         { document.getElementById('err-signup-username').textContent = 'Minimum 3 characters.';               ok = false; }
    else {
      const taken = App.getUsers().some(u => u.username === username);
      if (taken)         { document.getElementById('err-signup-username').textContent = 'Username already taken.';             ok = false; }
    }
    if (!dob)            { document.getElementById('err-signup-dob').textContent      = 'Date of birth is required.';          ok = false; }
    if (!password)       { document.getElementById('err-signup-password').textContent = 'Password is required.';               ok = false; }
    else if (password.length < 6)
                         { document.getElementById('err-signup-password').textContent = 'At least 6 characters.';             ok = false; }
    if (!confirm)        { document.getElementById('err-signup-confirm').textContent  = 'Please confirm your password.';       ok = false; }
    else if (password !== confirm)
                         { document.getElementById('err-signup-confirm').textContent  = 'Passwords do not match.';             ok = false; }

    if (!ok) return;

    App.showLoading();
    setTimeout(() => {
      App.hideLoading();
      const newUser = {
        id: App.genId(), name, username, dob, password,
        avatar: null,
        createdAt: new Date().toISOString()
      };
      const users = App.getUsers();
      users.push(newUser);
      App.saveUsers(users);
      localStorage.setItem('hn_current', newUser.id);
      App.currentUser = newUser;
      //App.showToast(`Welcome, ${name}! 🎉`);
      App.navigateTo('dashboard');
    }, 900);
  }
};

document.addEventListener('DOMContentLoaded', () => Auth.init());