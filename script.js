/**
 * Resizable Panels for MoEngage API Documentation
 * Adds a draggable resize handle between request and response code panels
 */

(function() {
  'use strict';

  const CONFIG = {
    minPanelHeight: 80,
    debounceDelay: 100,
    initDelay: 300
  };

  const initializedContainers = new WeakSet();
  let observerTimeout = null;

  function createDragHandle() {
    const handle = document.createElement('div');
    handle.className = 'moe-resize-handle';
    handle.innerHTML = '<div class="moe-resize-handle-dots"><span></span><span></span><span></span></div>';
    handle.setAttribute('role', 'separator');
    handle.setAttribute('aria-orientation', 'horizontal');
    handle.setAttribute('aria-label', 'Drag to resize panels');
    handle.setAttribute('tabindex', '0');
    return handle;
  }

  // Get the actual content height of a panel
  function getContentHeight(panel) {
    // Try to find the code content inside
    const pre = panel.querySelector('pre');
    const codeRegion = panel.querySelector('[role="region"]');
    const codeBlock = panel.querySelector('[class*="codeblock"]');
    
    // Get the scrollHeight of the content element
    let contentHeight = 0;
    
    if (pre) {
      contentHeight = pre.scrollHeight;
    } else if (codeRegion) {
      contentHeight = codeRegion.scrollHeight;
    } else if (codeBlock) {
      contentHeight = codeBlock.scrollHeight;
    }
    
    // Add padding for headers, tabs, etc. (approximately 80px)
    // Also account for the panel's own padding
    const headerHeight = 80;
    
    // Return at least the current height or the content height
    return Math.max(contentHeight + headerHeight, panel.scrollHeight, CONFIG.minPanelHeight);
  }

  function initializeResizer(topPanel, bottomPanel, handle) {
    let isResizing = false;
    let startY = 0;
    let startTopHeight = 0;
    let startBottomHeight = 0;
    let maxTopHeight = 0;
    let maxBottomHeight = 0;

    const startResize = (e) => {
      isResizing = true;
      startY = e.clientY || (e.touches && e.touches[0].clientY);
      
      startTopHeight = topPanel.getBoundingClientRect().height;
      startBottomHeight = bottomPanel.getBoundingClientRect().height;
      
      // Calculate maximum heights based on content
      // This prevents expanding beyond content (which causes grey area)
      maxTopHeight = getContentHeight(topPanel);
      maxBottomHeight = getContentHeight(bottomPanel);

      document.body.classList.add('moe-resizing');
      handle.classList.add('moe-resize-handle--active');
      
      e.preventDefault();
      e.stopPropagation();
    };

    const doResize = (e) => {
      if (!isResizing) return;

      const currentY = e.clientY || (e.touches && e.touches[0].clientY);
      const deltaY = currentY - startY;

      let newTopHeight = startTopHeight + deltaY;
      let newBottomHeight = startBottomHeight - deltaY;

      const totalHeight = startTopHeight + startBottomHeight;
      
      // Enforce MINIMUM heights
      if (newTopHeight < CONFIG.minPanelHeight) {
        newTopHeight = CONFIG.minPanelHeight;
        newBottomHeight = totalHeight - CONFIG.minPanelHeight;
      }
      if (newBottomHeight < CONFIG.minPanelHeight) {
        newBottomHeight = CONFIG.minPanelHeight;
        newTopHeight = totalHeight - CONFIG.minPanelHeight;
      }
      
      // Enforce MAXIMUM heights (prevent grey area)
      // Only cap if expanding beyond content
      if (newTopHeight > maxTopHeight && deltaY > 0) {
        newTopHeight = maxTopHeight;
        newBottomHeight = totalHeight - maxTopHeight;
      }
      if (newBottomHeight > maxBottomHeight && deltaY < 0) {
        newBottomHeight = maxBottomHeight;
        newTopHeight = totalHeight - maxBottomHeight;
      }
      
      // Make sure we don't go below minimum after max capping
      if (newBottomHeight < CONFIG.minPanelHeight) {
        newBottomHeight = CONFIG.minPanelHeight;
        newTopHeight = totalHeight - CONFIG.minPanelHeight;
      }
      if (newTopHeight < CONFIG.minPanelHeight) {
        newTopHeight = CONFIG.minPanelHeight;
        newBottomHeight = totalHeight - CONFIG.minPanelHeight;
      }

      topPanel.style.height = `${newTopHeight}px`;
      topPanel.style.maxHeight = `${newTopHeight}px`;
      topPanel.style.overflow = 'auto';
      
      bottomPanel.style.height = `${newBottomHeight}px`;
      bottomPanel.style.maxHeight = `${newBottomHeight}px`;
      bottomPanel.style.overflow = 'auto';
    };

    const stopResize = () => {
      if (!isResizing) return;
      isResizing = false;
      document.body.classList.remove('moe-resizing');
      handle.classList.remove('moe-resize-handle--active');
    };

    handle.addEventListener('mousedown', startResize);
    document.addEventListener('mousemove', doResize);
    document.addEventListener('mouseup', stopResize);

    handle.addEventListener('touchstart', startResize, { passive: false });
    document.addEventListener('touchmove', doResize, { passive: false });
    document.addEventListener('touchend', stopResize);

    handle.addEventListener('keydown', (e) => {
      const step = 30;
      let topHeight = topPanel.getBoundingClientRect().height;
      let bottomHeight = bottomPanel.getBoundingClientRect().height;
      
      // Recalculate max heights
      const currentMaxTop = getContentHeight(topPanel);
      const currentMaxBottom = getContentHeight(bottomPanel);

      if (e.key === 'ArrowUp' && topHeight > CONFIG.minPanelHeight + step) {
        e.preventDefault();
        topPanel.style.height = `${topHeight - step}px`;
        topPanel.style.maxHeight = `${topHeight - step}px`;
        const newBottomHeight = Math.min(bottomHeight + step, currentMaxBottom);
        bottomPanel.style.height = `${newBottomHeight}px`;
        bottomPanel.style.maxHeight = `${newBottomHeight}px`;
      } else if (e.key === 'ArrowDown' && bottomHeight > CONFIG.minPanelHeight + step) {
        e.preventDefault();
        const newTopHeight = Math.min(topHeight + step, currentMaxTop);
        topPanel.style.height = `${newTopHeight}px`;
        topPanel.style.maxHeight = `${newTopHeight}px`;
        bottomPanel.style.height = `${bottomHeight - step}px`;
        bottomPanel.style.maxHeight = `${bottomHeight - step}px`;
      }
    });

    handle.addEventListener('dblclick', () => {
      topPanel.style.height = '';
      topPanel.style.maxHeight = '';
      topPanel.style.overflow = '';
      bottomPanel.style.height = '';
      bottomPanel.style.maxHeight = '';
      bottomPanel.style.overflow = '';
    });
  }

  function setupResizablePanels() {
    const sideLayout = document.getElementById('content-side-layout');
    if (!sideLayout) return;
    if (sideLayout.querySelector('.moe-resize-handle')) return;

    const codeGroups = sideLayout.querySelectorAll('.code-group');
    const codeRegions = sideLayout.querySelectorAll('[role="region"][aria-label*="Code"]');
    
    let panels = codeGroups.length >= 2 ? Array.from(codeGroups) : Array.from(codeRegions);
    
    if (panels.length < 2) {
      const allDivs = sideLayout.querySelectorAll(':scope > div > div');
      panels = Array.from(allDivs).filter(div => 
        div.querySelector('pre') || 
        div.querySelector('code') || 
        div.classList.contains('code-group') ||
        div.getAttribute('role') === 'region'
      );
    }

    if (panels.length < 2) return;

    const topPanel = panels[0];
    const bottomPanel = panels[1];

    if (initializedContainers.has(topPanel)) return;

    let commonParent = topPanel.parentElement;
    while (commonParent && !commonParent.contains(bottomPanel)) {
      commonParent = commonParent.parentElement;
    }

    const handle = createDragHandle();
    
    if (topPanel.nextElementSibling === bottomPanel) {
      topPanel.after(handle);
      initializeResizer(topPanel, bottomPanel, handle);
    } else {
      let topWrapper = topPanel;
      while (topWrapper.parentElement !== commonParent && topWrapper.parentElement) {
        topWrapper = topWrapper.parentElement;
      }
      
      let bottomWrapper = bottomPanel;
      while (bottomWrapper.parentElement !== commonParent && bottomWrapper.parentElement) {
        bottomWrapper = bottomWrapper.parentElement;
      }
      
      if (topWrapper !== bottomWrapper) {
        topWrapper.after(handle);
        initializeResizer(topWrapper, bottomWrapper, handle);
      }
    }

    initializedContainers.add(topPanel);
  }

  function setupByPosition() {
    const sideLayout = document.getElementById('content-side-layout');
    if (!sideLayout) return;
    if (sideLayout.querySelector('.moe-resize-handle')) return;

    const children = Array.from(sideLayout.children);
    const codePanels = children.filter(child => {
      const rect = child.getBoundingClientRect();
      const hasCode = child.querySelector('pre, code, .code-group, [role="region"]');
      return rect.height > 50 && hasCode;
    });

    if (codePanels.length >= 2) {
      const topPanel = codePanels[0];
      const bottomPanel = codePanels[1];
      
      if (initializedContainers.has(topPanel)) return;
      
      const handle = createDragHandle();
      topPanel.after(handle);
      initializeResizer(topPanel, bottomPanel, handle);
      initializedContainers.add(topPanel);
    }
  }

  function trySetup() {
    setupResizablePanels();
    setupByPosition();
  }

  // Reset panel sizes (used when zoom changes)
  function resetPanelSizes() {
    const sideLayout = document.getElementById('content-side-layout');
    if (!sideLayout) return;
    
    // Find all panels that have been resized (have inline height style)
    const resizedPanels = sideLayout.querySelectorAll('[style*="height"]');
    resizedPanels.forEach(panel => {
      panel.style.height = '';
      panel.style.maxHeight = '';
      panel.style.overflow = '';
    });
  }

  function init() {
    trySetup();
    setTimeout(trySetup, CONFIG.initDelay);

    const observer = new MutationObserver(() => {
      if (observerTimeout) clearTimeout(observerTimeout);
      observerTimeout = setTimeout(trySetup, CONFIG.debounceDelay);
    });

    observer.observe(document.body, { childList: true, subtree: true });

    ['popstate', 'hashchange'].forEach(event => {
      window.addEventListener(event, () => setTimeout(trySetup, 200));
    });

    // Reset panels on window resize (includes zoom changes)
    let resizeTimeout;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        resetPanelSizes();
      }, 150);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.addEventListener('load', () => setTimeout(trySetup, 500));
})();


