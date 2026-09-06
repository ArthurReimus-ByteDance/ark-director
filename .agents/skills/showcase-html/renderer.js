// renderer.js — reads the #showcase-data JSON and renders the page.
// Inlined into template.html by scripts/generate_showcase.py.

(function () {
  const raw = document.getElementById('showcase-data').textContent;
  const data = JSON.parse(raw);
  const viaServer = location.protocol === 'http:' || location.protocol === 'https:';

  const el = (tag, cls, text) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  };

  // collect selectable ASSETS: assetId -> {manifest, field, key}
  // (many cards can share one assetId; each card carries its own filename)
  const selectable = {};
  (function () {
    for (const s of data.sections) {
      for (const c of (s.cards || [])) {
        if (c.id && c.manifest) {
          selectable[c.id] = {
            manifest: c.manifest, field: c.field || 'selected_variant',
            key: c.key || null,
          };
        }
      }
    }
  })();
  const selections = {}; // assetId -> filename

  // ---- nav ----
  const nav = el('nav');
  const navInner = el('div', 'inner');
  const brand = el('span', 'brand');
  brand.appendChild(document.createTextNode('Showcase'));
  const sep = el('span');
  sep.textContent = '·';
  brand.appendChild(sep);
  navInner.appendChild(brand);
  for (const s of data.sections) {
    const a = el('a', null, s.title);
    a.href = '#' + s.id;
    navInner.appendChild(a);
  }
  nav.appendChild(navInner);
  document.body.insertBefore(nav, document.body.firstChild);
  document.title = data.title;

  // ---- header ----
  const header = el('header');
  if (data.kicker) header.appendChild(el('div', 'kicker', data.kicker));
  header.appendChild(el('h1', null, data.title));
  if (data.lede) header.appendChild(el('p', 'lede', data.lede));
  if (data.badges && data.badges.length) {
    const badges = el('div', 'badges');
    for (const b of data.badges) {
      const span = el('span', 'badge');
      if (b.label) span.appendChild(document.createTextNode(b.label + ' '));
      span.appendChild(el('b', null, b.value));
      badges.appendChild(span);
    }
    header.appendChild(badges);
  }
  document.getElementById('app').appendChild(header);

  // ---- selection toolbar ----
  // Server mode: full select + save. Plain file:// : read-only preview.
  const selIds = Object.keys(selectable);
  let selToolbar = null, selStatus = null, selSave = null;
  if (selIds.length) {
    selToolbar = el('div', 'sel-bar');
    if (viaServer) {
      selStatus = el('span', 'sel-status', 'Pick variants, then press Ctrl+S (⌘S) to save.');
      selSave = el('button', 'sel-save', 'Save (Ctrl+S)');
      selSave.addEventListener('click', saveSelections);
      selToolbar.appendChild(selStatus);
      selToolbar.appendChild(selSave);
    } else {
      selToolbar.appendChild(el('span', 'sel-status',
        'Read-only preview — run with --serve to select and save variants.'));
    }
    document.getElementById('app').appendChild(selToolbar);
  }

  // ---- main ----
  const main = el('main');
  for (const s of data.sections) {
    main.appendChild(buildSection(s));
  }
  document.getElementById('app').appendChild(main);

  // ---- lightbox (click image to view fullscreen) ----
  const lb = el('div', 'lightbox');
  const lbImg = document.createElement('img');
  const lbClose = el('button', 'lb-close', '×');
  lbClose.setAttribute('aria-label', 'Close');
  const lbPrev = el('button', 'lb-nav lb-prev', '‹');
  const lbNext = el('button', 'lb-nav lb-next', '›');
  const lbCount = el('div', 'lb-count');
  lb.appendChild(lbImg);
  lb.appendChild(lbClose);
  lb.appendChild(lbPrev);
  lb.appendChild(lbNext);
  lb.appendChild(lbCount);
  document.body.appendChild(lb);

  const zoomable = Array.from(document.querySelectorAll('.media-frame img'));
  let zoomIdx = -1;

  function openZoom(i) {
    zoomIdx = (i + zoomable.length) % zoomable.length;
    const img = zoomable[zoomIdx];
    lbImg.src = img.src;
    lbImg.alt = img.alt || '';
    lbCount.textContent = (zoomIdx + 1) + ' / ' + zoomable.length;
    lb.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  }
  function closeZoom() {
    lb.style.display = 'none';
    document.body.style.overflow = '';
  }
  zoomable.forEach((img, i) => {
    img.addEventListener('click', () => openZoom(i));
  });
  lbClose.addEventListener('click', closeZoom);
  lbPrev.addEventListener('click', (e) => { e.stopPropagation(); openZoom(zoomIdx - 1); });
  lbNext.addEventListener('click', (e) => { e.stopPropagation(); openZoom(zoomIdx + 1); });
  lb.addEventListener('click', (e) => {
    if (e.target === lb) closeZoom();
  });
  document.addEventListener('keydown', (e) => {
    if (lb.style.display !== 'flex') return;
    if (e.key === 'Escape') closeZoom();
    else if (e.key === 'ArrowLeft') openZoom(zoomIdx - 1);
    else if (e.key === 'ArrowRight') openZoom(zoomIdx + 1);
  });

  if (data.footer) {
    const footer = el('footer');
    footer.appendChild(el('p', null, data.footer));
    document.getElementById('app').appendChild(footer);
  }

  function buildSection(s) {
    const section = el('section');
    section.id = s.id;

    const head = el('div', 'section-head');
    if (s.icon) {
      const ic = el('span', 'icon', s.icon);
      ic.style.background = s.iconBg || 'var(--accent-soft)';
      head.appendChild(ic);
    }
    head.appendChild(el('h2', null, s.title));
    if (s.count) head.appendChild(el('span', 'count', s.count));
    section.appendChild(head);

    if (s.desc) section.appendChild(el('div', 'section-desc', s.desc));

    if (s.kind === 'table') {
      section.appendChild(buildTable(s));
    } else if (s.kind === 'panel') {
      section.appendChild(buildPanel(s));
    } else {
      const grid = el('div', s.mediaOnly ? 'grid media-only' : 'grid');
      for (const c of (s.cards || [])) grid.appendChild(buildCard(c));
      section.appendChild(grid);
    }
    return section;
  }

  function buildCard(c) {
    const card = el('div', 'card ' + (c.type || 'video'));
    const isSelectable = viaServer && !!selectable[c.id];
    if (isSelectable) card.classList.add('selectable');
    if (c.media) {
      const frame = el('div', 'media-frame');
      if (c.kindPill) frame.appendChild(el('span', 'kind-pill', c.kindPill));
      if (isSelectable) {
        const sel = el('button', 'select-toggle', 'Select');
        sel.setAttribute('data-id', c.id);
        sel.setAttribute('data-filename', c.media.src.split('/').pop());
        sel.addEventListener('click', (e) => {
          e.stopPropagation();
          chooseVariant(c.id, c.media.src.split('/').pop(), sel);
        });
        frame.appendChild(sel);
      }
      frame.appendChild(mediaNode(c.media));
      card.appendChild(frame);
    }
    const body = el('div', 'body');
    if (c.tag) body.appendChild(el('div', 'tag', c.tag));
    if (c.title) body.appendChild(el('div', 'title', c.title));
    if (c.sub) body.appendChild(el('div', 'sub', c.sub));
    if (c.chips && c.chips.length) {
      const meta = el('div', 'meta');
      for (const ch of c.chips) meta.appendChild(el('span', 'chip', ch));
      body.appendChild(meta);
    }
    if (c.refs && c.refs.length) {
      const refs = el('div', 'refs');
      refs.appendChild(el('div', 'refs-label', 'Elements used'));
      for (const r of c.refs) {
        const ref = el('div', 'ref');
        ref.appendChild(el('span', 'dot ' + (r.kind || 'vid')));
        ref.appendChild(el('span', 'ref-name', r.name));
        if (r.role) ref.appendChild(el('span', 'ref-role', r.role));
        refs.appendChild(ref);
      }
      body.appendChild(refs);
    }
    if (c.prompt) {
      body.appendChild(el('div', 'prompt-label', 'Prompt'));
      const pre = el('pre');
      pre.textContent = c.prompt;
      body.appendChild(pre);
    }
    card.appendChild(body);
    return card;
  }

  function buildTable(s) {
    const wrap = el('div', 'table-wrap');
    const table = el('table', 'showcase');
    const thead = el('thead');
    const hr = el('tr');
    const cols = s.columns || ['Stage', 'Prompt / Input', 'Generated Result'];
    const colCls = ['col-stage', 'col-prompt', 'col-result'];
    cols.forEach((c, i) => {
      const th = el('th', colCls[i] || '', c);
      hr.appendChild(th);
    });
    thead.appendChild(hr);
    table.appendChild(thead);
    const tbody = el('tbody');
    for (const row of (s.rows || [])) {
      const tr = el('tr');
      const tdStage = el('td');
      const stageClass = row.stageClass || ((row.stage || '').toLowerCase() === 'before' ? 'before' : 'after');
      const stagePill = el('span', 'stage ' + stageClass, row.stage || '');
      tdStage.appendChild(stagePill);
      if (row.stageTitle) tdStage.appendChild(el('div', 'stage-title', row.stageTitle));
      if (row.stageSub) tdStage.appendChild(el('div', 'stage-sub', row.stageSub));
      tr.appendChild(tdStage);
      const tdPrompt = el('td');
      const pre = el('pre');
      pre.textContent = row.prompt || '';
      tdPrompt.appendChild(pre);
      tr.appendChild(tdPrompt);
      const tdResult = el('td');
      if (row.media) {
        const m = mediaNode(row.media);
        if (row.media.type === 'video') m.className = 'result-video';
        tdResult.appendChild(m);
      }
      if (row.meta) tdResult.appendChild(el('div', 'result-meta', row.meta));
      tr.appendChild(tdResult);
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);
    wrap.appendChild(table);
    return wrap;
  }

  function buildPanel(s) {
    const panel = el('div', 'panel');
    if (s.media) panel.appendChild(mediaNode(s.media));
    if (s.caption) panel.appendChild(el('div', 'caption', s.caption));
    return panel;
  }

  function mediaNode(m) {
    if (m.type === 'image') {
      const img = document.createElement('img');
      img.src = m.src;
      img.alt = m.alt || '';
      return img;
    }
    if (m.type === 'audio') {
      const audio = document.createElement('audio');
      audio.controls = true;
      audio.preload = 'metadata';
      audio.src = m.src;
      return audio;
    }
    const video = document.createElement('video');
    video.controls = true;
    video.preload = 'metadata';
    video.src = m.src;
    return video;
  }

  // ---- selection helpers (manual save via Ctrl+S / Cmd+S) ----
  function chooseVariant(id, filename, btn) {
    if (selections[id] === filename) {
      delete selections[id];
      btn.classList.remove('selected');
      btn.textContent = 'Select';
    } else {
      selections[id] = filename;
      // clear other selected buttons that share the same asset id
      document.querySelectorAll('.select-toggle.selected').forEach((b) => {
        if (b.getAttribute('data-id') === id && b !== btn) {
          b.classList.remove('selected');
          b.textContent = 'Select';
        }
      });
      btn.classList.add('selected');
      btn.textContent = '✓ Selected';
    }
    updateSelStatus();
  }

  function updateSelStatus() {
    if (!selStatus) return;
    const n = Object.keys(selections).length;
    selStatus.textContent = n
      ? n + ' of ' + selIds.length + ' assets selected — press Ctrl+S (⌘S) to save.'
      : 'Pick variants, then press Ctrl+S (⌘S) to save.';
  }

  async function saveSelections() {
    if (!viaServer) return; // read-only in file:// mode
    const n = Object.keys(selections).length;
    if (!n) { selStatus.textContent = 'Select at least one variant first.'; return; }
    selStatus.textContent = 'Saving…';
    try {
      const res = await fetch('/api/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selections }),
      });
      const r = await res.json();
      if (r.ok) {
        selStatus.textContent = 'Saved ' + r.applied.length + ' selection(s)' + (r.errors.length ? ' — ' + r.errors.length + ' error(s)' : '') + '.';
        refreshActivity();
      } else {
        selStatus.textContent = 'Save failed: ' + (r.error || 'unknown error');
      }
    } catch (e) {
      selStatus.textContent = 'Save failed (is the server running?): ' + e.message;
    }
  }

  // Ctrl+S / Cmd+S to save
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S')) {
      e.preventDefault();
      if (selSave) saveSelections();
    }
  });

  if (selIds.length && viaServer) {
    fetch('/api/selection')
      .then((r) => r.json())
      .then((existing) => {
        for (const k in existing) selections[k] = existing[k];
        refreshSelectButtons();
        updateSelStatus();
      })
      .catch(() => {});
  }

  function refreshSelectButtons() {
    document.querySelectorAll('.select-toggle').forEach((b) => {
      const id = b.getAttribute('data-id');
      const fn = b.getAttribute('data-filename');
      if (selections[id] === fn) {
        b.classList.add('selected');
        b.textContent = '✓ Selected';
      } else {
        b.classList.remove('selected');
        b.textContent = 'Select';
      }
    });
  }

  // ---- activity log (server mode only) ----
  if (viaServer) {
    const logPanel = el('section', 'log-panel');
    logPanel.id = 'activity-log';
    const logHead = el('div', 'section-head');
    logHead.appendChild(el('h2', null, 'Activity log'));
    logHead.appendChild(el('span', 'count', 'history'));
    logPanel.appendChild(logHead);
    const logList = el('ul', 'log-list');
    logPanel.appendChild(logList);
    document.getElementById('app').appendChild(logPanel);

    function renderLog(entries) {
      logList.textContent = '';
      if (!entries.length) {
        const empty = el('li', 'log-empty', 'No activity yet — selections will appear here.');
        logList.appendChild(empty);
        return;
      }
      for (const e of entries.slice().reverse()) {
        const li = el('li', 'log-entry');
        const ts = el('span', 'log-ts', e.ts);
        const ev = el('span', 'log-event', e.event);
        ev.setAttribute('data-e', e.event || '');
        let detail = '';
        if (e.event === 'select') {
          detail = (e.manifest || '') + '  →  ' + (e.filename || '');
        } else if (e.event === 'save') {
          detail = 'applied ' + (e.applied || []).length + ' of ' + (e.total || 0) + (e.errors && e.errors.length ? ' (' + e.errors.length + ' error)' : '');
        }
        li.appendChild(ts);
        li.appendChild(ev);
        if (detail) li.appendChild(el('span', 'log-detail', detail));
        logList.appendChild(li);
      }
    }

    function refreshActivity() {
      fetch('/api/log')
        .then((r) => r.json())
        .then(renderLog)
        .catch(() => {});
    }
    refreshActivity();
  }
})();
