/**
 * Panel System — ПравоАгент
 * VS Code / Cursor-like panel layout with drag, resize, tabs, and keyboard shortcuts
 * Vanilla JS (no dependencies)
 */

class PanelSystem {
    constructor(rootEl, options = {}) {
        this.root = typeof rootEl === 'string' ? document.querySelector(rootEl) : rootEl;
        if (!this.root) throw new Error('PanelSystem: root element not found');

        this.options = {
            storageKey: 'pravoagent-panel-layout',
            defaultLayout: null,
            minPanelWidth: 120,
            minSidebarWidth: 180,
            role: 'default',
            ...options
        };

        this.state = {
            layout: this.loadLayout() || this.options.defaultLayout || this.getDefaultLayout(),
            activeActivity: null,
            panels: {},
            tabs: {},
            resizeActive: false,
            dragActive: false,
            collapsedPanels: new Set()
        };

        this.init();
    }

    // ————— Default Layout —————

    getDefaultLayout() {
        return {
            sidebarWidth: 280,
            rightWidth: 320,
            activityBar: 'explorer',
            sidebarCollapsed: false,
            rightCollapsed: false,
            panels: {
                explorer: { collapsed: false },
                search: { collapsed: true }
            }
        };
    }

    // ————— Storage —————

    saveLayout() {
        try {
            localStorage.setItem(this.options.storageKey, JSON.stringify(this.state.layout));
        } catch (e) {
            // localStorage unavailable
        }
    }

    loadLayout() {
        try {
            const data = localStorage.getItem(this.options.storageKey);
            return data ? JSON.parse(data) : null;
        } catch (e) {
            return null;
        }
    }

    // ————— Initialization —————

    init() {
        this.render();
        this.bindResizeHandles();
        this.bindDragHandles();
        this.bindActivityBar();
        this.bindTabs();
        this.bindCollapseButtons();
        this.bindKeyboardShortcuts();
        this.restoreLayout();
        this.applyLayout();
    }

    render() {
        // Ensure the layout container has the panel-layout class
        this.root.classList.add('panel-layout');

        // Set CSS variables from layout
        this.root.style.setProperty('--panel-sidebar-width', this.state.layout.sidebarWidth + 'px');
        this.root.style.setProperty('--panel-right-width', this.state.layout.rightWidth + 'px');

        // Mark collapsed panels
        this.state.collapsedPanels.forEach(id => {
            const panel = this.root.querySelector(`.panel[data-panel-id="${id}"]`);
            if (panel) panel.classList.add('panel-collapsed');
        });

        // Mark active activity bar item
        if (this.state.layout.activityBar) {
            const btn = this.root.querySelector(`.activity-bar-item[data-panel="${this.state.layout.activityBar}"]`);
            if (btn) btn.classList.add('active');
        }

        // Restore sidebar collapsed state
        if (this.state.layout.sidebarCollapsed) {
            this.root.classList.add('sidebar-collapsed');
        }

        if (this.state.layout.rightCollapsed) {
            this.root.classList.add('right-collapsed');
        }
    }

    // ————— Resize —————

    bindResizeHandles() {
        const handles = this.root.querySelectorAll('.panel-resize-handle');
        handles.forEach(handle => {
            handle.addEventListener('mousedown', (e) => this.startResize(e, handle));
            // Touch support
            handle.addEventListener('touchstart', (e) => this.startResize(e, handle), { passive: false });
        });
    }

