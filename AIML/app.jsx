/* Seera — main app & conversation engine */
const { useState, useEffect, useRef, useMemo } = React;

// Conversation engine — simulates AIML kernel
const FLOW = {
  greeting: {
    blocks: [
      { type: "mascot" },
      { type: "text", content: 'Mau aku bantu cari warna pakaian yang paling cocok untukmu? Kita bisa mulai dengan profiling singkat — tidak perlu foto, hanya 2 pertanyaan. ✨' },
      { type: "qr", options: [
        { label: "Mulai Profiling", primary: true, next: "ask_skin_tone" },
        { label: "Belajar Dulu", next: "edu_seasonal" },
        { label: "Apa itu Seera?", next: "about" }
      ]}
    ]
  },
  about: {
    user: "Apa itu Seera?",
    blocks: [
      { type: "text", content: 'Aku menganalisis warna kulit & undertone-mu lewat percakapan, lalu merekomendasikan warna pakaian yang paling “glow” pakai logika <em>fuzzy Mamdani</em> + teori <em>personal color</em>.\n\nTidak ada foto yang disimpan — semua via percakapan saja 🤝' },
      { type: "qr", options: [
        { label: "Mulai Profiling", primary: true, next: "ask_skin_tone" },
        { label: "Belajar Dulu", next: "edu_seasonal" }
      ]}
    ]
  },
  edu_seasonal: {
    user: "Belajar dulu",
    blocks: [
      { type: "text", content: 'Personal color analysis mencocokkan warna pakaian dengan karakter kulit dan undertone-mu. Ada empat “musim” utama:' },
      { type: "palette", season: "spring" },
      { type: "palette", season: "summer" },
      { type: "palette", season: "autumn" },
      { type: "palette", season: "winter" },
      { type: "qr", options: [
        { label: "Mulai Profiling", primary: true, next: "ask_skin_tone" },
        { label: "Apa itu Undertone?", next: "edu_undertone" }
      ]}
    ]
  },
  edu_undertone: {
    user: "Apa itu undertone?",
    blocks: [
      { type: "text", content: '<em>Undertone</em> itu warna di bawah permukaan kulit — tidak berubah walau kulit terbakar matahari. Ada tiga: Cool (kebiruan), Warm (kekuningan), Neutral (campuran).' },
      { type: "qr", options: [
        { label: "Mulai Profiling", primary: true, next: "ask_skin_tone" }
      ]}
    ]
  },
  ask_skin_tone: {
    user: "Mulai profiling",
    setTopic: "PROFILING_SKIN_TONE",
    blocks: [
      { type: "text", content: 'Yuk kita mulai 🌟. Pertama — mana yang paling mirip warna kulitmu?' },
      { type: "fitz" }
    ]
  },
  ask_undertone: {
    setTopic: "PROFILING_UNDERTONE",
    blocks: [
      { type: "text", content: 'Bagus. Sekarang lihat urat di pergelangan tanganmu di bawah cahaya alami — warnanya cenderung apa?' },
      { type: "vein" }
    ]
  },
  reveal_loading: {
    blocks: [
      { type: "text", content: 'Sebentar, aku hitung musim warnamu… ⏳' },
      { type: "typing" }
    ]
  },
  rec_reveal: {
    user: "Lihat rekomendasi",
    blocks: [
      { type: "text", content: 'Ini pilihan terbaikku berdasarkan musimmu, lengkap dengan skor kecocokan ✨' },
      { type: "products" },
      { type: "qr", options: [
        { label: "Lihat Skor Detail", next: "score_detail" },
        { label: "Filter Harga", next: "filter" },
        { label: "Beri Feedback", next: "feedback" },
        { label: "Reset", next: "reset" }
      ]}
    ]
  },
  score_detail: {
    user: "Lihat skor detail",
    blocks: [
      { type: "text", content: 'Berikut breakdown kecocokan warnanya. Skor akhir dihitung dengan <em>Rank Order Centroid</em> — warna paling dominan dapat bobot terbesar.' },
      { type: "chart" },
      { type: "qr", options: [
        { label: "Kembali ke Rekomendasi", next: "rec_reveal" },
        { label: "Beri Feedback", next: "feedback" }
      ]}
    ]
  },
  filter: {
    user: "Filter harga",
    blocks: [
      { type: "text", content: 'Kisaran harga yang kamu mau?' },
      { type: "qr", options: [
        { label: "< Rp 200k", next: "rec_reveal" },
        { label: "Rp 200k–500k", next: "rec_reveal" },
        { label: "> Rp 500k", next: "rec_reveal" },
        { label: "Bebas", next: "rec_reveal" }
      ]}
    ]
  },
  feedback: {
    user: "Beri feedback",
    blocks: [
      { type: "feedback" }
    ]
  },
  feedback_thanks: {
    blocks: [
      { type: "text", content: 'Yay, makasih ya 💖. Mau coba kategori lain atau reset sesi?' },
      { type: "qr", options: [
        { label: "Lihat Lebih Banyak", next: "rec_reveal" },
        { label: "Reset Sesi", next: "reset" }
      ]}
    ]
  },
  reset: {
    user: "Reset",
    blocks: [
      { type: "text", content: 'Beres, sesi di-reset ✨' },
      { type: "mascot" },
      { type: "qr", options: [
        { label: "Mulai Profiling", primary: true, next: "ask_skin_tone" },
        { label: "Belajar Dulu", next: "edu_seasonal" }
      ]}
    ]
  }
};

