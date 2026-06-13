/* Seera multimodal block components */
const { useState, useEffect, useRef } = React;

const Icon = ({ name, size = 16 }) => {
  const paths = {
    send: <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>,
    sparkle: <path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round"/>,
    refresh: <path d="M3 12a9 9 0 0 1 15.5-6.3M21 4v5h-5M21 12a9 9 0 0 1-15.5 6.3M3 20v-5h5" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>,
    info: <g stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 8v.01M12 11v5"/></g>,
    settings: <g stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></g>,
    chat: <path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.4 8.4 0 0 1 3.8-.9h.5a8.5 8.5 0 0 1 8 8v.5z" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
  };
  return <svg width={size} height={size} viewBox="0 0 24 24">{paths[name]}</svg>;
};

const TextBubble = ({ children }) => (
  <div className="bubble" dangerouslySetInnerHTML={typeof children === "string" ? { __html: children } : null}>
    {typeof children !== "string" ? children : null}
  </div>
);

const MascotBlock = () => (
  <div className="block" style={{padding: 0, overflow: "hidden"}}>
    <div className="mascot">
      <div className="mascot-orb"></div>
      <div>
        <div className="mascot-text">Halo, aku <em style={{fontStyle:"italic"}}>Seera</em>.</div>
        <div style={{fontSize: 13, color: "var(--ink-2)", marginTop: 4}}>Asisten warna pribadimu — temukan palette pakaian yang membuatmu bersinar.</div>
      </div>
    </div>
  </div>
);

const PaletteBlock = ({ season, mini = false }) => {
  const s = window.SEERA_DATA.SEASONS[season];
  if (!s) return null;
  return (
    <div className="block" style={mini ? {padding: 14} : {}}>
      <div className="block-head">
        <div>
          <div className="block-tag">PALETTE · {s.tagline}</div>
          <div className="block-title">{s.name} {s.emoji}</div>
        </div>
      </div>
      <div className="palette">
        {s.colors.map((c, i) => (
          <div key={i} className="swatch" style={{background: c}} title={c}>
            <span className="swatch-hex">{c}</span>
          </div>
        ))}
      </div>
      <div className="palette-foot">
        <span style={{display:"inline-block", width:8, height:8, borderRadius:"50%", background: s.colors[0]}}></span>
        Palette {s.name.toLowerCase()} cocok untuk kulit dengan karakter {s.desc}.
      </div>
    </div>
  );
};

const FitzpatrickBlock = ({ onSelect, selected }) => (
  <div className="block">
    <div className="block-head">
      <div>
        <div className="block-tag">FITZPATRICK SCALE · I–VI</div>
        <div className="block-title">Mana yang paling mirip kulitmu?</div>
      </div>
    </div>
    <div className="fitz">
      {window.SEERA_DATA.FITZPATRICK.map(f => (
        <div
          key={f.num}
          className={"fitz-cell" + (selected === f.num ? " selected" : "")}
          style={{background: f.hex}}
          onClick={() => onSelect && onSelect(f)}
          role="button"
          aria-label={`${f.name} — ${f.sub}`}
          tabIndex="0"
        >
          <div className="fitz-num">{f.num}</div>
        </div>
      ))}
    </div>
    <div style={{display:"grid", gridTemplateColumns:"repeat(6,1fr)", gap: 6, marginTop: 8}}>
      {window.SEERA_DATA.FITZPATRICK.map(f => (
        <div key={f.num} style={{fontSize:9.5, color:"var(--ink-3)", textAlign:"center", lineHeight:1.2, fontFamily:"var(--font-mono)"}}>
          {f.name.split(" ").map((w,i)=><div key={i}>{w}</div>)}
        </div>
      ))}
    </div>
  </div>
);

const VeinTestBlock = ({ onSelect, selected }) => {
  const opts = [
    { id: "cool", label: "Biru / Ungu", cap: "Cool 💙", veinColor: "#6B7DB8" },
    { id: "warm", label: "Hijau", cap: "Warm 🔥", veinColor: "#7B9268" },
    { id: "neutral", label: "Campuran", cap: "Neutral 🌿", veinColor: "#8B7D8E" }
  ];
  return (
    <div className="block">
      <div className="block-head">
        <div>
          <div className="block-tag">VEIN TEST · UNDERTONE</div>
          <div className="block-title">Lihat urat di pergelangan tanganmu.</div>
        </div>
      </div>
      <div className="vein-viz">
        {opts.map(o => (
          <div
            key={o.id}
            className={"vein-card" + (selected === o.id ? " selected" : "")}
            onClick={() => onSelect && onSelect(o)}
            role="button"
            tabIndex="0"
          >
            <svg className="vein-svg" viewBox="0 0 80 50" preserveAspectRatio="none">
              <path d="M10 5 Q 25 25, 20 45" stroke={o.veinColor} strokeWidth="2.5" fill="none" strokeLinecap="round" opacity="0.7"/>
              <path d="M40 5 Q 50 25, 45 45" stroke={o.veinColor} strokeWidth="2.5" fill="none" strokeLinecap="round" opacity="0.7"/>
              <path d="M65 5 Q 70 25, 68 45" stroke={o.veinColor} strokeWidth="2.5" fill="none" strokeLinecap="round" opacity="0.7"/>
            </svg>
            <div className="vein-label">{o.label}</div>
            <div className="vein-cap">{o.cap}</div>
          </div>
        ))}
      </div>
      <div style={{fontSize:11.5, color:"var(--ink-3)", marginTop: 4, textAlign:"center"}}>
        Lihat di bawah cahaya alami untuk hasil terbaik.
      </div>
    </div>
  );
};