    startResize(e, handle) {
        e.preventDefault();
        this.state.resizeActive = true;
        handle.classList.add('active');

        const panel = handle.closest('.panel');
        const isHorizontal = handle.classList.contains('horizontal');
        const layout = this.root;
        const startX = e.clientX || e.touches?.[0]?.clientX || 0;
        const startY = e.clientY || e.touches?.[0]?.clientY || 0;
        const startWidth = panel ? panel.offsetWidth : layout.offsetWidth;

        const onMove = (ev) => {
            if (!this.state.resizeActive) return;
            ev.preventDefault();

            const currentX = ev.clientX || ev.touches?.[0]?.clientX || 0;
            const currentY = ev.clientY || ev.touches?.[0]?.clientY || 0;

            if (isHorizontal) {
                const delta = currentY - startY;
                // We'd need more complex logic for horizontal splits
            } else if (panel) {
                const delta = currentX - startX;
                const newWidth = Math.max(this.options.minPanelWidth, startWidth + delta);

                if (handle.dataset.resizeTarget === 'sidebar') {
                    this.state.layout.sidebarWidth = newWidth;
                    this.root.style.setProperty('--panel-sidebar-width', newWidth + 'px');
                } else if (handle.dataset.resizeTarget === 'right') {
                    this.state.layout.rightWidth = newWidth;
                    this.root.style.setProperty('--panel-right-width', newWidth + 'px');
                } else {
                    panel.style.width = newWidth + 'px';
                    panel.style.flex = 'none';
                }
            }
        };

        const onUp = () => {
            this.state.resizeActive = false;
            handle.classList.remove('active');
            document.removeEventListener('mousemove', onMove);
            document.removeEventListener('mouseup', onUp);
            document.removeEventListener('touchmove', onMove);
            document.removeEventListener('touchend', onUp);
            this.saveLayout();
        };

        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
        document.addEventListener('touchmove', onMove, { passive: false });
        document.addEventListener('touchend', onUp);
    }

    // ————— Drag (reorder panels) —————

    bindDragHandles() {
        const headers = this.root.querySelectorAll('.panel-header');
        headers.forEach(header => {
            header.addEventListener('mousedown', (e) => this.startDrag(e, header));
        });
    }

    startDrag(e, header) {
        // Only drag if clicking the title area, not buttons
        if (e.target.closest('.panel-header-btn') || e.target.closest('.panel-tab')) return;

        e.preventDefault();
        this.state.dragActive = true;
        const panel = header.closest('.panel');
        if (!panel) return;

        panel.style.opacity = '0.8';
        panel.style.zIndex = '100';

        const startX = e.clientX;
        const startY = e.clientY;
        const startRect = panel.getBoundingClientRect();
        const ghost = panel.cloneNode(true);
        ghost.style.position = 'fixed';
        ghost.style.zIndex = '999';
        ghost.style.pointerEvents = 'none';
        ghost.style.opacity = '0.5';
        ghost.style.width = startRect.width + 'px';
        ghost.style.height = startRect.height + 'px';
        ghost.style.left = startRect.left + 'px';
        ghost.style.top = startRect.top + 'px';
        ghost.style.transform = 'rotate(2deg)';
        document.body.appendChild(ghost);

        const onMove = (ev) => {
            if (!this.state.dragActive) return;
            const dx = ev.clientX - startX;
            const dy = ev.clientY - startY;
            ghost.style.left = (startRect.left + dx) + 'px';
            ghost.style.top = (startRect.top + dy) + 'px';
        };

        const onUp = () => {
            this.state.dragActive = false;
            panel.style.opacity = '';
            panel.style.zIndex = '';
            ghost.remove();

            // In a real implementation, detect drop zone and reorder
            document.removeEventListener('mousemove', onMove);
            document.removeEventListener('mouseup', onUp);
        };

        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
    }

    // ————— Activity Bar —————

    bindActivityBar() {
        const items = this.root.querySelectorAll('.activity-bar-item');
        items.forEach(item => {
            item.addEventListener('click', () => this.toggleActivityPanel(item.dataset.panel));
        });
    }