/**
 * System Status Indicator
 *
 * Shows the live rollup from status.moengage.com (Atlassian Statuspage) as a
 * pill in the navbar, in one of four states:
 *
 *   operational  green  all clear
 *   degraded     amber  something is impaired but serving
 *   major        red    a real outage
 *   unavailable  grey   the status API could not be reached, so we do not know
 *
 * The grey state matters: a failed fetch must never be painted as an outage.
 */

(function() {
  'use strict';

  const CONFIG = {
    /* The rollup endpoint is 216 bytes and sends access-control-allow-origin: *,
       so it reads straight from the browser with no proxy. summary.json carries
       the same rollup plus 186 per-region components, far more than a
       chrome-level indicator needs. */
    apiUrl: 'https://status.moengage.com/api/v2/status.json',
    pageUrl: 'https://status.moengage.com',
    cacheKey: 'moe-system-status',
    cacheTtl: 60 * 1000,
    refreshInterval: 5 * 60 * 1000,
    requestTimeout: 5000,
    debounceDelay: 100
  };

  /* Statuspage reports five indicators; we collapse them into four states.
     critical joins major because both mean "down", and maintenance joins
     degraded because planned work still impairs service - painting it green
     would be wrong and painting it red would be alarmist. */
  const INDICATORS = {
    none: 'operational',
    minor: 'degraded',
    major: 'major',
    critical: 'major',
    maintenance: 'degraded'
  };

  /* Short labels keep the navbar tight. The API's own status.description is
     human-authored and longer ("Partial System Outage"), so it goes in the
     tooltip instead, where it can never contradict the status page. */
  const LABELS = {
    operational: 'Operational',
    degraded: 'Degraded',
    major: 'Major Outage',
    unavailable: 'Status Unavailable'
  };

  const UNKNOWN = { state: 'unavailable', label: LABELS.unavailable, detail: 'Could not reach the status page' };

  let current = null;
  let observerTimeout = null;
  let inFlight = false;

  // sessionStorage throws outright in some embedding contexts, so every access
  // is guarded and a failure just means we refetch.
  function readCache() {
    try {
      const raw = sessionStorage.getItem(CONFIG.cacheKey);
      if (!raw) return null;
      const cached = JSON.parse(raw);
      if (!cached || Date.now() - cached.at > CONFIG.cacheTtl) return null;
      return cached.status;
    } catch (e) {
      return null;
    }
  }

  function writeCache(status) {
    try {
      sessionStorage.setItem(CONFIG.cacheKey, JSON.stringify({ at: Date.now(), status: status }));
    } catch (e) {
      /* Private mode or blocked storage: polling still works, just uncached. */
    }
  }

  // Local-only override so every state can be previewed in mint dev without
  // waiting for a real incident: ?moe-status=major
  function debugOverride() {
    const host = window.location.hostname;
    if (host !== 'localhost' && host !== '127.0.0.1') return null;
    const key = new URLSearchParams(window.location.search).get('moe-status');
    if (!key || !LABELS[key]) return null;
    return { state: key, label: LABELS[key], detail: LABELS[key] };
  }

  function normalize(payload) {
    const status = payload && payload.status;
    if (!status || !INDICATORS[status.indicator]) return null;
    const state = INDICATORS[status.indicator];
    return {
      state: state,
      label: LABELS[state],
      detail: (status.description || '').trim() || LABELS[state]
    };
  }

  function fetchStatus() {
    if (inFlight) return Promise.resolve(current);
    inFlight = true;

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), CONFIG.requestTimeout);

    return fetch(CONFIG.apiUrl, { signal: controller.signal, mode: 'cors' })
      .then(response => (response.ok ? response.json() : null))
      .then(payload => {
        const status = normalize(payload);
        if (status) writeCache(status);
        return status;
      })
      .catch(() => null)
      .then(status => {
        clearTimeout(timer);
        inFlight = false;
        /* Prefer the last known good reading over grey: a single dropped poll on
           the reader's flaky wifi should not start claiming we are unreachable. */
        return status || current || UNKNOWN;
      });
  }

  function buildPill(status) {
    const link = document.createElement('a');
    link.className = 'moe-status-pill';
    link.setAttribute('data-moe-status', status.state);
    link.href = CONFIG.pageUrl;
    link.target = '_blank';
    link.rel = 'noreferrer';
    // Carries the full wording for the compact, dot-only mobile rendering.
    link.title = status.detail;

    const dot = document.createElement('span');
    dot.className = 'moe-status-dot';
    dot.setAttribute('aria-hidden', 'true');

    const label = document.createElement('span');
    label.className = 'moe-status-pill-label';
    label.textContent = status.label;

    link.appendChild(dot);
    link.appendChild(label);
    return link;
  }

  /* Two navbar slots, because Mintlify renders two navbars and swaps them at its
     lg breakpoint. The desktop link list sits inside a `hidden lg:flex` wrapper,
     so a pill placed there is display:none below 1024px; the icon row beside the
     mobile search is `flex lg:hidden`. A slot in each covers every width.

     Each slot is a live region. Only one is ever displayed, and a live region
     inside a display:none ancestor is not announced, so a state change is
     announced once rather than twice.

     Both are created empty and toggled with the hidden attribute. The desktop
     list is space-x-6 (margin-inline-end on :not(:last-child)) and the mobile
     row is gap-3, but a hidden element is display:none and generates no box, so
     neither spacing rule renders while the slot is empty. */
  function makeSlot(tag, className) {
    const slot = document.createElement(tag);
    slot.className = className;
    slot.setAttribute('role', 'status');
    slot.setAttribute('aria-live', 'polite');
    slot.hidden = true;
    return slot;
  }

  function desktopSlot() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return null;

    const existing = navbar.querySelector('.moe-status-navbar');
    if (existing) return existing;

    const list = navbar.querySelector('ul');
    if (!list) return null;

    const slot = makeSlot('li', 'navbar-link moe-status-navbar');
    list.insertBefore(slot, list.firstChild);
    return slot;
  }

  function mobileSlot() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return null;

    const existing = navbar.querySelector('.moe-status-navbar-mobile');
    if (existing) return existing;

    // The mobile icon row (search, menu). Matched on utility classes rather than
    // a generated hash, the same way the footer rules in style.css do.
    const row = Array.from(navbar.querySelectorAll('div')).find(
      div =>
        typeof div.className === 'string' &&
        div.className.indexOf('lg:hidden') !== -1 &&
        div.className.indexOf('items-center') !== -1
    );
    if (!row) return null;

    const slot = makeSlot('span', 'moe-status-navbar-mobile');
    row.insertBefore(slot, row.firstChild);
    return slot;
  }

  function fillSlot(slot, status) {
    if (!slot) return;

    if (!status) {
      slot.hidden = true;
      slot.textContent = '';
      delete slot.dataset.moeStatus;
      return;
    }

    // Idempotent: the MutationObserver fires constantly, and rebuilding the pill
    // every time would restart its pulse animation on each mutation.
    if (slot.dataset.moeStatus === status.state && slot.dataset.moeLabel === status.label) {
      slot.hidden = false;
      return;
    }

    slot.dataset.moeStatus = status.state;
    slot.dataset.moeLabel = status.label;
    slot.textContent = '';
    slot.appendChild(buildPill(status));
    slot.hidden = false;
  }

  function render() {
    fillSlot(desktopSlot(), current);
    fillSlot(mobileSlot(), current);
  }

  function refresh(force) {
    const override = debugOverride();
    if (override) {
      current = override;
      render();
      return;
    }

    const cached = !force && readCache();
    if (cached) {
      current = cached;
      render();
      return;
    }

    fetchStatus().then(status => {
      current = status;
      render();
    });
  }

  function init() {
    refresh(false);

    // Mintlify routes on the client, so the navbar is torn down and rebuilt
    // without a page load. Re-render on mutation, same contract as the
    // resizable-panels observer above.
    const observer = new MutationObserver(() => {
      if (observerTimeout) clearTimeout(observerTimeout);
      observerTimeout = setTimeout(render, CONFIG.debounceDelay);
    });
    observer.observe(document.body, { childList: true, subtree: true });

    // Docs tabs stay open for hours. Poll while visible, stop while hidden, and
    // catch up on return rather than burning requests in a background tab.
    setInterval(() => {
      if (!document.hidden) refresh(true);
    }, CONFIG.refreshInterval);

    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) refresh(false);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