// Layer 1 inference — skin_tone × undertone → seasonal_type
function inferSeason(skinTone, undertone) {
  const RULES = [
    [1, "cool", "summer"], [1, "neutral", "summer"], [1, "warm", "spring"],
    [2, "cool", "summer"], [2, "neutral", "summer"], [2, "warm", "spring"],
    [3, "cool", "summer"], [3, "neutral", "autumn"], [3, "warm", "spring"],
    [4, "cool", "winter"], [4, "neutral", "autumn"], [4, "warm", "autumn"],
    [5, "cool", "winter"], [5, "neutral", "autumn"], [5, "warm", "autumn"],
    [6, "cool", "winter"], [6, "neutral", "winter"], [6, "warm", "autumn"]
  ];
  const match = RULES.find(r => r[0] === skinTone && r[1] === undertone);
  return match ? match[2] : "summer";
}

const SeasonReveal = ({ season }) => {
  const s = window.SEERA_DATA.SEASONS[season];
  return {
    blocks: [
      { type: "text", content: `Hasilnya: kamu <em>${s.name}</em> ${s.emoji} — palette-mu ${s.desc}.` },
      { type: "palette", season },
      { type: "qr", options: [
        { label: "Lihat Rekomendasi", primary: true, next: "rec_reveal" },
        { label: `Pelajari ${s.name}`, next: "edu_seasonal" },
        { label: "Reset", next: "reset" }
      ]}
    ]
  };
};

// AIML traces shown in the side panel — purely cosmetic
const AIML_TRACES = {
  greeting: `<category>
  <pattern>HALO</pattern>
  <template>
    <random>
      <li>Halo! Aku Seera ✨</li>
      <li>Hai! Senang ketemu kamu.</li>
    </random>
    <visual id="mascot_wave"/>
    <quick-reply options="..."/>
    <think><set name="last_intent">GREETING</set></think>
  </template>
</category>`,
  ask_skin_tone: `<category>
  <pattern>MULAI PROFILING</pattern>
  <template>
    <fitzpatrick-scale highlight="0"/>
    <think>
      <set name="topic">PROFILING_SKIN_TONE</set>
    </think>
  </template>
</category>`,
  ask_undertone: `<category>
  <pattern>ASK UNDERTONE</pattern>
  <template>
    <visual id="vein_test_chart"/>
    <quick-reply options="Cool|Warm|Neutral"/>
    <think><set name="topic">PROFILING_UNDERTONE</set></think>
  </template>
</category>`,
  rec_reveal: `<category>
  <pattern>LIHAT REKOMENDASI</pattern>
  <template>
    <product-card ids="auto" limit="6" score="show"/>
    <think><set name="last_intent">RECOMMENDATION_REVEAL</set></think>
  </template>
</category>`,
  score_detail: `<category>
  <pattern>LIHAT SKOR DETAIL</pattern>
  <template>
    <chart type="score-breakdown" data="last_recommendation"/>
  </template>
</category>`
};