    toggleActivityPanel(panelId) {
        if (!panelId) return;

        const panel = this.root.querySelector(`.panel[data-panel-id="${panelId}"]`);
        if (!panel) return;

        const isCurrentlyActive = this.state.layout.activityBar === panelId;

        // Deactivate all activity bar items
        this.root.querySelectorAll('.activity-bar-item').forEach(el => el.classList.remove('active'));

        if (isCurrentlyActive) {
            // Toggle off: collapse the panel
            this.state.layout.activityBar = null;
            this.collapsePanel(panelId);
        } else {
            // Collapse the previously active panel first
            if (this.state.layout.activityBar) {
                this.collapsePanel(this.state.layout.activityBar);
            }

            // Show the new panel
            this.state.layout.activityBar = panelId;
            panel.classList.remove('panel-collapsed');
            this.state.collapsedPanels.delete(panelId);

            const btn = this.root.querySelector(`.activity-bar-item[data-panel="${panelId}"]`);
            if (btn) btn.classList.add('active');

            // Restore sidebar width
            if (this.root.classList.contains('sidebar-collapsed')) {
                this.root.classList.remove('sidebar-collapsed');
            }
        }

        this.saveLayout();
    }

    collapsePanel(panelId) {
        const panel = this.root.querySelector(`.panel[data-panel-id="${panelId}"]`);
        if (panel) {
            panel.classList.add('panel-collapsed');
            this.state.collapsedPanels.add(panelId);
        }
    }

    // ————— Tabs —————

    bindTabs() {
        this.root.addEventListener('click', (e) => {
            // Tab switching
            const tab = e.target.closest('.panel-tab:not(.panel-tab-close)');
            if (tab) {
                const tabGroup = tab.closest('.panel-tabs');
                if (tabGroup) {
                    tabGroup.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
                    tab.classList.add('active');
                    this.switchTabContent(tab);
                }
            }

            // Tab close
            const closeBtn = e.target.closest('.panel-tab-close');
            if (closeBtn) {
                e.stopPropagation();
                this.closeTab(closeBtn.closest('.panel-tab'));
            }
        });
    }

    switchTabContent(tab) {
        const panel = tab.closest('.panel');
        if (!panel) return;

        const body = panel.querySelector('.panel-body');
        if (!body) return;

        const targetId = tab.dataset.tabTarget;
        if (targetId) {
            // Show all tab contents
            panel.querySelectorAll('[data-tab-content]').forEach(el => {
                el.style.display = el.dataset.tabContent === targetId ? '' : 'none';
            });
        }
    }

    closeTab(tab) {
        if (!tab) return;

        const tabGroup = tab.closest('.panel-tabs');
        if (!tabGroup) return;

        const wasActive = tab.classList.contains('active');
        tab.remove();

        // Recalculate tab contents if needed
        if (tab.dataset.tabTarget) {
            const content = tab.closest('.panel')?.querySelector(`[data-tab-content="${tab.dataset.tabTarget}"]`);
            if (content) content.remove();
        }

        if (wasActive) {
            const remaining = tabGroup.querySelector('.panel-tab');
            if (remaining) {
                remaining.classList.add('active');
                this.switchTabContent(remaining);
            }
        }
    }

    openTab(panelId, tabConfig) {
        const panel = this.root.querySelector(`.panel[data-panel-id="${panelId}"]`);
        if (!panel) return;

        let tabGroup = panel.querySelector('.panel-tabs');
        if (!tabGroup) {
            tabGroup = document.createElement('div');
            tabGroup.className = 'panel-tabs';
            panel.insertBefore(tabGroup, panel.querySelector('.panel-body'));
        }

        const tab = document.createElement('div');
        tab.className = 'panel-tab' + (tabConfig.active ? ' active' : '');
        tab.dataset.tabTarget = tabConfig.id;
        tab.innerHTML = `
            ${tabConfig.icon || ''}
            <span>${tabConfig.title}</span>
            <button class="panel-tab-close" title="Close">&times;</button>
        `;

        tabGroup.appendChild(tab);
        this.switchTabContent(tab);
    }

    // ————— Collapse Buttons —————

