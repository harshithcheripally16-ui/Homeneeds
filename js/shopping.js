'use strict';

const Shopping = {
  currentFilter: 'all',

  render() {
    this.renderList();
    this.updateSummary();
    this.initFilters();
  },

  initFilters() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.onclick = () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.currentFilter = btn.dataset.filter;
        this.renderList();
      };
    });
  },

  renderList() {
    const container = document.getElementById('shopping-list');
    const emptyState = document.getElementById('shopping-empty');
    if (!container || !App.currentUser) return;

    container.innerHTML = '';

    let items = App.getShoppingList(App.currentUser.id);

    if (this.currentFilter === 'pending') items = items.filter(i => !i.bought);
    if (this.currentFilter === 'bought') items = items.filter(i => i.bought);

    if (items.length === 0) {
      emptyState?.classList.remove('hidden');
      return;
    }
    emptyState?.classList.add('hidden');

    // Group by dish
    const groups = {};
    items.forEach(item => {
      const key = `${item.dishName}_${item.day}_${item.mealType}`;
      if (!groups[key]) {
        groups[key] = {
          dishName: item.dishName,
          day: item.day,
          mealType: item.mealType,
          items: []
        };
      }
      groups[key].items.push(item);
    });

    Object.values(groups).forEach(group => {
      const groupEl = document.createElement('div');
      groupEl.className = 'shopping-group';

      const dayLabel = group.day.charAt(0).toUpperCase() + group.day.slice(1);
      const mealLabel = group.mealType.charAt(0).toUpperCase() + group.mealType.slice(1);

      groupEl.innerHTML = `
        <div class="shopping-group-header">
          <div>
            <div class="shopping-group-dish">🍽️ ${group.dishName}</div>
            <div class="shopping-group-meta">${dayLabel} · ${mealLabel}</div>
          </div>
        </div>
      `;

      group.items.forEach(item => {
        const itemEl = this.createShoppingItem(item);
        groupEl.appendChild(itemEl);
      });

      container.appendChild(groupEl);
    });

    this.updateSummary();
  },

  createShoppingItem(item) {
    const itemEl = document.createElement('div');
    itemEl.className = `shopping-item${item.bought ? ' bought' : ''}`;
    itemEl.id = `shop-item-${item.id}`;

    itemEl.innerHTML = `
      <div class="shopping-checkbox">${item.bought ? '✓' : ''}</div>
      <span class="shopping-item-name">${item.name}</span>
      <button class="shopping-item-return" title="Return to pantry" data-item-id="${item.id}">↩️</button>
    `;

    // Toggle bought
    itemEl.querySelector('.shopping-checkbox').addEventListener('click', (e) => {
      e.stopPropagation();
      this.toggleBought(item.id);
    });

    itemEl.querySelector('.shopping-item-name').addEventListener('click', () => {
      this.toggleBought(item.id);
    });

    // Return to pantry
    itemEl.querySelector('.shopping-item-return').addEventListener('click', (e) => {
      e.stopPropagation();
      this.returnToPantry(item);
    });

    return itemEl;
  },

  toggleBought(itemId) {
    const list = App.getShoppingList(App.currentUser.id);
    const item = list.find(i => i.id === itemId);
    if (!item) return;
    item.bought = !item.bought;
    App.saveShoppingList(App.currentUser.id, list);
    this.renderList();
    App.showToast(item.bought ? 'Marked as bought ✓' : 'Marked as pending');
  },

  returnToPantry(shoppingItem) {
    // Remove from shopping list
    let list = App.getShoppingList(App.currentUser.id);
    list = list.filter(i => i.id !== shoppingItem.id);
    App.saveShoppingList(App.currentUser.id, list);

    // Update meal ingredient
    const meals = App.getMeals(App.currentUser.id);
    const dayMeals = meals[shoppingItem.day];
    if (dayMeals && dayMeals[shoppingItem.mealType]) {
      const dish = dayMeals[shoppingItem.mealType].find(d => d.id === shoppingItem.dishId);
      if (dish) {
        const ing = dish.ingredients.find(i => i.name === shoppingItem.name);
        if (ing) ing.inShopping = false;
        App.saveMeals(App.currentUser.id, meals);
      }
    }

    this.renderList();
    App.showToast(`${shoppingItem.name} returned to pantry ✅`);

    // Refresh meals if visible
    if (App.currentPage === 'meals' && typeof Meals !== 'undefined') {
      Meals.render();
    }
  },

  updateSummary() {
    if (!App.currentUser) return;
    const list = App.getShoppingList(App.currentUser.id);
    const total = list.length;
    const bought = list.filter(i => i.bought).length;
    const remaining = total - bought;

    const shopTotal = document.getElementById('shop-total');
    const shopBought = document.getElementById('shop-bought');
    const shopRemaining = document.getElementById('shop-remaining');

    if (shopTotal) shopTotal.textContent = total;
    if (shopBought) shopBought.textContent = bought;
    if (shopRemaining) shopRemaining.textContent = remaining;

    // Update dashboard stat
    const statShopping = document.getElementById('stat-shopping');
    if (statShopping) statShopping.textContent = remaining;
  }
};

document.addEventListener('DOMContentLoaded', () => {
  // Initialized via App.navigateTo
});