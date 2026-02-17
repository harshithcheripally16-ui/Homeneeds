// static/js/app.js

// ============================================
// THEME MANAGEMENT
// ============================================
(function initThemeImmediately() {
    const savedTheme = localStorage.getItem('homeNeedsTheme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
})();

function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('homeNeedsTheme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const allToggles = document.querySelectorAll('.theme-toggle, #themeToggle');
    allToggles.forEach(function(btn) {
        const icon = btn.querySelector('i');
        if (icon) {
            if (theme === 'dark') {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            } else {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            }
        }
    });
}

function loadTheme() {
    const savedTheme = localStorage.getItem('homeNeedsTheme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

document.addEventListener('DOMContentLoaded', loadTheme);

// ============================================
// GLOBAL VARIABLES
// ============================================
let currentItems = [];
let undoTimeout = null;
let touchStartX = 0;
let touchCurrentX = 0;
let swipingElement = null;
const SWIPE_THRESHOLD = 80;

// ============================================
// API HELPER
// ============================================
async function apiCall(url, method, body) {
    method = method || 'GET';
    body = body || null;

    const options = {
        method: method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(url, options);
        if (response.status === 401) {
            window.location.href = '/login';
            return null;
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return null;
    }
}

// ============================================
// ADD NEW ITEM (works on any page)
// ============================================
async function addNewItem(category) {
    const input = document.getElementById('addItemInput');
    if (!input) return;

    const name = input.value.trim();

    if (!name) {
        input.classList.add('shake');
        setTimeout(function() { input.classList.remove('shake'); }, 500);
        return;
    }

    const result = await apiCall('/api/items', 'POST', { name: name, category: category });

    if (result && result.success) {
        input.value = '';
        const currentPage = getCurrentPage();
        if (currentPage === 'procure') {
            loadProcureItems(category);
        } else if (currentPage === 'list') {
            loadFullList(category);
        }
        showMiniToast('"' + name + '" added!');
    } else if (result) {
        showMiniToast(result.message || 'Failed to add item', true);
    }
}

// Handle Enter key on add input
document.addEventListener('DOMContentLoaded', function () {
    const addInput = document.getElementById('addItemInput');
    if (addInput) {
        addInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                var btn = document.querySelector('.add-item-btn');
                if (btn) btn.click();
            }
        });
    }
});

// ============================================
// DETERMINE CURRENT PAGE
// ============================================
function getCurrentPage() {
    var path = window.location.pathname;
    if (path.indexOf('-procure') !== -1) return 'procure';
    if (path.indexOf('-list') !== -1) return 'list';
    return 'dashboard';
}

// ============================================
// LOAD PROCURE ITEMS (Pages 2 & 3)
// ============================================
async function loadProcureItems(category) {
    var itemsList = document.getElementById('itemsList');
    var emptyState = document.getElementById('emptyState');

    if (!itemsList) return;

    itemsList.innerHTML = '';
    for (var i = 0; i < 4; i++) {
        itemsList.innerHTML += '<div class="loading-shimmer"></div>';
    }

    var items = await apiCall('/api/items/' + category);
    if (!items) return;

    currentItems = items;

    var procureItems = items.filter(function(item) { return item.to_procure; });
    var activeItems = procureItems.filter(function(item) { return !item.consumed; });
    var consumedItems = procureItems.filter(function(item) { return item.consumed; });

    itemsList.innerHTML = '';

    if (procureItems.length === 0) {
        itemsList.style.display = 'none';
        emptyState.style.display = 'flex';
        return;
    }

    itemsList.style.display = 'flex';
    emptyState.style.display = 'none';

    if (activeItems.length > 0) {
        itemsList.innerHTML += '<div class="section-header"><h3>Active Items</h3><span class="section-count">' + activeItems.length + ' items</span></div>';
        activeItems.forEach(function(item, index) {
            itemsList.innerHTML += createProcureItemCard(item, false, index);
        });
    }

    if (consumedItems.length > 0) {
        itemsList.innerHTML += '<div class="section-header"><h3>Consumed</h3><span class="section-count">' + consumedItems.length + ' items</span></div>';
        consumedItems.forEach(function(item, index) {
            itemsList.innerHTML += createProcureItemCard(item, true, activeItems.length + index);
        });
    }
}

function createProcureItemCard(item, isConsumed, index) {
    var delay = Math.min(index * 0.05, 0.3);
    var consumedClass = isConsumed ? 'consumed' : '';
    var iconClass = isConsumed ? 'fa-undo' : 'fa-check';
    var actionText = isConsumed ? 'Tap to restore' : 'Tap to consume';

    return '<div class="item-card ' + consumedClass + ' animate-card" ' +
        'data-id="' + item.id + '" ' +
        'data-consumed="' + isConsumed + '" ' +
        'style="animation-delay: ' + delay + 's" ' +
        'onclick="toggleConsumed(' + item.id + ', \'' + item.category + '\')">' +
        '<div class="item-status-dot"></div>' +
        '<span class="item-name">' + escapeHtml(item.name) + '</span>' +
        '<div class="item-action">' +
        '<span class="item-action-text">' + actionText + '</span>' +
        '<i class="fas ' + iconClass + '"></i>' +
        '</div></div>';
}

// ============================================
// TOGGLE CONSUMED (Procure pages)
// ============================================
async function toggleConsumed(itemId, category) {
    var card = document.querySelector('.item-card[data-id="' + itemId + '"]');
    if (card) {
        card.classList.add('slide-out');
    }

    await new Promise(function(resolve) { setTimeout(resolve, 300); });

    var result = await apiCall('/api/items/' + itemId + '/toggle-consumed', 'PUT');
    if (result && result.success) {
        loadProcureItems(category);
    }
}

// ============================================
// LOAD FULL LIST (Pages 4 & 5)
// ============================================
async function loadFullList(category) {
    var itemsList = document.getElementById('itemsList');
    var emptyState = document.getElementById('emptyState');

    if (!itemsList) return;

    itemsList.innerHTML = '';
    for (var i = 0; i < 6; i++) {
        itemsList.innerHTML += '<div class="loading-shimmer"></div>';
    }

    var items = await apiCall('/api/items/' + category);
    if (!items) return;

    currentItems = items;
    renderFullList(items);
}

function renderFullList(items) {
    var itemsList = document.getElementById('itemsList');
    var emptyState = document.getElementById('emptyState');

    itemsList.innerHTML = '';

    if (items.length === 0) {
        itemsList.style.display = 'none';
        emptyState.style.display = 'flex';
        return;
    }

    itemsList.style.display = 'flex';
    emptyState.style.display = 'none';

    items.forEach(function(item, index) {
        var delay = Math.min(index * 0.03, 0.5);
        var itemEl = document.createElement('div');
        var checkedClass = item.to_procure ? 'checked' : '';
        var checkedAttr = item.to_procure ? 'checked' : '';

        itemEl.className = 'item-checkbox-wrapper ' + checkedClass + ' animate-card';
        itemEl.style.animationDelay = delay + 's';
        itemEl.setAttribute('data-id', item.id);
        itemEl.setAttribute('data-name', item.name.toLowerCase());

        itemEl.innerHTML = '<div class="swipe-delete-bg"><i class="fas fa-trash-alt"></i></div>' +
            '<label class="custom-checkbox">' +
            '<input type="checkbox" ' + checkedAttr + ' onchange="toggleProcure(' + item.id + ', \'' + item.category + '\', this)">' +
            '<span class="checkmark"></span>' +
            '</label>' +
            '<span class="checkbox-item-name">' + escapeHtml(item.name) + '</span>';

        setupSwipeToDelete(itemEl, item);
        itemsList.appendChild(itemEl);
    });
}

// ============================================
// TOGGLE PROCURE (List pages - checkbox)
// ============================================
async function toggleProcure(itemId, category, checkbox) {
    var wrapper = checkbox.closest('.item-checkbox-wrapper');

    var result = await apiCall('/api/items/' + itemId + '/toggle-procure', 'PUT');
    if (result && result.success) {
        if (result.item.to_procure) {
            wrapper.classList.add('checked');
            showMiniToast('"' + result.item.name + '" added to procure list');
        } else {
            wrapper.classList.remove('checked');
            showMiniToast('"' + result.item.name + '" removed from procure list');
        }
    } else {
        checkbox.checked = !checkbox.checked;
    }
}

// ============================================
// SWIPE TO DELETE
// ============================================
function setupSwipeToDelete(element, item) {
    var startX = 0;
    var currentX = 0;
    var isDragging = false;

    element.addEventListener('touchstart', function (e) {
        if (e.target.type === 'checkbox' || e.target.closest('.custom-checkbox')) return;
        startX = e.touches[0].clientX;
        currentX = startX;
        isDragging = true;
        element.style.transition = 'none';
    }, { passive: true });

    element.addEventListener('touchmove', function (e) {
        if (!isDragging) return;
        currentX = e.touches[0].clientX;
        var diff = startX - currentX;

        if (diff > 0) {
            var translateX = Math.min(diff, 120);
            element.style.transform = 'translateX(-' + translateX + 'px)';
            element.classList.add('swiping');

            var deleteBg = element.querySelector('.swipe-delete-bg');
            if (deleteBg) {
                deleteBg.style.opacity = Math.min(diff / SWIPE_THRESHOLD, 1);
            }
        }
    }, { passive: true });

    element.addEventListener('touchend', function () {
        if (!isDragging) return;
        isDragging = false;

        var diff = startX - currentX;
        element.style.transition = 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)';

        if (diff > SWIPE_THRESHOLD) {
            element.style.transform = 'translateX(-100%)';
            element.style.opacity = '0';
            setTimeout(function() {
                deleteItem(item.id, item.name, element);
            }, 300);
        } else {
            element.style.transform = 'translateX(0)';
            element.classList.remove('swiping');
        }
    });

    // Mouse support for desktop
    element.addEventListener('mousedown', function (e) {
        if (e.target.type === 'checkbox' || e.target.closest('.custom-checkbox')) return;

        startX = e.clientX;
        currentX = startX;
        isDragging = true;
        element.style.transition = 'none';

        var moveHandler = function (e) {
            if (!isDragging) return;
            currentX = e.clientX;
            var diff = startX - currentX;

            if (diff > 0) {
                var translateX = Math.min(diff, 120);
                element.style.transform = 'translateX(-' + translateX + 'px)';
                element.classList.add('swiping');
            }
        };

        var upHandler = function () {
            if (!isDragging) return;
            isDragging = false;

            var diff = startX - currentX;
            element.style.transition = 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)';

            if (diff > SWIPE_THRESHOLD) {
                element.style.transform = 'translateX(-100%)';
                element.style.opacity = '0';
                setTimeout(function() {
                    deleteItem(item.id, item.name, element);
                }, 300);
            } else {
                element.style.transform = 'translateX(0)';
                element.classList.remove('swiping');
            }

            document.removeEventListener('mousemove', moveHandler);
            document.removeEventListener('mouseup', upHandler);
        };

        document.addEventListener('mousemove', moveHandler);
        document.addEventListener('mouseup', upHandler);
    });
}