    bindCollapseButtons() {
        this.root.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-action="collapse-panel"]');
            if (btn) {
                const panel = btn.closest('.panel');
                if (panel) {
                    panel.classList.toggle('panel-collapsed');
                    const isCollapsed = panel.classList.contains('panel-collapsed');
                    if (isCollapsed) {
                        this.state.collapsedPanels.add(panel.dataset.panelId);
                    } else {
                        this.state.collapsedPanels.delete(panel.dataset.panelId);
                    }
                    this.saveLayout();
                }
            }

            // Toggle sidebar
            const toggleSidebar = e.target.closest('[data-action="toggle-sidebar"]');
            if (toggleSidebar) {
                this.toggleSidebar();
            }

            // Toggle right panel
            const toggleRight = e.target.closest('[data-action="toggle-right"]');
            if (toggleRight) {
                this.toggleRightPanel();
            }
        });
    }

    toggleSidebar() {
        this.root.classList.toggle('sidebar-collapsed');
        this.state.layout.sidebarCollapsed = this.root.classList.contains('sidebar-collapsed');
        this.saveLayout();
    }

    toggleRightPanel() {
        this.root.classList.toggle('right-collapsed');
        this.state.layout.rightCollapsed = this.root.classList.contains('right-collapsed');
        this.saveLayout();
    }

    // ————— Keyboard Shortcuts —————

    bindKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+B — toggle sidebar
            if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
                e.preventDefault();
                this.toggleSidebar();
            }

            // Ctrl+W — close active tab
            if ((e.ctrlKey || e.metaKey) && e.key === 'w') {
                e.preventDefault();
                const activeTab = this.root.querySelector('.panel-tab.active');
                if (activeTab) this.closeTab(activeTab);
            }

            // Ctrl+Tab — switch to next tab
            if ((e.ctrlKey || e.metaKey) && e.key === 'Tab') {
                e.preventDefault();
                this.switchToNextTab();
            }

            // Ctrl+Shift+Tab — switch to previous tab
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'Tab') {
                e.preventDefault();
                this.switchToPrevTab();
            }

            // Escape — close omnibox
            if (e.key === 'Escape') {
                this.closeOmnibox();
            }
        });
    }

    switchToNextTab() {
        const tabs = this.root.querySelectorAll('.panel-tab');
        const active = this.root.querySelector('.panel-tab.active');
        if (!active && tabs.length > 0) {
            tabs[0].classList.add('active');
            this.switchTabContent(tabs[0]);
            return;
        }
        const idx = Array.from(tabs).indexOf(active);
        const next = tabs[(idx + 1) % tabs.length];
        if (next) {
            active.classList.remove('active');
            next.classList.add('active');
            this.switchTabContent(next);
        }
    }

    switchToPrevTab() {
        const tabs = this.root.querySelectorAll('.panel-tab');
        const active = this.root.querySelector('.panel-tab.active');
        if (!active && tabs.length > 0) {
            tabs[tabs.length - 1].classList.add('active');
            this.switchTabContent(tabs[tabs.length - 1]);
            return;
        }
        const idx = Array.from(tabs).indexOf(active);
        const prev = tabs[(idx - 1 + tabs.length) % tabs.length];
        if (prev) {
            active.classList.remove('active');
            prev.classList.add('active');
            this.switchTabContent(prev);
        }
    }

    closeOmnibox() {
        const omnibox = document.querySelector('.omnibox-overlay.open');
        if (omnibox) {
            omnibox.classList.remove('open');
            document.body.classList.remove('omnibox-open');
        }
    }

    // ————— Layout Restoration —————

    restoreLayout() {
        // Restore panel widths from data attributes
        this.root.querySelectorAll('.panel').forEach(panel => {
            if (panel.dataset.defaultWidth) {
                panel.style.width = panel.dataset.defaultWidth + 'px';
                panel.style.flex = 'none';
            }
        });
    }

    applyLayout() {
        // Dispatch event that layout is ready
        this.root.dispatchEvent(new CustomEvent('panel-layout-ready', {
            detail: { system: this }
        }));
    }

    // ————— Public API —————

    setLayout(layout) {
        this.state.layout = { ...this.state.layout, ...layout };
        this.applyLayout();
        this.saveLayout();
    }

    getLayout() {
        return { ...this.state.layout };
    }

    resetLayout() {
        localStorage.removeItem(this.options.storageKey);
        this.state.layout = this.getDefaultLayout();
        this.applyLayout();
        this.saveLayout();
    }
}

