'use strict';

const Dashboard = {

  DAYS: ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],

  render() {
    this._renderHeader();
    this._renderWeekGrid();    // ← this was the missing call
    this._renderStats();
  },

  _renderHeader() {
    if (!App.currentUser) return;
    const h = new Date().getHours();
    const greeting = h < 12 ? 'Good Morning! ☀️' : h < 17 ? 'Good Afternoon! 🌤️' : 'Good Evening! 🌙';
    document.getElementById('dash-greeting').textContent  = greeting;
    document.getElementById('dash-username').textContent  = App.currentUser.name;
    const av = document.getElementById('dash-avatar');
    if (av) {
      av.innerHTML = App.currentUser.avatar
        ? `<img src="${App.currentUser.avatar}" alt="avatar" />`
        : App.currentUser.name.charAt(0).toUpperCase();
    }
  },

  _renderWeekGrid() {
    const grid = document.getElementById('week-grid');
    if (!grid || !App.currentUser) return;
    grid.innerHTML = '';                          // clear before re-render

    const today       = new Date();
    const todayStr    = this._dateStr(today);
    const dow         = today.getDay();           // 0=Sun…6=Sat
    const mondayDelta = (dow === 0) ? -6 : 1 - dow;
    const monday      = new Date(today);
    monday.setDate(today.getDate() + mondayDelta);

    const meals = App.getMeals(App.currentUser.id);

    this.DAYS.forEach((dayName, i) => {
      const date    = new Date(monday);
      date.setDate(monday.getDate() + i);
      const dStr    = this._dateStr(date);
      const isToday = dStr === todayStr;
      const dayKey  = dayName.toLowerCase();
      const dm      = meals[dayKey] || {};
      const bf      = (dm.breakfast || []).length;
      const lu      = (dm.lunch     || []).length;
      const di      = (dm.dinner    || []).length;
      const total   = bf + lu + di;
      const isLast  = (i === 6);

      const card = document.createElement('div');
      card.className = [
        'day-card',
        isToday ? 'today'      : '',
        isLast  ? 'full-width' : ''
      ].filter(Boolean).join(' ');

      const dateLabel = date.toLocaleDateString('en-IN', { day:'numeric', month:'short' });

      // Dot rows
      let dotsHTML = '';
      if (bf > 0) dotsHTML += `<span class="meal-dot breakfast" title="Breakfast"></span>`.repeat(Math.min(bf,3));
      if (lu > 0) dotsHTML += `<span class="meal-dot lunch"     title="Lunch"></span>`.repeat(Math.min(lu,3));
      if (di > 0) dotsHTML += `<span class="meal-dot dinner"    title="Dinner"></span>`.repeat(Math.min(di,3));

      card.innerHTML = `
        <div class="day-card-top">
          <div>
            <div class="day-name">${dayName}</div>
            <div class="day-date">${dateLabel}</div>
          </div>
          ${isToday ? '<span class="day-badge">Today</span>' : ''}
        </div>
        <div class="day-card-bottom">
          ${total > 0
            ? `<div class="meal-preview">${dotsHTML}</div>
               <p class="meal-count-text">${total} meal${total !== 1 ? 's' : ''} planned</p>`
            : `<p class="day-empty-text">No meals planned</p>`
          }
        </div>
      `;

      card.addEventListener('click', () => {
        App.currentDay = dayKey;
        document.getElementById('meals-day-title').textContent = dayName;
        App.navigateTo('meals');
      });

      grid.appendChild(card);
    });
  },

  _renderStats() {
    if (!App.currentUser) return;
    const meals    = App.getMeals(App.currentUser.id);
    const shopping = App.getShoppingList(App.currentUser.id);

    let totalMeals = 0, daysPlanned = 0;
    this.DAYS.forEach(d => {
      const dm = meals[d.toLowerCase()] || {};
      const n  = (dm.breakfast||[]).length + (dm.lunch||[]).length + (dm.dinner||[]).length;
      totalMeals  += n;
      if (n > 0) daysPlanned++;
    });

    this._count('stat-total-meals', totalMeals);
    this._count('stat-shopping',    shopping.filter(i => !i.bought).length);
    this._count('stat-complete',    daysPlanned);
  },

  _count(id, target) {
    const el = document.getElementById(id);
    if (!el) return;
    const start = parseInt(el.textContent) || 0;
    const t0    = performance.now();
    const dur   = 500;
    const step  = ts => {
      const p = Math.min((ts - t0) / dur, 1);
      el.textContent = Math.round(start + (target - start) * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  },

  _dateStr(d) {
    return d.toISOString().split('T')[0];
  },

  /* Called from Meals/Shopping after data changes */
  updateStats() { this._renderStats(); }
};