function highlightAiml(s) {
  return s
    .replace(/(&)/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/(&lt;\/?)([a-zA-Z\-]+)/g, '$1<span class="tk-tag">$2</span>')
    .replace(/([a-zA-Z\-]+)=(&quot;|")([^"&]*)(&quot;|")/g, '<span class="tk-attr">$1</span>=<span class="tk-str">"$3"</span>')
    .replace(/="([^"]*)"/g, '=<span class="tk-str">"$1"</span>');
}

// ---------- App ----------
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "showSidePanels": true,
  "showAimlTrace": true,
  "accent": "clay"
}/*EDITMODE-END*/;

const ACCENTS = {
  clay:    { "--clay": "#C97B5C", "--clay-deep": "#A85E40" },
  forest:  { "--clay": "#5C8A6E", "--clay-deep": "#3F6B50" },
  cobalt:  { "--clay": "#4A6FB8", "--clay-deep": "#2F4F94" },
  plum:    { "--clay": "#8E5C8A", "--clay-deep": "#6E3F6B" }
};

function App() {
  const [tweaks, setTweak] = window.useTweaks ? window.useTweaks(TWEAK_DEFAULTS) : [TWEAK_DEFAULTS, () => {}];
  const [items, setItems] = useState([]); // chat items: {role, type, ...}
  const [predicates, setPredicates] = useState({
    user_name: null,
    skin_tone: null,
    undertone: null,
    seasonal_type: null,
    last_intent: null,
    current_topic: "GREETING"
  });
  const [currentNode, setCurrentNode] = useState("greeting");
  const [composing, setComposing] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesRef = useRef(null);

  // Apply accent
  useEffect(() => {
    const accent = ACCENTS[tweaks.accent] || ACCENTS.clay;
    Object.entries(accent).forEach(([k,v]) => document.documentElement.style.setProperty(k, v));
  }, [tweaks.accent]);

  useEffect(() => {
    // initial greeting
    runNode("greeting", { skipUser: true });
  }, []);

  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [items, isTyping]);

  function pushBot(blocks, nodeId) {
    setItems(prev => [...prev, { role: "bot", blocks, nodeId, ts: Date.now() }]);
  }
  function pushUser(text) {
    setItems(prev => [...prev, { role: "user", text, ts: Date.now() }]);
  }

  async function runNode(nodeId, opts = {}) {
    let node = FLOW[nodeId];
    let blocks;

    if (nodeId === "season_reveal") {
      // dynamic
      const season = predicates.seasonal_type;
      blocks = SeasonReveal({ season }).blocks;
    } else if (!node) {
      return;
    } else {
      if (node.user && !opts.skipUser) {
        pushUser(node.user);
      }
      blocks = node.blocks;
      if (node.setTopic) {
        setPredicates(p => ({ ...p, current_topic: node.setTopic, last_intent: nodeId.toUpperCase() }));
      } else {
        setPredicates(p => ({ ...p, last_intent: nodeId.toUpperCase() }));
      }
    }

    setCurrentNode(nodeId);
    setIsTyping(true);
    await new Promise(r => setTimeout(r, opts.skipUser ? 250 : 600));
    setIsTyping(false);
    pushBot(blocks, nodeId);
  }

  function handleQR(opt) {
    pushUser(opt.label);
    setTimeout(() => runNode(opt.next, { skipUser: true }), 100);
  }

  function handleFitzPick(f) {
    pushUser(`${f.name} (${f.sub})`);
    setPredicates(p => ({ ...p, skin_tone: f.num }));
    setTimeout(() => runNode("ask_undertone", { skipUser: true }), 200);
  }

  function handleVeinPick(o) {
    pushUser(o.label);
    const newPred = { ...predicates, undertone: o.id };
    const season = inferSeason(predicates.skin_tone, o.id);
    newPred.seasonal_type = season;
    setPredicates(newPred);
    setTimeout(async () => {
      pushBot([{ type: "text", content: `Catat: undertone <em>${o.id}</em>. Sebentar, aku hitung musim warnamu… ⏳` }], "calc");
      setIsTyping(true);
      await new Promise(r => setTimeout(r, 1100));
      setIsTyping(false);
      const s = window.SEERA_DATA.SEASONS[season];
      pushBot([
        { type: "text", content: `Hasilnya: kamu <em>${s.name}</em> ${s.emoji} — palette-mu ${s.desc}.` },
        { type: "palette", season },
        { type: "qr", options: [
          { label: "Lihat Rekomendasi", primary: true, next: "rec_reveal" },
          { label: `Pelajari ${s.name}`, next: "edu_seasonal" },
          { label: "Reset", next: "reset" }
        ]}
      ], "season_reveal");
      setCurrentNode("season_reveal");
    }, 250);
  }

  function handleFeedback(kind) {
    pushUser(kind === "up" ? "👍 Membantu" : "👎 Kurang membantu");
    setTimeout(() => runNode("feedback_thanks", { skipUser: true }), 200);
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!composing.trim()) return;
    const txt = composing.trim();
    pushUser(txt);
    setComposing("");
    // Simple keyword fallback
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      const lower = txt.toLowerCase();
      let next = null;
      if (/halo|hai|hi|hello/.test(lower)) next = "greeting";
      else if (/profil|mulai/.test(lower)) next = "ask_skin_tone";
      else if (/rekomen/.test(lower)) next = "rec_reveal";
      else if (/skor|detail/.test(lower)) next = "score_detail";
      else if (/reset|ulang/.test(lower)) next = "reset";
      else if (/belajar|edukasi/.test(lower)) next = "edu_seasonal";
      else if (/undertone/.test(lower)) next = "edu_undertone";

      if (next) runNode(next, { skipUser: true });
      else pushBot([
        { type: "text", content: 'Hmm, aku belum paham 🤔. Aku spesialis warna pakaian — coba salah satu ini?' },
        { type: "qr", options: [
          { label: "Mulai Profiling", primary: true, next: "ask_skin_tone" },
          { label: "Lihat Rekomendasi", next: "rec_reveal" },
          { label: "Bantuan", next: "about" }
        ]}
      ], "fallback");
    }, 700);
  }

  // -------- render block --------
  function renderBlock(b, key, msg) {
    switch (b.type) {
      case "text":
        return <div key={key} className="bubble" dangerouslySetInnerHTML={{__html: b.content.replace(/\n/g, "<br/>")}}/>;
      case "mascot": return <MascotBlock key={key}/>;
      case "palette": return <PaletteBlock key={key} season={b.season}/>;
      case "fitz": return <FitzpatrickBlock key={key} onSelect={handleFitzPick} selected={predicates.skin_tone}/>;
      case "vein": return <VeinTestBlock key={key} onSelect={handleVeinPick} selected={predicates.undertone}/>;
      case "products": return <ProductCardBlock key={key} season={predicates.seasonal_type || "summer"}/>;
      case "chart": return <ChartBlock key={key} season={predicates.seasonal_type || "summer"}/>;
      case "feedback": return <FeedbackBlock key={key} onPick={handleFeedback}/>;
      case "qr": return <QuickReplies key={key} options={b.options} onPick={handleQR}/>;
      case "typing": return null;
      default: return null;
    }
  }

  const seasonal = predicates.seasonal_type;
  const seasonObj = seasonal ? window.SEERA_DATA.SEASONS[seasonal] : null;

  return (
    <div className="app">
      {/* LEFT RAIL */}
      {tweaks.showSidePanels && (
      <aside className="rail">
        <div className="brand">
          <div className="brand-mark"></div>
          <div>
            <div className="brand-name">Seera</div>
            <div className="brand-sub">Color Stylist · v2.0</div>
          </div>
        </div>

        <div className="rail-section">
          <div className="rail-label">Sesi</div>
          <div className="rail-item active"><span className="dot"></span>Profiling Saat Ini</div>
          <div className="rail-item"><span className="dot"></span>Riwayat Rekomendasi</div>
          <div className="rail-item"><span className="dot"></span>Palette Tersimpan</div>
        </div>

        <div className="rail-section">
          <div className="rail-label">Edukasi</div>
          <div className="rail-item" onClick={() => runNode("edu_seasonal", {skipUser:true})}><span className="dot"></span>Seasonal Theory</div>
          <div className="rail-item" onClick={() => runNode("edu_undertone", {skipUser:true})}><span className="dot"></span>Undertone</div>
          <div className="rail-item"><span className="dot"></span>Fitzpatrick I–VI</div>
        </div>

        <div className="rail-foot">
          <div style={{fontFamily:"var(--font-mono)", fontSize:10, letterSpacing:"0.06em"}}>SESSION_ID</div>
          <div style={{fontFamily:"var(--font-mono)", fontSize:10.5, color:"var(--ink-2)"}}>5f9c·a31b·7e2d·…</div>
          <div style={{marginTop:14, fontSize:11, color:"var(--ink-3)"}}>Anonim by default · tidak ada PII tersimpan.</div>
        </div>
      </aside>
      )}

      {/* CENTER — CHAT */}
      <main className="chat">
        <div className="chat-head">
          <div className="chat-head-left">
            <div className="avatar"></div>
            <div>
              <div className="chat-head-name">Seera</div>
              <div className="chat-head-status">● Online · personal color stylist</div>
            </div>
          </div>
          <div className="chat-head-actions">
            <button className="icon-btn" title="Info" onClick={() => runNode("about", {skipUser:true})}><Icon name="info"/></button>
            <button className="icon-btn" title="Reset sesi" onClick={() => runNode("reset", {skipUser:true})}><Icon name="refresh"/></button>
          </div>
        </div>

        <div className="messages" ref={messagesRef}>
          <div className="messages-inner">
            <div className="day-divider">Hari ini · {new Date().toLocaleDateString("id-ID", {day:"numeric", month:"long"})}</div>
            {items.map((m, i) => {
              if (m.role === "user") {
                return (
                  <div className="msg-row user" key={i}>
                    <div className="msg-stack">
                      <div className="bubble">{m.text}</div>
                    </div>
                  </div>
                );
              }
              return (
                <div className="msg-row" key={i}>
                  <div className="msg-avatar"></div>
                  <div className="msg-stack">
                    {m.blocks.map((b, j) => renderBlock(b, j, m))}
                  </div>
                </div>
              );
            })}
            {isTyping && (
              <div className="msg-row">
                <div className="msg-avatar"></div>
                <div className="msg-stack"><Typing/></div>
              </div>
            )}
          </div>
        </div>

        <div className="composer-wrap">
          <form className="composer" onSubmit={handleSubmit}>
            <textarea
              rows="1"
              placeholder="Ketik pesan untuk Seera…"
              value={composing}
              onChange={e => setComposing(e.target.value)}
              onKeyDown={e => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
            <button className="composer-send" disabled={!composing.trim()} aria-label="Kirim">
              <Icon name="send" size={18}/>
            </button>
          </form>
          <div className="composer-foot">
            <span>↩ Enter untuk kirim · ⇧ Shift+Enter baris baru</span>
            <span>AIML 2.0 · FIS Mamdani 2-layer · ROC</span>
          </div>
        </div>
      </main>

      {/* RIGHT — STYLIST NOTES */}
      {tweaks.showSidePanels && (
      <aside className="panel">
        <div className="panel-section">
          <div className="panel-label">Stylist Notes</div>
          <div className={"season-card" + (seasonObj ? "" : " empty")}
               style={{"--season-gradient": seasonObj ? seasonObj.gradient : "transparent"}}>
            <div className="season-card-inner">
              <div className="season-name" style={{color: seasonObj ? "var(--ink)" : "var(--ink-3)"}}>
                {seasonObj ? `${seasonObj.name} ${seasonObj.emoji}` : "—"}
              </div>
              <div className="season-tag">{seasonObj ? seasonObj.tagline : "Belum di-profile"}</div>
              {seasonObj && (
                <div style={{display:"flex", gap:4, marginTop:12}}>
                  {seasonObj.colors.map((c,i) => (
                    <div key={i} style={{width:24, height:24, borderRadius:6, background:c, border:"1px solid rgba(0,0,0,0.08)"}}/>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="panel-section">
          <div className="panel-label">Predicates</div>
          <div className="panel-card">
            <div className="panel-row">
              <span className="panel-key">skin_tone</span>
              <span className={"panel-val" + (predicates.skin_tone ? "" : " empty")}>
                {predicates.skin_tone ? `${predicates.skin_tone} · ${window.SEERA_DATA.FITZPATRICK[predicates.skin_tone-1].name}` : "—"}
              </span>
            </div>
            <div className="panel-row">
              <span className="panel-key">undertone</span>
              <span className={"panel-val" + (predicates.undertone ? "" : " empty")}>
                {predicates.undertone || "—"}
              </span>
            </div>
            <div className="panel-row">
              <span className="panel-key">seasonal_type</span>
              <span className={"panel-val" + (predicates.seasonal_type ? "" : " empty")}>
                {predicates.seasonal_type || "—"}
              </span>
            </div>
            <div className="panel-row">
              <span className="panel-key">current_topic</span>
              <span className="panel-val" style={{fontFamily:"var(--font-mono)", fontSize:11}}>{predicates.current_topic}</span>
            </div>
            <div className="panel-row">
              <span className="panel-key">last_intent</span>
              <span className="panel-val" style={{fontFamily:"var(--font-mono)", fontSize:11}}>{predicates.last_intent || "—"}</span>
            </div>
          </div>
        </div>

        {tweaks.showAimlTrace && AIML_TRACES[currentNode] && (
        <div className="panel-section">
          <div className="panel-label">AIML Trace</div>
          <div className="aiml-trace" dangerouslySetInnerHTML={{__html: highlightAiml(AIML_TRACES[currentNode])}}/>
          <div style={{fontSize:10.5, color:"var(--ink-3)", fontFamily:"var(--font-mono)", marginTop:6}}>
            Pattern matched · {currentNode}
          </div>
        </div>
        )}

        <div className="panel-section">
          <div className="panel-label">Pipeline</div>
          <div className="panel-card" style={{padding:0}}>
            {[
              { id: 1, label: "Profiling", done: !!predicates.skin_tone && !!predicates.undertone },
              { id: 2, label: "FIS Layer 1 → Y1", done: !!predicates.seasonal_type },
              { id: 3, label: "FIS Layer 2 → Y2", done: items.some(m => m.nodeId === "rec_reveal") },
              { id: 4, label: "ROC Aggregate", done: items.some(m => m.nodeId === "rec_reveal") },
              { id: 5, label: "Ranking & Reveal", done: items.some(m => m.nodeId === "rec_reveal") }
            ].map(p => (
              <div key={p.id} style={{display:"flex", alignItems:"center", gap:10, padding:"10px 12px", borderTop: p.id > 1 ? "1px dashed var(--line)" : "none"}}>
                <div style={{
                  width:18, height:18, borderRadius:"50%",
                  background: p.done ? "var(--clay)" : "var(--line-2)",
                  color: "white", display:"grid", placeItems:"center",
                  fontSize:10, fontWeight:600, fontFamily:"var(--font-mono)"
                }}>{p.done ? "✓" : p.id}</div>
                <span style={{fontSize:12, color: p.done ? "var(--ink)" : "var(--ink-3)"}}>{p.label}</span>
              </div>
            ))}
          </div>
        </div>
      </aside>
      )}

      {/* TWEAKS PANEL */}
      {window.TweaksPanel && (
        <window.TweaksPanel title="Tweaks">
          <window.TweakSection title="Layout">
            <window.TweakToggle label="Show side panels" value={tweaks.showSidePanels} onChange={v => setTweak('showSidePanels', v)}/>
            <window.TweakToggle label="Show AIML trace" value={tweaks.showAimlTrace} onChange={v => setTweak('showAimlTrace', v)}/>
          </window.TweakSection>
          <window.TweakSection title="Accent">
            <window.TweakRadio
              value={tweaks.accent}
              onChange={v => setTweak('accent', v)}
              options={[
                {value: "clay", label: "Clay"},
                {value: "forest", label: "Forest"},
                {value: "cobalt", label: "Cobalt"},
                {value: "plum", label: "Plum"}
              ]}
            />
          </window.TweakSection>
          <window.TweakSection title="Demo Shortcuts">
            <window.TweakButton label="→ Profiling" onClick={() => runNode("ask_skin_tone", {skipUser:true})}/>
            <window.TweakButton label="→ Recommendations (Summer)" onClick={() => {
              setPredicates(p => ({...p, skin_tone: 3, undertone: "cool", seasonal_type: "summer"}));
              setTimeout(() => runNode("rec_reveal", {skipUser:true}), 50);
            }}/>
            <window.TweakButton label="→ Score Breakdown" onClick={() => {
              setPredicates(p => ({...p, skin_tone: 3, undertone: "cool", seasonal_type: "summer"}));
              setTimeout(() => runNode("score_detail", {skipUser:true}), 50);
            }}/>
            <window.TweakButton label="↻ Reset" onClick={() => runNode("reset", {skipUser:true})}/>
          </window.TweakSection>
        </window.TweaksPanel>
      )}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