// ————— Omnibox / Command Palette —————

class Omnibox {
    constructor(options = {}) {
        this.options = {
            placeholder: 'Поиск дел, документов, команд...',
            items: [],
            onSelect: null,
            ...options
        };

        this.state = {
            open: false,
            query: '',
            selectedIndex: 0
        };

        this.render();
        this.bindEvents();
    }

    render() {
        // Create overlay if not exists
        this.overlay = document.createElement('div');
        this.overlay.className = 'omnibox-overlay';
        this.overlay.innerHTML = `
            <div class="omnibox">
                <div class="omnibox-input-wrapper">
                    <span class="omnibox-search-icon">&#128269;</span>
                    <input type="text" class="omnibox-input" placeholder="${this.options.placeholder}" autofocus>
                    <span class="omnibox-shortcut-hint">ESC</span>
                </div>
                <div class="omnibox-results"></div>
                <div class="omnibox-footer">
                    <div class="omnibox-footer-commands">
                        <span class="omnibox-footer-command"><kbd>&uarr;</kbd> <kbd>&darr;</kbd> Навигация</span>
                        <span class="omnibox-footer-command"><kbd>&crarr;</kbd> Выбрать</span>
                        <span class="omnibox-footer-command"><kbd>ESC</kbd> Закрыть</span>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(this.overlay);
        this.input = this.overlay.querySelector('.omnibox-input');
        this.resultsEl = this.overlay.querySelector('.omnibox-results');
    }

    bindEvents() {
        this.input.addEventListener('input', () => {
            this.state.query = this.input.value;
            this.state.selectedIndex = 0;
            this.filterResults();
        });

        this.input.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    this.state.selectedIndex = Math.min(this.state.selectedIndex + 1, this.getFilteredItems().length - 1);
                    this.highlightItem();
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    this.state.selectedIndex = Math.max(this.state.selectedIndex - 1, 0);
                    this.highlightItem();
                    break;
                case 'Enter':
                    e.preventDefault();
                    this.selectItem();
                    break;
                case 'Escape':
                    this.close();
                    break;
            }
        });

        // Click on items
        this.resultsEl.addEventListener('click', (e) => {
            const item = e.target.closest('.omnibox-item');
            if (item) {
                const idx = Array.from(item.parentElement.children).indexOf(item);
                this.state.selectedIndex = idx;
                this.selectItem();
            }
        });

        // Close on overlay click
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) this.close();
        });

        // Global shortcut
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
                e.preventDefault();
                this.toggle();
            }
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'p') {
                e.preventDefault();
                this.toggle();
            }
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.toggle();
            }
        });
    }

    getFilteredItems() {
        if (!this.state.query) return this.options.items;
        const q = this.state.query.toLowerCase();
        return this.options.items.filter(item =>
            item.title.toLowerCase().includes(q) ||
            (item.description && item.description.toLowerCase().includes(q))
        );
    }

    filterResults() {
        const filtered = this.getFilteredItems();

        if (filtered.length === 0) {
            this.resultsEl.innerHTML = `
                <div class="omnibox-empty">
                    <div class="omnibox-empty-icon">&#128270;</div>
                    <div class="omnibox-empty-text">Ничего не найдено</div>
                </div>
            `;
            return;
        }

        // Group by section
        const sections = {};
        filtered.forEach(item => {
            const section = item.section || 'Общее';
            if (!sections[section]) sections[section] = [];
            sections[section].push(item);
        });

        let html = '';
        Object.entries(sections).forEach(([sectionName, items]) => {
            html += `<div class="omnibox-section">
                <div class="omnibox-section-title">${sectionName}</div>`;
            items.forEach((item, idx) => {
                const isActive = this.state.selectedIndex === html.match(/omnibox-item/g)?.length || 0;
                html += `
                    <div class="omnibox-item ${isActive ? 'active' : ''}" data-action="${item.action || ''}">
                        <div class="omnibox-item-icon">${item.icon || '&#128196;'}</div>
                        <div class="omnibox-item-content">
                            <div class="omnibox-item-title">${this.highlightText(item.title)}</div>
                            ${item.description ? `<div class="omnibox-item-description">${this.highlightText(item.description)}</div>` : ''}
                        </div>
                        ${item.shortcut ? `<div class="omnibox-item-shortcut">${item.shortcut}</div>` : ''}
                    </div>
                `;
            });
            html += '</div>';
        });

        this.resultsEl.innerHTML = html;
    }

    highlightText(text) {
        if (!this.state.query) return text;
        const q = this.state.query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        return text.replace(new RegExp(`(${q})`, 'gi'), '<strong>$1</strong>');
    }

    highlightItem() {
        const items = this.resultsEl.querySelectorAll('.omnibox-item');
        items.forEach((el, idx) => {
            el.classList.toggle('active', idx === this.state.selectedIndex);
        });
        items[this.state.selectedIndex]?.scrollIntoView({ block: 'nearest' });
    }

    selectItem() {
        const items = this.resultsEl.querySelectorAll('.omnibox-item');
        const selected = items[this.state.selectedIndex];
        if (!selected) return;

        if (this.options.onSelect) {
            const filtered = this.getFilteredItems();
            this.options.onSelect(filtered[this.state.selectedIndex]);
        }

        this.close();
    }

    open() {
        this.state.open = true;
        this.overlay.classList.add('open');
        document.body.classList.add('omnibox-open');
        this.state.selectedIndex = 0;
        this.state.query = '';
        this.input.value = '';
        this.filterResults();
        setTimeout(() => this.input.focus(), 100);
    }

    close() {
        this.state.open = false;
        this.overlay.classList.remove('open');
        document.body.classList.remove('omnibox-open');
    }

    toggle() {
        this.state.open ? this.close() : this.open();
    }

    setItems(items) {
        this.options.items = items;
        if (this.state.open) this.filterResults();
    }
}

// ————— Auto-initialize on DOM ready —————

document.addEventListener('DOMContentLoaded', () => {
    // Initialize panel system if container exists
    const container = document.querySelector('.panel-layout');
    if (container && !container.dataset.panelInitialized) {
        container.dataset.panelInitialized = 'true';
        window.panelSystem = new PanelSystem(container, {
            role: document.body.dataset.role || 'default'
        });
    }

    // Initialize omnibox
    if (!window.omnibox) {
        window.omnibox = new Omnibox({
            placeholder: 'Поиск дел, документов, команд...',
            items: [
                { title: 'Все дела', description: 'Перейти к списку дел', icon: '&#128203;', section: 'Навигация', action: 'cases' },
                { title: 'Документы', description: 'Перейти к документам', icon: '&#128196;', section: 'Навигация', action: 'documents' },
                { title: 'Дашборд', description: 'Главная панель управления', icon: '&#128202;', section: 'Навигация', action: 'dashboard' },
                { title: 'Поиск по базе знаний', description: 'Искать в юридической базе', icon: '&#128269;', section: 'Поиск', action: 'search-knowledge' },
                { title: 'Создать дело', description: 'Новое судебное дело', icon: '&#10133;', section: 'Действия', action: 'new-case' },
                { title: 'Создать документ', description: 'Новый документ', icon: '&#10133;', section: 'Действия', action: 'new-doc' }
            ],
            onSelect: (item) => {
                if (item.action) {
                    // Handle navigation
                    const links = { cases: '/cases', documents: '/documents', dashboard: '/' };
                    if (links[item.action]) {
                        window.location.href = links[item.action];
                    }
                }
            }
        });
    }
});
