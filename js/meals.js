'use strict';

const Meals = {

  catalogue: {
    breakfast: [
      { name:'Idli',        emoji:'🍚', ingredients:['Rice batter','Urad dal','Salt','Water'] },
      { name:'Masala Dosa', emoji:'🥞', ingredients:['Rice batter','Urad dal','Potato','Onion','Mustard seeds','Curry leaves','Oil'] },
      { name:'Plain Dosa',  emoji:'🥞', ingredients:['Rice batter','Urad dal','Salt','Oil'] },
      { name:'Pongal',      emoji:'🍲', ingredients:['Rice','Moong dal','Black pepper','Cumin','Ghee','Cashews','Ginger'] },
      { name:'Upma',        emoji:'🫕', ingredients:['Rava','Onion','Mustard seeds','Urad dal','Curry leaves','Oil','Salt'] },
      { name:'Medu Vada',   emoji:'🍩', ingredients:['Urad dal','Onion','Black pepper','Curry leaves','Green chilli','Salt','Oil'] },
      { name:'Pesarattu',   emoji:'🥞', ingredients:['Green moong dal','Rice','Ginger','Green chilli','Onion','Salt'] },
      { name:'Appam',       emoji:'🫓', ingredients:['Rice','Coconut milk','Yeast','Sugar','Salt'] },
      { name:'Puttu',       emoji:'🎋', ingredients:['Rice flour','Grated coconut','Salt','Water'] },
      { name:'Poori',       emoji:'🫓', ingredients:['Wheat flour','Oil','Salt','Water'] }
    ],
    lunch: [
      { name:'Sambar Rice',      emoji:'🍛', ingredients:['Rice','Toor dal','Tamarind','Tomatoes','Mixed vegetables','Sambar powder','Mustard seeds'] },
      { name:'Curd Rice',        emoji:'🍚', ingredients:['Rice','Curd','Salt','Mustard seeds','Curry leaves','Pomegranate'] },
      { name:'Bisi Bele Bath',   emoji:'🍲', ingredients:['Rice','Toor dal','Vegetables','Tamarind','Jaggery','Spice powder','Ghee'] },
      { name:'Rasam Rice',       emoji:'🍛', ingredients:['Rice','Toor dal','Tamarind','Tomatoes','Rasam powder','Black pepper','Garlic'] },
      { name:'Lemon Rice',       emoji:'🍋', ingredients:['Rice','Lemon','Peanuts','Turmeric','Mustard seeds','Curry leaves'] },
      { name:'Tomato Rice',      emoji:'🍅', ingredients:['Rice','Tomatoes','Onion','Coriander','Spices','Oil'] },
      { name:'Puliyogare',       emoji:'🍛', ingredients:['Rice','Tamarind paste','Peanuts','Sesame seeds','Jaggery','Curry leaves'] },
      { name:'Kootu',            emoji:'🥘', ingredients:['Vegetables','Coconut','Cumin','Urad dal','Red chillies','Curry leaves'] },
      { name:'Avial',            emoji:'🥗', ingredients:['Mixed vegetables','Coconut','Cumin','Curd','Curry leaves','Coconut oil'] },
      { name:'Vegetable Biryani',emoji:'🍛', ingredients:['Basmati rice','Mixed vegetables','Mint','Coriander','Biryani masala','Saffron'] }
    ],
    dinner: [
      { name:'Chapati & Kurma',    emoji:'🫓', ingredients:['Wheat flour','Mixed vegetables','Coconut','Cashews','Spices','Oil'] },
      { name:'Idiyappam',          emoji:'🍝', ingredients:['Rice flour','Salt','Water','Coconut milk'] },
      { name:'Parotta',            emoji:'🫓', ingredients:['Maida','Oil','Salt','Water'] },
      { name:'Kothu Roti',         emoji:'🍽️', ingredients:['Parotta','Egg','Onion','Tomato','Green chilli','Spices'] },
      { name:'Ven Pongal',         emoji:'🍲', ingredients:['Rice','Moong dal','Black pepper','Cumin','Ghee','Ginger','Cashews'] },
      { name:'Palak Dal',          emoji:'🥘', ingredients:['Toor dal','Spinach','Tomatoes','Garlic','Onion','Spices','Oil'] },
      { name:'Paneer Butter Masala',emoji:'🧀',ingredients:['Paneer','Tomatoes','Cream','Butter','Onion','Cashews','Spices'] },
      { name:'Egg Curry',          emoji:'🥚', ingredients:['Eggs','Onion','Tomato','Coconut milk','Curry leaves','Spices'] },
      { name:'Fish Curry',         emoji:'🐟', ingredients:['Fish','Tamarind','Coconut','Tomatoes','Ginger','Garlic','Spices'] },
      { name:'Chicken Chettinad',  emoji:'🍗', ingredients:['Chicken','Kalpasi','Marathi mokku','Coconut','Onion','Tomato','Spices'] }
    ]
  },

  _pendingIngredients: [],
  _pendingImage: null,
  _currentMealType: null,

  render() {
    const container = document.getElementById('meals-content');
    if (!container || !App.currentUser || !App.currentDay) return;

    container.innerHTML = '';

    var types = [
      { key: 'breakfast', label: 'Breakfast', icon: '🌅', time: '7:00 – 9:00 AM' },
      { key: 'lunch',     label: 'Lunch',     icon: '☀️',  time: '12:00 – 2:00 PM' },
      { key: 'dinner',    label: 'Dinner',    icon: '🌙', time: '7:00 – 9:00 PM' }
    ];

    for (var i = 0; i < types.length; i++) {
      container.appendChild(this._buildSection(types[i]));
    }
  },

  _buildSection(type) {
    var allMeals = App.getMeals(App.currentUser.id);
    var dayData  = allMeals[App.currentDay] || {};
    var dishes   = dayData[type.key] || [];

    var section = document.createElement('div');
    section.className = 'meal-section';
    section.setAttribute('data-meal', type.key);

    // Build option list
    var opts = '';
    for (var i = 0; i < this.catalogue[type.key].length; i++) {
      var d = this.catalogue[type.key][i];
      opts += '<option value="' + d.name + '">' + d.emoji + ' ' + d.name + '</option>';
    }

    section.innerHTML =
      '<div class="meal-section-header">' +
        '<div class="meal-section-title-wrap">' +
          '<div class="meal-icon">' + type.icon + '</div>' +
          '<div>' +
            '<div class="meal-title">' + type.label + '</div>' +
            '<div class="meal-time">' + type.time + '</div>' +
          '</div>' +
        '</div>' +
        '<button class="btn-add-meal" title="Add custom dish">+</button>' +
      '</div>' +
      '<div class="predefined-select-wrap">' +
        '<span class="predefined-select-label">Quick add a dish</span>' +
        '<select class="predefined-select">' +
          '<option value="">— Choose a South Indian dish —</option>' +
          opts +
        '</select>' +
      '</div>' +
      '<div class="dish-list" id="dish-list-' + type.key + '"></div>';

    // Render existing dishes
    var listEl = section.querySelector('#dish-list-' + type.key);
    if (dishes.length === 0) {
      listEl.innerHTML = '<p class="meal-empty">No dishes yet — choose from the list above or tap +</p>';
    } else {
      for (var j = 0; j < dishes.length; j++) {
        listEl.appendChild(this._buildDishCard(dishes[j], type.key));
      }
    }

    // Dropdown handler
    var self = this;
    section.querySelector('.predefined-select').addEventListener('change', function(e) {
      var name = e.target.value;
      if (!name) return;
      e.target.value = '';

      var existing = (App.getMeals(App.currentUser.id)[App.currentDay] || {})[type.key] || [];
      for (var k = 0; k < existing.length; k++) {
        if (existing[k].name === name) {
          //App.showToast(name + ' already added', '⚠️');
          return;
        }
      }

      var cat = null;
      for (var k = 0; k < self.catalogue[type.key].length; k++) {
        if (self.catalogue[type.key][k].name === name) {
          cat = self.catalogue[type.key][k];
          break;
        }
      }

      if (cat) {
        var ings = [];
        for (var m = 0; m < cat.ingredients.length; m++) {
          ings.push({ name: cat.ingredients[m], inShopping: false });
        }
        self._addDish(type.key, {
          id: App.genId(),
          name: cat.name,
          emoji: cat.emoji,
          ingredients: ings,
          image: null
        });
      }
    });

    // + button handler
    section.querySelector('.btn-add-meal').addEventListener('click', function() {
      self._openAddModal(type.key);
    });

    return section;
  },

  /* =========================================================
     BUILD DISH CARD
     
     Structure:
     
     <div class="dish-card">          ← display: block
       <div class="dish-card-inner">  ← flex row: img|info|del
         ...
       </div>
       <div class="dish-ingredients-section">  ← block, below inner
         <div class="ingredients-title">...</div>
         <div class="ingredients-chips">  ← flex-wrap
           <span class="ingredient-chip">...</span>
           ...
         </div>
       </div>
     </div>
     
     Because .dish-card is display:block, the two child divs
     (.dish-card-inner and .dish-ingredients-section) stack
     vertically in normal document flow. There is ZERO chance
     of overlap.
  ========================================================= */
  _buildDishCard(dish, mealType) {
    var self = this;

    // ── Card container (display: block) ──
    var card = document.createElement('div');
    card.className = 'dish-card';
    card.id = 'dish-' + dish.id;

    // ══════════════════════════════════════
    // TOP ROW: image + name/preview + delete
    // ══════════════════════════════════════
    var inner = document.createElement('div');
    inner.className = 'dish-card-inner';

    // Image
    var imgWrap = document.createElement('div');
    imgWrap.className = 'dish-img-wrap';
    if (dish.image) {
      var img = document.createElement('img');
      img.src = dish.image;
      img.alt = dish.name || 'Dish';
      imgWrap.appendChild(img);
    } else {
      var emojiSpan = document.createElement('span');
      emojiSpan.className = 'dish-emoji';
      emojiSpan.textContent = dish.emoji || '🍽️';
      imgWrap.appendChild(emojiSpan);
    }

    // Info
    var info = document.createElement('div');
    info.className = 'dish-info';

    var nameDiv = document.createElement('div');
    nameDiv.className = 'dish-name';
    nameDiv.textContent = dish.name || 'Unnamed Dish';

    var previewDiv = document.createElement('div');
    previewDiv.className = 'dish-ingredients-preview';
    if (dish.ingredients.length > 0) {
      var names = [];
      for (var i = 0; i < dish.ingredients.length; i++) {
        names.push(dish.ingredients[i].name);
      }
      previewDiv.textContent = names.join(' · ');
    } else {
      previewDiv.textContent = 'No ingredients listed';
      previewDiv.style.color = 'var(--ink-3)';
      previewDiv.style.fontStyle = 'italic';
    }

    info.appendChild(nameDiv);
    info.appendChild(previewDiv);

    // Delete
    var actions = document.createElement('div');
    actions.className = 'dish-actions';

    var delBtn = document.createElement('button');
    delBtn.className = 'dish-action-btn delete-dish';
    delBtn.title = 'Remove dish';
    delBtn.textContent = '🗑️';
    delBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      self._removeDish(mealType, dish.id);
    });
    actions.appendChild(delBtn);

    // Assemble top row
    inner.appendChild(imgWrap);
    inner.appendChild(info);
    inner.appendChild(actions);

    // Add top row to card
    card.appendChild(inner);

    // ══════════════════════════════════════
    // BOTTOM: Ingredients section
    // Appended to card, NOT to inner.
    // ══════════════════════════════════════
    if (dish.ingredients.length > 0) {
      var section = document.createElement('div');
      section.className = 'dish-ingredients-section';

      var title = document.createElement('div');
      title.className = 'ingredients-title';
      title.textContent = 'Ingredients — tap to move to / from shopping list';
      section.appendChild(title);

      var chipsWrap = document.createElement('div');
      chipsWrap.className = 'ingredients-chips';

      for (var j = 0; j < dish.ingredients.length; j++) {
        (function(ing) {
          var chip = document.createElement('span');
          chip.className = 'ingredient-chip' + (ing.inShopping ? ' unavailable' : '');

          var icon = document.createElement('span');
          icon.className = 'chip-icon';
          icon.textContent = ing.inShopping ? '🛒' : '✅';

          var text = document.createTextNode(' ' + ing.name);

          chip.appendChild(icon);
          chip.appendChild(text);

          chip.title = ing.inShopping
            ? 'In shopping list — tap to return'
            : 'Tap to move to shopping list';

          chip.addEventListener('click', function() {
            self._toggleIngredient(dish.id, mealType, ing.name);
          });

          chipsWrap.appendChild(chip);
        })(dish.ingredients[j]);
      }

      section.appendChild(chipsWrap);
      card.appendChild(section);    // ← appended to CARD, not inner
    }

    return card;
  },

  /* ── Data mutations ── */
  _addDish(mealType, dish) {
    var meals = App.getMeals(App.currentUser.id);
    if (!meals[App.currentDay]) meals[App.currentDay] = {};
    if (!meals[App.currentDay][mealType]) meals[App.currentDay][mealType] = [];
    meals[App.currentDay][mealType].push(dish);
    App.saveMeals(App.currentUser.id, meals);
    this._refreshList(mealType);
    Dashboard.updateStats();
    //App.showToast(dish.name + ' added ✓');
  },

  _removeDish(mealType, dishId) {
    var meals = App.getMeals(App.currentUser.id);
    var list = (meals[App.currentDay] || {})[mealType];
    if (!list) return;

    // Remove shopping items for this dish
    var shop = App.getShoppingList(App.currentUser.id);
    var newShop = [];
    for (var i = 0; i < shop.length; i++) {
      if (shop[i].dishId !== dishId) newShop.push(shop[i]);
    }
    App.saveShoppingList(App.currentUser.id, newShop);

    // Remove dish
    var newList = [];
    for (var i = 0; i < list.length; i++) {
      if (list[i].id !== dishId) newList.push(list[i]);
    }
    meals[App.currentDay][mealType] = newList;
    App.saveMeals(App.currentUser.id, meals);

    this._refreshList(mealType);
    Dashboard.updateStats();
    //App.showToast('Dish removed', '🗑️');
  },

  _toggleIngredient(dishId, mealType, ingName) {
    var meals = App.getMeals(App.currentUser.id);
    var dayMeals = (meals[App.currentDay] || {})[mealType];
    if (!dayMeals) return;

    var dish = null;
    for (var i = 0; i < dayMeals.length; i++) {
      if (dayMeals[i].id === dishId) { dish = dayMeals[i]; break; }
    }
    if (!dish) return;

    var ing = null;
    for (var i = 0; i < dish.ingredients.length; i++) {
      if (dish.ingredients[i].name === ingName) { ing = dish.ingredients[i]; break; }
    }
    if (!ing) return;

    var shop = App.getShoppingList(App.currentUser.id);

    if (!ing.inShopping) {
      ing.inShopping = true;
      shop.push({
        id: App.genId(),
        name: ingName,
        dishId: dishId,
        dishName: dish.name,
        day: App.currentDay,
        mealType: mealType,
        bought: false
      });
      //App.showToast(ingName + ' → Shopping list 🛒', '🛒');
    } else {
      ing.inShopping = false;
      var newShop = [];
      for (var i = 0; i < shop.length; i++) {
        if (!(shop[i].dishId === dishId && shop[i].name === ingName)) {
          newShop.push(shop[i]);
        }
      }
      shop = newShop;
      //App.showToast(ingName + ' returned to pantry ✅');
    }

    App.saveMeals(App.currentUser.id, meals);
    App.saveShoppingList(App.currentUser.id, shop);
    this._refreshList(mealType);
    Dashboard.updateStats();
  },

  _refreshList(mealType) {
    var listEl = document.getElementById('dish-list-' + mealType);
    if (!listEl) return;

    var dishes = ((App.getMeals(App.currentUser.id)[App.currentDay]) || {})[mealType] || [];

    // Clear
    listEl.innerHTML = '';

    if (dishes.length === 0) {
      listEl.innerHTML = '<p class="meal-empty">No dishes yet — choose from the list above or tap +</p>';
      return;
    }

    for (var i = 0; i < dishes.length; i++) {
      listEl.appendChild(this._buildDishCard(dishes[i], mealType));
    }
  },

  /* ── Add Custom Dish Modal ── */
  _openAddModal(mealType) {
    this._currentMealType = mealType;
    this._pendingIngredients = [];
    this._pendingImage = null;

    document.getElementById('new-dish-name').value = '';
    document.getElementById('new-ingredient-input').value = '';
    document.getElementById('ingredient-tags').innerHTML = '';

    var preview = document.getElementById('dish-image-preview');
    if (preview) { preview.classList.add('hidden'); preview.src = ''; }

    var placeholder = document.getElementById('upload-placeholder');
    if (placeholder) placeholder.classList.remove('hidden');

    var fileInput = document.getElementById('dish-image-upload');
    if (fileInput) fileInput.value = '';

    App.openModal('modal-add-dish');
    this._bindAddModal();
  },

  _bindAddModal() {
    var self = this;

    // Clone buttons to remove old listeners
    var ids = ['btn-add-ingredient', 'btn-save-dish'];
    for (var i = 0; i < ids.length; i++) {
      var old = document.getElementById(ids[i]);
      if (old) {
        var clone = old.cloneNode(true);
        old.parentNode.replaceChild(clone, old);
      }
    }

    // Clone image area
    var oldArea = document.getElementById('dish-image-area');
    if (oldArea) {
      var areaClone = oldArea.cloneNode(true);
      oldArea.parentNode.replaceChild(areaClone, oldArea);
    }

    // Add ingredient
    function doAdd() {
      var inp = document.getElementById('new-ingredient-input');
      var val = inp.value.trim();
      if (!val) return;

      // Check duplicate
      for (var i = 0; i < self._pendingIngredients.length; i++) {
        if (self._pendingIngredients[i].toLowerCase() === val.toLowerCase()) {
          //App.showToast('Already added', '⚠️');
          return;
        }
      }

      self._pendingIngredients.push(val);
      self._renderPendingTags();
      inp.value = '';
      inp.focus();
    }

    document.getElementById('btn-add-ingredient').addEventListener('click', doAdd);
    document.getElementById('new-ingredient-input').addEventListener('keydown', function(e) {
      if (e.key === 'Enter') { e.preventDefault(); doAdd(); }
    });

    // Image upload
    document.getElementById('dish-image-area').addEventListener('click', function() {
      document.getElementById('dish-image-upload').click();
    });

    document.getElementById('dish-image-upload').addEventListener('change', function(e) {
      var file = e.target.files[0];
      if (!file) return;
      var reader = new FileReader();
      reader.onload = function(ev) {
        self._pendingImage = ev.target.result;
        var prev = document.getElementById('dish-image-preview');
        prev.src = self._pendingImage;
        prev.classList.remove('hidden');
        document.getElementById('upload-placeholder').classList.add('hidden');
      };
      reader.readAsDataURL(file);
    });

    // Save dish
    document.getElementById('btn-save-dish').addEventListener('click', function() {
      var name = document.getElementById('new-dish-name').value.trim() || 'Custom Dish';
      var ings = [];
      for (var i = 0; i < self._pendingIngredients.length; i++) {
        ings.push({ name: self._pendingIngredients[i], inShopping: false });
      }
      self._addDish(self._currentMealType, {
        id: App.genId(),
        name: name,
        emoji: '🍽️',
        ingredients: ings,
        image: self._pendingImage
      });
      App.closeModal('modal-add-dish');
    });
  },

  _renderPendingTags() {
    var self = this;
    var wrap = document.getElementById('ingredient-tags');
    wrap.innerHTML = '';

    for (var i = 0; i < this._pendingIngredients.length; i++) {
      (function(idx) {
        var tag = document.createElement('span');
        tag.className = 'ingredient-tag';

        var text = document.createTextNode(self._pendingIngredients[idx] + ' ');
        tag.appendChild(text);

        var x = document.createElement('span');
        x.className = 'tag-remove';
        x.textContent = '✕';
        x.addEventListener('click', function() {
          self._pendingIngredients.splice(idx, 1);
          self._renderPendingTags();
        });
        tag.appendChild(x);

        wrap.appendChild(tag);
      })(i);
    }
  }
};