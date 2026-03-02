import streamlit as st
import requests
import json
import urllib.parse

# ── Page Config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tamil ↔ English Translator",
    page_icon="🌐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@400;600;700&family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 820px; }

/* ── HERO ── */
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1a1a3e 50%, #0f2027 100%);
    border-radius: 22px;
    padding: 32px;
    text-align: center;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,.07);
}
.hero::before {
    content: '';
    position: absolute;
    top: -80px; left: 50%;
    transform: translateX(-50%);
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(139,92,246,.18), transparent 65%);
    pointer-events: none;
}
.hero-badge {
    display: inline-flex; align-items: center; gap: 7px;
    background: rgba(139,92,246,.2);
    border: 1px solid rgba(139,92,246,.35);
    color: #c4b5fd;
    font-size: .72rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase;
    padding: 5px 14px; border-radius: 100px; margin-bottom: 14px;
}
.hero-badge .dot { width: 6px; height: 6px; border-radius: 50%; background: #a78bfa; animation: blink 1.6s infinite; }
@keyframes blink { 0%,100%{opacity:.3} 50%{opacity:1} }
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem; font-weight: 800; letter-spacing: -.03em;
    color: #fff; margin: 0 0 8px;
}
.hero h1 .ta { color: #a78bfa; }
.hero h1 .en { color: #34d399; }
.hero-sub { color: rgba(255,255,255,.5); font-size: .9rem; margin: 0; }

/* ── LANG BAR ── */
.lang-bar {
    display: flex; align-items: center; justify-content: center;
    gap: 16px; margin-bottom: 20px; flex-wrap: wrap;
}
.lang-pill {
    display: flex; align-items: center; gap: 8px;
    padding: 10px 22px; border-radius: 100px;
    font-weight: 700; font-size: .9rem; cursor: pointer;
    transition: all .25s; border: 2px solid transparent;
    font-family: 'DM Sans', sans-serif;
}
.lang-pill.active-ta {
    background: rgba(167,139,250,.15);
    border-color: #a78bfa; color: #a78bfa;
}
.lang-pill.active-en {
    background: rgba(52,211,153,.15);
    border-color: #34d399; color: #059669;
}
.lang-pill.inactive {
    background: #f8fafc; border-color: #e2e8f0; color: #64748b;
}
.swap-btn {
    width: 40px; height: 40px; border-radius: 50%;
    background: #fff; border: 2px solid #e2e8f0;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; font-size: 18px;
    transition: transform .3s, border-color .2s;
    box-shadow: 0 2px 8px rgba(0,0,0,.06);
}
.swap-btn:hover { transform: rotate(180deg); border-color: #a78bfa; }

/* ── TRANSLATOR CARD ── */
.trans-card {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,.07);
    margin-bottom: 18px;
}
.trans-half {
    padding: 0;
}
.trans-label {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 18px;
    border-bottom: 1px solid #f1f5f9;
    background: #fafafa;
}
.trans-lang-name {
    font-size: .78rem; font-weight: 700; letter-spacing: .07em;
    text-transform: uppercase;
}
.label-ta { color: #7c3aed; }
.label-en { color: #059669; }
.char-count { font-size: .72rem; color: #94a3b8; }

/* ── VOICE IN TRANSLATOR ── */
.voice-row {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 16px;
    border-bottom: 1px solid #f1f5f9;
    background: #fefefe;
}
.mic-btn {
    width: 36px; height: 36px; border-radius: 50%;
    background: linear-gradient(135deg, #7c3aed, #6d28d9);
    border: none; cursor: pointer; font-size: 15px;
    display: flex; align-items: center; justify-content: center;
    transition: transform .2s, box-shadow .2s;
    box-shadow: 0 3px 10px rgba(124,58,237,.3);
    flex-shrink: 0;
}
.mic-btn:hover { transform: scale(1.1); }
.mic-btn.on {
    background: linear-gradient(135deg, #ef4444, #dc2626);
    box-shadow: 0 3px 10px rgba(239,68,68,.4);
    animation: micPulse 1s infinite;
}
@keyframes micPulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(239,68,68,.4); }
    50%      { box-shadow: 0 0 0 10px rgba(239,68,68,0); }
}
.voice-hint { font-size: .78rem; color: #94a3b8; }
.voice-hint.active { color: #ef4444; font-weight: 600; }

/* wave bars */
.waves { display: flex; align-items: center; gap: 2px; }
.w { width: 3px; border-radius: 2px; background: #ef4444; animation: wb .7s ease-in-out infinite; }
.w:nth-child(1){height:6px;  animation-delay:0s}
.w:nth-child(2){height:14px; animation-delay:.1s}
.w:nth-child(3){height:9px;  animation-delay:.2s}
.w:nth-child(4){height:18px; animation-delay:.3s}
.w:nth-child(5){height:11px; animation-delay:.15s}
@keyframes wb { 0%,100%{transform:scaleY(.3)} 50%{transform:scaleY(1)} }

/* ── OUTPUT BOX ── */
.output-box {
    padding: 18px;
    min-height: 130px;
    font-size: 1.05rem;
    line-height: 1.75;
    color: #0f172a;
    font-family: 'Noto Sans Tamil', 'DM Sans', sans-serif;
    background: #fff;
    white-space: pre-wrap;
    word-break: break-word;
}
.output-box.empty { color: #94a3b8; font-style: italic; font-size: .9rem; }
.output-box.loading {
    display: flex; align-items: center; gap: 10px;
    color: #7c3aed; font-style: normal;
}

/* ── COPY ROW ── */
.copy-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 16px;
    border-top: 1px solid #f1f5f9;
    background: #fafafa;
}
.copy-btn {
    display: flex; align-items: center; gap: 6px;
    background: #fff; border: 1.5px solid #e2e8f0;
    color: #475569; font-size: .78rem; font-weight: 600;
    padding: 6px 14px; border-radius: 8px; cursor: pointer;
    transition: all .2s; font-family: 'DM Sans', sans-serif;
}
.copy-btn:hover { border-color: #7c3aed; color: #7c3aed; background: rgba(124,58,237,.05); }
.engine-tag {
    font-size: .68rem; color: #94a3b8;
    display: flex; align-items: center; gap: 4px;
}
.engine-dot { width: 5px; height: 5px; border-radius: 50%; background: #10b981; }

/* ── QUICK PHRASES ── */
.phrases-wrap {
    background: #fff; border: 1px solid #e2e8f0;
    border-radius: 16px; padding: 20px;
    margin-bottom: 18px;
}
.phrases-title {
    font-size: .75rem; font-weight: 700; letter-spacing: .08em;
    text-transform: uppercase; color: #64748b; margin-bottom: 14px;
    display: flex; align-items: center; gap: 6px;
}
.phrases-title::before { content: ''; width: 18px; height: 2px; background: #a78bfa; border-radius: 2px; }
.phrases-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.phrase-chip {
    background: #f8fafc; border: 1.5px solid #e2e8f0;
    color: #334155; font-size: .82rem; font-weight: 500;
    padding: 6px 14px; border-radius: 100px; cursor: pointer;
    transition: all .2s; font-family: 'DM Sans', sans-serif;
}
.phrase-chip:hover {
    background: rgba(124,58,237,.08);
    border-color: #a78bfa; color: #7c3aed;
}

/* ── HISTORY ── */
.history-wrap {
    background: #fff; border: 1px solid #e2e8f0;
    border-radius: 16px; padding: 20px; margin-bottom: 18px;
}
.hist-item {
    padding: 12px 14px;
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 10px; margin-bottom: 8px; cursor: pointer;
    transition: border-color .2s, background .2s;
}
.hist-item:hover { border-color: #a78bfa; background: rgba(124,58,237,.04); }
.hist-src { font-size: .82rem; color: #64748b; margin-bottom: 3px; }
.hist-tgt {
    font-size: .9rem; font-weight: 600; color: #0f172a;
    font-family: 'Noto Sans Tamil', 'DM Sans', sans-serif;
}

/* ── STREAMLIT OVERRIDES ── */
div.stButton > button {
    border-radius: 10px !important; font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: transform .2s, box-shadow .2s !important;
}
div.stButton > button:hover { transform: translateY(-2px) !important; }
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
    color: #fff !important; border: none !important;
}
div.stTextArea textarea {
    border-radius: 12px !important;
    border: 1.5px solid #e2e8f0 !important;
    font-family: 'Noto Sans Tamil', 'DM Sans', sans-serif !important;
    font-size: 1rem !important; line-height: 1.7 !important;
}
div.stTextArea textarea:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,.1) !important;
}
div.stSelectbox > div { border-radius: 10px !important; }
.stSpinner > div { text-align: center; }
</style>
""", unsafe_allow_html=True)

import streamlit.components.v1 as components

# ── Session State ────────────────────────────────────────────────────
if "direction" not in st.session_state:
    st.session_state.direction = "en_to_ta"  # or ta_to_en
if "history" not in st.session_state:
    st.session_state.history = []
if "last_translation" not in st.session_state:
    st.session_state.last_translation = ""
if "last_engine" not in st.session_state:
    st.session_state.last_engine = ""
if "voice_input" not in st.session_state:
    st.session_state.voice_input = ""

# ── Translation Functions ────────────────────────────────────────────

def translate_groq(text: str, src_lang: str, tgt_lang: str) -> str:
    """Translate using Groq Llama — best quality"""
    try:
        from groq import Groq
        api_key = st.secrets.get("GROQ_API_KEY", "")
        if not api_key:
            return None
        client = Groq(api_key=api_key)
        lang_names = {"ta": "Tamil", "en": "English", "hi": "Hindi"}
        src = lang_names.get(src_lang, src_lang)
        tgt = lang_names.get(tgt_lang, tgt_lang)
        prompt = f"""Translate the following {src} text to {tgt}.
Return ONLY the translated text — no explanations, no quotes, no extra words.

Text: {text}"""
        msg = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        result = msg.choices[0].message.content.strip()
        # Clean quotes if any
        result = result.strip('"\'')
        return result
    except Exception:
        return None


def translate_mymemory(text: str, lang_pair: str) -> str:
    """Translate using MyMemory API — free, no key needed"""
    try:
        encoded = urllib.parse.quote(text)
        url = f"https://api.mymemory.translated.net/get?q={encoded}&langpair={lang_pair}"
        resp = requests.get(url, timeout=8)
        data = resp.json()
        if data.get("responseStatus") == 200:
            return data["responseData"]["translatedText"]
        return None
    except Exception:
        return None


def translate(text: str) -> tuple[str, str]:
    """Smart translate with Groq first, MyMemory fallback"""
    if not text.strip():
        return "", ""

    direction = st.session_state.direction
    if direction == "en_to_ta":
        src_lang, tgt_lang, mm_pair = "en", "ta", "en|ta"
    elif direction == "ta_to_en":
        src_lang, tgt_lang, mm_pair = "ta", "en", "ta|en"
    else:  # en_to_hi
        src_lang, tgt_lang, mm_pair = "en", "hi", "en|hi"

    # Try Groq first
    result = translate_groq(text, src_lang, tgt_lang)
    if result:
        return result, "🤖 Groq AI"

    # Fallback: MyMemory
    result = translate_mymemory(text, mm_pair)
    if result:
        return result, "🌐 MyMemory"

    return "❌ Translation failed. Check internet connection.", "❌ Error"


# ══════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════

# HERO
st.markdown("""
<div class="hero">
  <div class="hero-badge"><span class="dot"></span>AI Powered · Free · Offline Fallback</div>
  <h1><span class="ta">தமிழ்</span> ↔ <span class="en">English</span> Translator</h1>
  <p class="hero-sub">Groq AI quality · Voice input · Instant translation</p>
</div>
""", unsafe_allow_html=True)


# ── DIRECTION SELECTOR ───────────────────────────────────────────────
col1, col2, col3 = st.columns([2, 1, 2])

with col1:
    dir_options = {
        "🇮🇳 Tamil → English": "ta_to_en",
        "🇬🇧 English → Tamil": "en_to_ta",
        "🇬🇧 English → Hindi": "en_to_hi",
    }
    selected_dir = st.selectbox(
        "Translation Direction",
        list(dir_options.keys()),
        index=1,
        label_visibility="collapsed"
    )
    st.session_state.direction = dir_options[selected_dir]

with col2:
    if st.button("🔄 Swap", use_container_width=True):
        if st.session_state.direction == "en_to_ta":
            st.session_state.direction = "ta_to_en"
        elif st.session_state.direction == "ta_to_en":
            st.session_state.direction = "en_to_ta"
        st.rerun()

with col3:
    engine_choice = st.selectbox(
        "Engine",
        ["🤖 Groq AI (Best)", "🌐 MyMemory (No Key)"],
        label_visibility="collapsed"
    )


# ── VOICE INPUT ──────────────────────────────────────────────────────
direction = st.session_state.direction
voice_lang = "ta-IN" if "ta_to_en" in direction else "en-US" if "en_to" in direction else "en-US"

voice_html = f"""
<div style="display:flex;align-items:center;gap:10px;padding:12px 16px;
  background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:12px;margin-bottom:4px">
  <button id="micBtn" onclick="toggleMic()"
    style="width:40px;height:40px;border-radius:50%;
    background:linear-gradient(135deg,#7c3aed,#6d28d9);
    border:none;cursor:pointer;font-size:16px;color:#fff;
    box-shadow:0 3px 12px rgba(124,58,237,.35);
    display:flex;align-items:center;justify-content:center;
    transition:transform .2s;flex-shrink:0">🎤</button>
  <div id="micStatus" style="font-size:.82rem;color:#94a3b8;flex:1">
    Click mic to speak — <b style="color:#7c3aed">{voice_lang.split('-')[0].upper()}</b> language
  </div>
  <div id="waveWrap" style="display:none;align-items:center;gap:2px">
    {''.join(['<div style="width:3px;border-radius:2px;background:#ef4444;animation:wb .7s ease-in-out infinite ' + str(i*0.1) + 's;height:' + str([6,14,9,18,11][i%5]) + 'px"></div>' for i in range(5)])}
  </div>
</div>
<style>
@keyframes wb{{0%,100%{{transform:scaleY(.3)}}50%{{transform:scaleY(1)}}}}
#micBtn:hover{{transform:scale(1.1)}}
</style>
<script>
let recog = null, listening = false, transcript = '';

function toggleMic(){{
  listening ? stopMic() : startMic();
}}

function startMic(){{
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SR){{ alert('Use Chrome for voice input!'); return; }}
  recog = new SR();
  recog.lang = '{voice_lang}';
  recog.continuous = true;
  recog.interimResults = true;
  recog.onstart = ()=>{{
    listening = true;
    document.getElementById('micBtn').style.background = 'linear-gradient(135deg,#ef4444,#dc2626)';
    document.getElementById('micBtn').innerHTML = '⏹';
    document.getElementById('waveWrap').style.display = 'flex';
    document.getElementById('micStatus').innerHTML = '<b style="color:#ef4444">🔴 Listening... speak now</b>';
  }};
  recog.onresult = (e)=>{{
    let fin='', int='';
    for(let i=0;i<e.results.length;i++){{
      if(e.results[i].isFinal) fin += e.results[i][0].transcript+' ';
      else int += e.results[i][0].transcript;
    }}
    transcript = fin || int;
    document.getElementById('micStatus').innerHTML =
      '🗣️ <span style="color:#334155">' + (transcript.length>60?'...'+transcript.slice(-60):transcript) + '</span>';
  }};
  recog.onerror = (e)=>{{
    stopMic();
    document.getElementById('micStatus').innerHTML = '❌ <span style="color:#ef4444">'+e.error+' — Try Chrome</span>';
  }};
  recog.onend = ()=>{{
    if(listening){{
      stopMic();
      if(transcript.trim()){{
        // Pass to Streamlit
        const url = new URL(window.location.href);
        url.searchParams.set('voice_input', encodeURIComponent(transcript.trim()));
        window.location.href = url.toString();
      }}
    }}
  }};
  recog.start();
}}

function stopMic(){{
  listening = false;
  if(recog){{ try{{recog.stop()}}catch(e){{}} }}
  document.getElementById('micBtn').style.background = 'linear-gradient(135deg,#7c3aed,#6d28d9)';
  document.getElementById('micBtn').innerHTML = '🎤';
  document.getElementById('waveWrap').style.display = 'none';
  if(!transcript.trim()){{
    document.getElementById('micStatus').innerHTML = 'Click mic to speak — <b style="color:#7c3aed">{voice_lang.split("-")[0].upper()}</b> language';
  }}
}}
</script>
"""
components.html(voice_html, height=76)

# Get voice input from query params
voice_prefill = ""
try:
    params = st.query_params
    if "voice_input" in params:
        voice_prefill = urllib.parse.unquote(params["voice_input"])
        st.query_params.clear()
except:
    pass


# ── INPUT TEXT AREA ──────────────────────────────────────────────────
src_label = "🇮🇳 Tamil Text" if "ta_to_en" in direction else "🇬🇧 English Text"

input_text = st.text_area(
    src_label,
    value=voice_prefill,
    placeholder="Type or speak your text here...",
    height=140,
    key="input_text"
)

# char count
if input_text:
    st.caption(f"📝 {len(input_text)} characters · {len(input_text.split())} words")


# ── QUICK PHRASES ────────────────────────────────────────────────────
if direction == "en_to_ta":
    phrases = ["Hello, how are you?", "Thank you", "What is your name?",
               "Good morning", "Please help me", "How much does it cost?",
               "Where is the hospital?", "I don't understand"]
elif direction == "ta_to_en":
    phrases = ["வணக்கம்", "நன்றி", "உங்கள் பெயர் என்ன?",
               "காலை வணக்கம்", "எனக்கு உதவுங்கள்", "இது எவ்வளவு?",
               "மருத்துவமனை எங்கே?", "எனக்கு புரியவில்லை"]
else:
    phrases = ["Hello", "Thank you", "Good morning", "How are you?",
               "Please help me", "What is your name?"]

st.markdown('<div class="phrases-wrap"><div class="phrases-title">Quick Phrases</div><div class="phrases-grid">', unsafe_allow_html=True)
phrase_cols = st.columns(4)
for i, phrase in enumerate(phrases):
    with phrase_cols[i % 4]:
        if st.button(phrase, key=f"ph_{i}", use_container_width=True):
            st.session_state["quick_phrase"] = phrase
            st.rerun()
st.markdown('</div></div>', unsafe_allow_html=True)

# Use quick phrase if selected
if "quick_phrase" in st.session_state:
    input_text = st.session_state.pop("quick_phrase")


# ── TRANSLATE BUTTON ─────────────────────────────────────────────────
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    translate_btn = st.button("🌐 Translate", type="primary", use_container_width=True)
with col_t2:
    clear_btn = st.button("🗑 Clear", use_container_width=True)

if clear_btn:
    st.session_state.last_translation = ""
    st.session_state.last_engine = ""
    st.rerun()

# Auto-translate if voice input came in
if voice_prefill and not translate_btn:
    translate_btn = True

if translate_btn and input_text.strip():
    with st.spinner("🤖 Translating..."):
        # Override engine if user chose MyMemory only
        if "MyMemory" in engine_choice:
            direction_map = {
                "en_to_ta": "en|ta", "ta_to_en": "ta|en", "en_to_hi": "en|hi"
            }
            result = translate_mymemory(input_text, direction_map[direction])
            engine = "🌐 MyMemory"
            if not result:
                result = "❌ Translation failed. Check internet."
                engine = "❌ Error"
        else:
            result, engine = translate(input_text)

        st.session_state.last_translation = result
        st.session_state.last_engine = engine

        # Save to history
        if result and "❌" not in result:
            st.session_state.history.insert(0, {
                "src": input_text[:60] + ("..." if len(input_text) > 60 else ""),
                "tgt": result[:80] + ("..." if len(result) > 80 else ""),
                "dir": selected_dir
            })
            st.session_state.history = st.session_state.history[:10]  # keep last 10


# ── OUTPUT ───────────────────────────────────────────────────────────
if st.session_state.last_translation:
    tgt_label = "🇬🇧 English Translation" if "ta_to_en" in direction else "🇮🇳 Tamil Translation" if "en_to_ta" in direction else "🇮🇳 Hindi Translation"

    st.markdown(f"**{tgt_label}**")

    # Result box
    st.markdown(f"""
    <div style="background:#fff;border:1.5px solid #e2e8f0;border-radius:14px;
      padding:20px;margin-bottom:10px;
      font-family:'Noto Sans Tamil','DM Sans',sans-serif;
      font-size:1.08rem;line-height:1.8;color:#0f172a;
      box-shadow:0 2px 12px rgba(0,0,0,.05);">
      {st.session_state.last_translation}
      <div style="margin-top:12px;padding-top:10px;border-top:1px solid #f1f5f9;
        font-size:.72rem;color:#94a3b8;display:flex;align-items:center;gap:6px;">
        <span style="width:6px;height:6px;border-radius:50%;background:#10b981;display:inline-block"></span>
        Translated by {st.session_state.last_engine}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Copy button
    col_c1, col_c2 = st.columns([1, 3])
    with col_c1:
        if st.button("📋 Copy", use_container_width=True):
            st.code(st.session_state.last_translation)
            st.success("✅ Select & copy from above!")
    with col_c2:
        # Text to speech output
        tts_lang = "ta" if "en_to_ta" in direction else "en"
        components.html(f"""
        <button onclick="speak()" style="
          background:#fff;border:1.5px solid #e2e8f0;
          color:#475569;font-size:.82rem;font-weight:600;
          padding:8px 16px;border-radius:8px;cursor:pointer;
          display:flex;align-items:center;gap:6px;
          font-family:'DM Sans',sans-serif;
          transition:all .2s;width:100%;justify-content:center;">
          🔊 Listen (Text to Speech)
        </button>
        <script>
        function speak(){{
          const text = `{st.session_state.last_translation.replace('`', '')}`;
          const u = new SpeechSynthesisUtterance(text);
          u.lang = '{tts_lang}-IN' if tts_lang == 'ta' else 'en-US';
          window.speechSynthesis.speak(u);
        }}
        </script>
        """, height=44)

else:
    st.markdown("""
    <div style="background:#f8fafc;border:1.5px dashed #e2e8f0;border-radius:14px;
      padding:28px;text-align:center;color:#94a3b8;font-size:.9rem;margin-bottom:18px">
      🌐 Translation will appear here
    </div>
    """, unsafe_allow_html=True)


# ── HISTORY ─────────────────────────────────────────────────────────
if st.session_state.history:
    with st.expander(f"📚 Recent Translations ({len(st.session_state.history)})"):
        for item in st.session_state.history:
            st.markdown(f"""
            <div class="hist-item">
              <div class="hist-src">🔤 {item['src']} <span style="font-size:.7rem;color:#94a3b8">({item['dir']})</span></div>
              <div class="hist-tgt">→ {item['tgt']}</div>
            </div>
            """, unsafe_allow_html=True)
        if st.button("🗑 Clear History"):
            st.session_state.history = []
            st.rerun()
