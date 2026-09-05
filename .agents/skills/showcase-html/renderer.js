// renderer.js — reads the #showcase-data JSON and renders the page.
// Inlined into template.html by scripts/generate_showcase.py.

(function () {
  const raw = document.getElementById('showcase-data').textContent;
  const data = JSON.parse(raw);

  const el = (tag, cls, text) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  };

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

  // ---- main ----
  const main = el('main');
  for (const s of data.sections) {
    main.appendChild(buildSection(s));
  }
  document.getElementById('app').appendChild(main);

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
    if (c.media) {
      const frame = el('div', 'media-frame');
      if (c.kindPill) frame.appendChild(el('span', 'kind-pill', c.kindPill));
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
})();