// ============================================
// DELETE ITEM WITH UNDO
// ============================================
async function deleteItem(itemId, itemName, element) {
    var result = await apiCall('/api/items/' + itemId, 'DELETE');

    if (result && result.success) {
        if (element) {
            element.remove();
        }

        currentItems = currentItems.filter(function(i) { return i.id !== itemId; });

        var itemsList = document.getElementById('itemsList');
        var emptyState = document.getElementById('emptyState');
        if (itemsList && itemsList.children.length === 0) {
            itemsList.style.display = 'none';
            if (emptyState) emptyState.style.display = 'flex';
        }

        showUndoToast(result.deleted_id, itemName);
    }
}

function showUndoToast(deletedId, itemName) {
    var toast = document.getElementById('undoToast');
    var message = document.getElementById('undoMessage');
    var undoBtn = document.getElementById('undoBtn');

    if (!toast) return;

    if (undoTimeout) {
        clearTimeout(undoTimeout);
    }

    message.textContent = '"' + itemName + '" deleted';
    toast.style.display = 'flex';
    toast.style.animation = 'none';
    void toast.offsetHeight;
    toast.style.animation = 'toastIn 0.4s cubic-bezier(0.16, 1, 0.3, 1)';

    var newUndoBtn = undoBtn.cloneNode(true);
    undoBtn.parentNode.replaceChild(newUndoBtn, undoBtn);

    newUndoBtn.addEventListener('click', async function () {
        var result = await apiCall('/api/items/undo/' + deletedId, 'POST');
        if (result && result.success) {
            toast.style.display = 'none';
            if (undoTimeout) clearTimeout(undoTimeout);

            var path = window.location.pathname;
            if (path.indexOf('vegfruit') !== -1) {
                loadFullList('vegfruit');
            } else if (path.indexOf('groceries') !== -1 || path.indexOf('grocery') !== -1) {
                loadFullList('grocery');
            }

            showMiniToast('"' + itemName + '" restored!');
        }
    });

    undoTimeout = setTimeout(function() {
        toast.style.display = 'none';
    }, 5000);
}