const ProductCardBlock = ({ season }) => {
  const items = window.SEERA_DATA.PRODUCTS[season] || [];
  return (
    <div className="block">
      <div className="block-head">
        <div>
          <div className="block-tag">REKOMENDASI · {items.length} produk</div>
          <div className="block-title">Untukmu, {window.SEERA_DATA.SEASONS[season].name}</div>
        </div>
        <div style={{fontSize:10, fontFamily:"var(--font-mono)", color:"var(--ink-3)"}}>ROC × Y2</div>
      </div>
      <div className="products">
        {items.map(p => (
          <div className="product" key={p.id}>
            <div className="product-thumb">
              <div className="product-thumb-bg" style={{background: p.bg}}></div>
              <div className="product-score"><em>{p.score}</em>/100</div>
            </div>
            <div className="product-info">
              <div className="product-title">{p.title}</div>
              <div className="product-price">{p.price}</div>
              <div className="product-swatches">
                {p.swatches.map((s,i) => <div key={i} style={{background:s}}/>)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const ChartBlock = ({ season }) => {
  const items = window.SEERA_DATA.PRODUCTS[season] || [];
  const top = items[0];
  if (!top) return null;
  // Simulated breakdown: 3 colors with Y2 scores derived from top.score
  const breakdown = [
    { label: "Y2 · Warna 1", value: top.score, weight: 0.611 },
    { label: "Y2 · Warna 2", value: Math.max(40, top.score - 14), weight: 0.278 },
    { label: "Y2 · Warna 3", value: Math.max(30, top.score - 28), weight: 0.111 }
  ];
  const finalScore = breakdown.reduce((sum, b) => sum + b.value * b.weight, 0).toFixed(1);
  return (
    <div className="block">
      <div className="block-head">
        <div>
          <div className="block-tag">SCORE BREAKDOWN · {top.id}</div>
          <div className="block-title">{top.title}</div>
        </div>
        <div style={{fontFamily:"var(--font-display)", fontSize:22, fontWeight:500}}>{finalScore}</div>
      </div>
      <div className="chart-rows">
        {breakdown.map((b, i) => (
          <div className="chart-row" key={i}>
            <div className="chart-label">{b.label} <span style={{color:"var(--ink-3)", fontWeight:400}}>· w={b.weight}</span></div>
            <div className="chart-bar"><div className="chart-bar-fill" style={{width: `${b.value}%`}}></div></div>
            <div className="chart-val">{b.value}</div>
          </div>
        ))}
      </div>
      <div className="chart-formula">Skor = Σ wᵢ · Y2ᵢ  =  {breakdown.map(b => `${b.weight}·${b.value}`).join("  +  ")}  =  {finalScore}</div>
    </div>
  );
};

const QuickReplies = ({ options, onPick }) => (
  <div className="quick-replies">
    {options.map((o, i) => (
      <button
        key={i}
        className={"qr" + (o.primary ? " primary" : "")}
        onClick={() => onPick(o)}
      >
        {o.icon && <span>{o.icon}</span>}
        {o.label || o}
      </button>
    ))}
  </div>
);

const FeedbackBlock = ({ onPick }) => (
  <div className="block" style={{display:"flex", alignItems:"center", justifyContent:"space-between", gap:14}}>
    <div>
      <div className="block-tag">FEEDBACK</div>
      <div style={{fontFamily:"var(--font-display)", fontSize:16, fontWeight:500, marginTop:2}}>Apakah rekomendasi ini membantu?</div>
    </div>
    <div className="feedback">
      <button className="fb-btn up" onClick={() => onPick("up")} aria-label="Membantu">👍</button>
      <button className="fb-btn down" onClick={() => onPick("down")} aria-label="Kurang membantu">👎</button>
    </div>
  </div>
);

const Typing = () => (
  <div className="typing"><span/><span/><span/></div>
);

Object.assign(window, {
  Icon, TextBubble, MascotBlock, PaletteBlock, FitzpatrickBlock,
  VeinTestBlock, ProductCardBlock, ChartBlock, QuickReplies,
  FeedbackBlock, Typing
});