// ============================================
// SEARCH / FILTER
// ============================================
function filterItems() {
    var searchInput = document.getElementById('searchInput');
    if (!searchInput) return;

    var query = searchInput.value.toLowerCase().trim();
    var items = document.querySelectorAll('.item-checkbox-wrapper');

    items.forEach(function(item) {
        var name = item.getAttribute('data-name') || '';
        if (name.indexOf(query) !== -1) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

// ============================================
// MINI TOAST
// ============================================
function showMiniToast(message, isError) {
    isError = isError || false;

    var existing = document.querySelector('.mini-toast');
    if (existing) existing.remove();

    var toast = document.createElement('div');
    toast.className = 'mini-toast';
    var bgColor = isError ? 'linear-gradient(135deg, #ff4757, #ff2d2d)' : 'linear-gradient(135deg, #2ED573, #17B978)';

    toast.style.cssText = 'position:fixed;top:20px;left:50%;transform:translateX(-50%) translateY(-100px);' +
        'background:' + bgColor + ';color:white;padding:12px 24px;border-radius:14px;font-size:14px;' +
        'font-weight:600;font-family:Poppins,sans-serif;z-index:9999;box-shadow:0 8px 30px rgba(0,0,0,0.2);' +
        'transition:transform 0.4s cubic-bezier(0.16,1,0.3,1);max-width:calc(100% - 40px);text-align:center;pointer-events:none;';

    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(function() {
        toast.style.transform = 'translateX(-50%) translateY(0)';
    });

    setTimeout(function() {
        toast.style.transform = 'translateX(-50%) translateY(-100px)';
        setTimeout(function() { toast.remove(); }, 400);
    }, 2500);
}

// ============================================
// DASHBOARD STATS
// ============================================
async function refreshDashboardStats() {
    var result = await apiCall('/api/dashboard-stats');
    if (result) {
        var el = function(id) { return document.getElementById(id); };
        if (el('statVegProcure')) animateNumber(el('statVegProcure'), result.veg_procure);
        if (el('statGroceryProcure')) animateNumber(el('statGroceryProcure'), result.grocery_procure);
        if (el('statTotalVeg')) animateNumber(el('statTotalVeg'), result.total_veg);
        if (el('statTotalGrocery')) animateNumber(el('statTotalGrocery'), result.total_grocery);
    }
}

function animateNumber(element, target) {
    var current = parseInt(element.textContent) || 0;
    if (current === target) return;

    var diff = target - current;
    var steps = Math.min(Math.abs(diff), 20);
    var increment = diff / steps;
    var step = 0;

    var timer = setInterval(function() {
        step++;
        var value = Math.round(current + increment * step);
        element.textContent = value;
        if (step >= steps) {
            element.textContent = target;
            clearInterval(timer);
        }
    }, 30);
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Ripple effect
document.addEventListener('click', function (e) {
    var target = e.target.closest('.nav-card, .auth-btn, .add-item-btn');
    if (target) {
        var ripple = document.createElement('span');
        ripple.className = 'ripple-effect';
        var rect = target.getBoundingClientRect();
        var size = Math.max(rect.width, rect.height);
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
        ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
        target.appendChild(ripple);
        setTimeout(function() { ripple.remove(); }, 600);
    }
});

// Smooth page load
document.addEventListener('DOMContentLoaded', function () {
    document.body.style.opacity = '0';
    requestAnimationFrame(function() {
        document.body.style.transition = 'opacity 0.3s ease';
        document.body.style.opacity = '1';
    });
});