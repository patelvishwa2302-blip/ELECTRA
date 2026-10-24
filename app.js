// ============================================================
// ELECTRA DASHBOARD — app.js
// Frontend Lead: Vishwa Patel
// ============================================================

// ── CONFIG ──────────────────────────────────────────────────
// Change this to Bhavya's IP when integrating
const BACKEND_URL = 'http://localhost:8000';

// ── STATE ───────────────────────────────────────────────────
let scannedMedicines = [];
let ayurvedicMedicines = [];
let currentMode = 'doctor'; // 'doctor' | 'patient' | 'hindi'
let lastResponse = null; // store last API response for toggles
let allMedicineNames = []; // loaded from /medicines endpoint

// ── HINDI TRANSLATIONS (pre-written) ────────────────────────
const HINDI_EXPLANATIONS = {
  'BLEED-001': 'आपकी दो दवाइयाँ खून पतला करती हैं। साथ लेने से पेट में खून बहने का खतरा बढ़ जाता है। कृपया डॉक्टर से पूछें।',
  'BLEED-002': 'आप दो तरह की खून पतला करने वाली दवाइयाँ ले रहे हैं। यह जरूरी हो सकता है, लेकिन डॉक्टर से सलाह लेते रहें।',
  'KID-001': 'आपकी तीन दवाइयाँ मिलकर आपके गुर्दों (kidney) को नुकसान पहुँचा सकती हैं। यह बहुत जरूरी है कि डॉक्टर इसे जाँचें।',
  'KID-002': 'आपकी दर्द की दवा आपकी किडनी पर बोझ डालती है। किडनी की बीमारी में यह दवा नुकसान पहुँचा सकती है। कृपया डॉक्टर से पूछें कि इसकी जगह पैरासिटामोल लिया जा सकता है या नहीं।',
  'SED-001': 'आपकी कुछ दवाइयाँ नींद और चक्कर ला सकती हैं। साथ लेने पर गिरने का खतरा है। गाड़ी न चलाएँ।',
  'RESP-001': 'यह दवाइयों का संयोजन खतरनाक है — नींद में साँस रुकने का खतरा है। तुरंत डॉक्टर को बताएँ।',
  'QT-001': 'दो दवाइयाँ मिलकर दिल की धड़कन को अनियमित कर सकती हैं। ECG कराएँ।',
  'HYPO-001': 'आपकी एंटीबायोटिक दवा शुगर को बहुत कम कर सकती है। शुगर बार-बार जाँचें। कमज़ोरी या पसीना आए तो तुरंत कुछ मीठा खाएँ।',
  'SER-001': 'दो दवाइयाँ दिमाग में सेरोटोनिन बढ़ा सकती हैं। बुखार, बेचैनी, या मांसपेशियों में ऐंठन हो तो तुरंत अस्पताल जाएँ।',
  'DUP-001': 'आपके पास एक ही दवा दो अलग नामों से है! एक तुरंत बंद करें। यह दोगुना डोज़ है।',
  'DUP-002': 'आप एक ही तरह की दो दवाइयाँ ले रहे हैं। डॉक्टर से पूछें कि दोनों जरूरी हैं या नहीं।',
  'AYUR-001': 'आपकी आयुर्वेदिक दवा और खून पतला करने वाली दवा साथ में लेने से खून बहने का खतरा है। डॉक्टर को बताएँ।',
  'AYUR-002': 'आपकी आयुर्वेदिक दवा शुगर को और कम कर सकती है। शुगर बार-बार जाँचें।',
  'FOOD-001': 'अंगूर का रस (grapefruit juice) आपकी दवा को 5 गुना तेज़ कर देता है। इससे साइड इफेक्ट हो सकते हैं। यह जूस बंद करें।',
  'FOOD-002': 'दूध, दही, और पनीर आपकी एंटीबायोटिक का असर 50% कम कर देते हैं। दवा और डेयरी के बीच 2 घंटे का अंतर रखें।',
  'AYUR-DYNAMIC': 'आपकी आयुर्वेदिक दवा का असर आपकी अन्य दवा पर पड़ सकता है। डॉक्टर को बताएँ।',
  'CTRL-001': 'यह एक नियंत्रित दवा है। इसे हमेशा डॉक्टर की सलाह से ही लें। किसी को न दें।',
   // ── Phase 2 rules: pregnancy, breastfeeding, GI-bleed, heart failure ──
  'PREG-001': 'आप गर्भवती हैं, और यह पेनकिलर प्रेगनेंसी में सुरक्षित नहीं है। यह आपके बच्चे की किडनी और ब्लड फ्लो को नुकसान पहुंचा सकता है। इसे न लें। कृपया दर्द या बुखार के लिए किसी सुरक्षित विकल्प के बारे में आज ही अपने डॉक्टर से बात करें।',
  'PREG-002': 'आप गर्भवती हैं, और यह ब्लड-प्रेशर की दवा आपके बच्चे की किडनी को नुकसान पहुंचा सकती है। कृपया तुरंत अपने डॉक्टर से संपर्क करें। अपनी मर्जी से कोई भी दवा न रोकें या बदलें।',
  'PREG-003': 'आप गर्भवती हैं, और यह ब्लड थिनर आपके बच्चे के विकास को नुकसान पहुंचा सकता है। इसे आपके डॉक्टर द्वारा तुरंत चेक किया जाना चाहिए। कृपया आज ही उनसे संपर्क करें, और इसे अपनी मर्जी से न रोकें।',
  'PREG-004': 'आप गर्भवती हैं, और प्रेगनेंसी के दौरान आमतौर पर कोलेस्ट्रॉल की दवाएं बंद कर दी जाती हैं। कृपया अपनी अगली डोज़ से पहले अपने डॉक्टर से बात करें।',
  'PREG-005': 'आप गर्भवती हैं, और यह एंटीबायोटिक आपके बच्चे के दांतों और हड्डियों पर असर डाल सकता है। कृपया अपने डॉक्टर से कोई दूसरी एंटीबायोटिक मांगें।',
  'LACT-001': 'आप स्तनपान करा रही हैं, और यह पेनकिलर आपके दूध में जा सकता है जिससे आपका बच्चा बहुत ज्यादा नींद में जा सकता है या उसे सांस लेने में तकलीफ हो सकती है। कृपया इसे न लें। किसी सुरक्षित विकल्प के लिए अपने डॉक्टर से पूछें।',
  'GI-001': 'आपको पहले पेट का अल्सर या पेट में ब्लीडिंग हो चुकी है, और यह पेनकिलर इसे दोबारा पैदा कर सकता है। कृपया इसे न लें। किसी सुरक्षित विकल्प के लिए अपने डॉक्टर से पूछें।',
  'GI-002': 'आप इस पेनकिलर के साथ स्टेरॉयड की दवा ले रही हैं। दोनों मिलकर पेट में ब्लीडिंग या अल्सर पैदा कर सकते हैं। कृपया अपने पेट को सुरक्षित रखने के बारे में अपने डॉक्टर से बात करें।',
  'HF-001': 'आपको हार्ट फेलियर है, और यह पेनकिलर आपके शरीर में फ्लूइड जमा कर सकता है जिससे आपकी दिल की स्थिति और खराब हो सकती है। कृपया इसे लेने से पहले अपने डॉक्टर से बात करें।',
  'DM-001': 'स्टेरॉयड से ब्लड शुगर बढ़ता है। चूंकि आप डायबिटीज की दवा भी लेते हैं, इसलिए आपका शुगर कंट्रोल अनिश्चित हो सकता है। कृपया स्टेरॉयड लेते समय अपना ब्लड शुगर ज्यादा बार चेक करें।',
};

// ── TIMING RULES (per therapeutic class) ────────────────────
const TIMING_RULES = {
  'thyroid_hormone': { time: '6:00 AM', note: 'Empty stomach — 30 min before anything' },
  'antidiabetic': { time: '8:00 AM', note: 'With breakfast' },
  'antiplatelet': { time: '8:00 AM', note: 'With breakfast (food protects stomach)' },
  'nsaid': { time: '1:00 PM', note: 'With food only — never empty stomach' },
  'analgesic': { time: 'As needed', note: 'With food. Max 3x daily.' },
  'calcium_channel_blocker':{ time: '6:00 PM', note: 'Evening — avoid grapefruit juice' },
  'ace_inhibitor': { time: '8:00 AM', note: 'Any time, consistent daily' },
  'arb': { time: '8:00 AM', note: 'Any time, consistent daily' },
  'beta_blocker': { time: '8:00 AM', note: 'With food' },
  'anticoagulant': { time: '6:00 PM', note: 'Same time each day — INR monitoring' },
  'supplement': { time: '9:00 PM', note: 'After dinner — separate from antibiotics by 2 hrs' },
  'diuretic': { time: '8:00 AM', note: 'Morning — avoids night-time urination' },
  'ssri': { time: '8:00 AM', note: 'With food to reduce nausea' },
  'benzodiazepine': { time: '10:00 PM', note: 'Night only — do not drive after' },
  'antibiotic': { time: '8:00 AM & 8:00 PM', note: 'Complete full course. Separate from dairy.' },
  'fluoroquinolone': { time: '8:00 AM & 8:00 PM', note: '2 hrs away from dairy/calcium' },
};

// ── ON LOAD ──────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', async () => {
  await loadMedicineList();
  setupAutocomplete();
  document.getElementById('med-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') addMedicine();
  });
});

async function loadMedicineList() {
  try {
    const res = await fetch(`${BACKEND_URL}/medicines`);
    const data = await res.json();
    allMedicineNames = Object.values(data).map(m => m.brand);
  } catch (e) {
    // Backend not connected yet — use demo list
    allMedicineNames = ['Ecosprin 75','Brufen 400','Glycomet 500','Stamlo 5','Crocin 500','Shelcal 500'];
  }
}

// ── AUTOCOMPLETE ─────────────────────────────────────────────
function setupAutocomplete() {
  const input = document.getElementById('med-input');
  const list = document.getElementById('autocomplete-list');

  input.addEventListener('input', () => {
    const val = input.value.toLowerCase().trim();
    list.innerHTML = '';
    if (!val || val.length < 2) return;

    const matches = allMedicineNames.filter(n => n.toLowerCase().includes(val)).slice(0, 6);
    if (!matches.length) return;

    const dropdown = document.createElement('div');
    dropdown.style.cssText = `
      position:absolute; z-index:100; width:100%;
      background:var(--bg-card); border:1px solid var(--border);
      border-radius:6px; margin-top:2px; overflow:hidden;
    `;

    matches.forEach(name => {
      const item = document.createElement('div');
      item.textContent = name;
      item.style.cssText = `padding:8px 12px; font-size:0.82rem; cursor:pointer;`;
      item.addEventListener('mouseover', () => item.style.background = 'var(--bg-input)');
      item.addEventListener('mouseout', () => item.style.background = 'transparent');
      item.addEventListener('click', () => {
        input.value = name;
        list.innerHTML = '';
        addMedicine();
      });
      dropdown.appendChild(item);
    });

    list.appendChild(dropdown);
  });

  document.addEventListener('click', e => {
    if (e.target !== input) list.innerHTML = '';
  });
}

// ── ADD / REMOVE MEDICINE ────────────────────────────────────
function addMedicine() {
  const input = document.getElementById('med-input');
  const name = input.value.trim();
  if (!name || scannedMedicines.includes(name)) { input.value = ''; return; }

  scannedMedicines.push(name);
  input.value = '';
  document.getElementById('autocomplete-list').innerHTML = '';
  renderMedTags();
}

function removeMedicine(name) {
  scannedMedicines = scannedMedicines.filter(m => m !== name);
  renderMedTags();
}

function renderMedTags() {
  const container = document.getElementById('med-tags-container');
  if (!scannedMedicines.length) {
    container.innerHTML = '<span style="font-size:0.78rem; color:var(--text-muted);">No medicines added yet</span>';
    return;
  }
  container.innerHTML = scannedMedicines.map(m =>
    `<span class="med-tag" id="tag-${m.replace(/\s/g,'_')}">
      💊 ${m}
      <span class="remove" onclick="removeMedicine('${m}')" title="Remove">✕</span>
    </span>`
  ).join('');
}

// ── ADD AYURVEDIC ────────────────────────────────────────────
function addAyurvedic() {
  const input = document.getElementById('ayurvedic-input');
  const val = input.value.trim();
  if (!val || ayurvedicMedicines.includes(val)) return;
  ayurvedicMedicines.push(val);
  renderAyurvedicTags();
  input.value = '';
}

function removeAyurvedic(name) {
  ayurvedicMedicines = ayurvedicMedicines.filter(m => m !== name);
  renderAyurvedicTags();
}

function renderAyurvedicTags() {
  const container = document.getElementById('ayurvedic-tags');
  container.innerHTML = ayurvedicMedicines.map(m =>
    `<span class="med-tag" style="border-color:var(--risk-low)">
      🌿 ${m}
      <span class="remove" onclick="removeAyurvedic('${m}')">✕</span>
    </span>`
  ).join('');
}

// ── LOAD DEMO (Ramesh scenario) ──────────────────────────────
function loadDemo() {
  // Clear existing
  scannedMedicines = ['Ecosprin 75', 'Brufen 400', 'Glycomet 500'];
  ayurvedicMedicines = ['Ashwagandha'];

  // Set foods
  document.querySelectorAll('.food-check').forEach(cb => {
    cb.checked = cb.value === 'grapefruit_juice';
  });

  // Set patient profile
  document.getElementById('patient-age').value = 72;
  document.getElementById('p-diabetes').checked = true;
  document.getElementById('p-hypertension').checked = true;
  document.getElementById('p-ckd').checked = true;
  document.getElementById('p-liver').checked = false;
  document.getElementById('p-kidney-fn').value = 'mild';
  document.getElementById('p-caregiver').value = '+918849065660';

  renderMedTags();
  renderAyurvedicTags();
}

// ── BUILD REQUEST BODY ───────────────────────────────────────
function buildRequestBody() {
  const foods = [...document.querySelectorAll('.food-check:checked')].map(cb => cb.value);
  return {
    device_id: 'web-dashboard',
    scanned_medicines: scannedMedicines,
    ayurvedic_medicines: ayurvedicMedicines,
    foods: foods,
    patient: {
      age: parseInt(document.getElementById('patient-age').value) || 50,
      diabetes: document.getElementById('p-diabetes').checked,
      hypertension: document.getElementById('p-hypertension').checked,
      ckd: document.getElementById('p-ckd').checked,
      liver_disease: document.getElementById('p-liver').checked,
      kidney_function: document.getElementById('p-kidney-fn').value,
      caregiver_phone: document.getElementById('p-caregiver').value || null,
      sex: (document.querySelector('input[name="p-sex"]:checked') || {}).value || 'male',
      pregnant: document.getElementById('p-pregnant').checked,
      breastfeeding: document.getElementById('p-breastfeeding').checked,
      gi_bleed_history: document.getElementById('p-gi').checked,
      heart_failure: document.getElementById('p-hf').checked,
      alcohol: document.getElementById('p-alcohol').checked,
      copd: document.getElementById('p-copd').checked,
      sleep_apnoea: document.getElementById('p-apnoea').checked,
      dehydration: document.getElementById('p-dehydration').checked,
      bradycardia: document.getElementById('p-bradycardia').checked,
      hypokalemia: document.getElementById('p-hypokalemia').checked,
      hypomagnesemia: document.getElementById('p-hypomagnesemia').checked,

    }
  };
}

// ── MAIN ANALYZE ─────────────────────────────────────────────
async function analyzeClick() {
  if (!scannedMedicines.length) {
    alert('Please add at least one medicine first.');
    return;
  }

  const btn = document.getElementById('analyze-btn');
  btn.textContent = '⏳ Analyzing...';
  btn.classList.add('loading');
  btn.disabled = true;

  try {
    const response = await fetch(`${BACKEND_URL}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(buildRequestBody())
    });

    if (!response.ok) throw new Error(`Server error: ${response.status}`);
    const data = await response.json();
    lastResponse = data;

    renderResults(data);
    loadTags();

  } catch (err) {
    alert(`❌ Could not connect to backend.\n\nMake sure Bhavya's server is running:\nuvicorn main:app --reload --port 8000\n\nError: ${err.message}`);
  } finally {
    btn.textContent = '🔍 ANALYZE';
    btn.classList.remove('loading');
    btn.disabled = false;
  }
}

// ── RENDER ALL RESULTS ───────────────────────────────────────
function renderResults(data) {
  document.getElementById('empty-state').style.display = 'none';
  document.getElementById('results-container').style.display = 'block';

  renderRiskBadge(data.overall_risk);
  renderBurdenScore(data.burden_score);
  renderAlertCards(data.alerts, data.overall_risk);
  renderTimeline(data);
  renderTimingSchedule();
  renderAuditTrail(data);

  // WhatsApp banner
  const waEl = document.getElementById('whatsapp-banner');
  waEl.classList.toggle('show', !!data.whatsapp_sent);

  // Unknown medicines
  const uwEl = document.getElementById('unknown-warning');
  if (data.unrecognized_medicines && data.unrecognized_medicines.length) {
    uwEl.textContent = `⚠ Unrecognized: ${data.unrecognized_medicines.join(', ')} — not in database`;
    uwEl.classList.add('show');
  } else { uwEl.classList.remove('show'); }

  // Highlight risky medicine tags in left panel
  scannedMedicines.forEach(med => {
    const tagEl = document.getElementById(`tag-${med.replace(/\s/g,'_')}`);
    if (!tagEl) return;
    const isRisky = data.alerts.some(a => a.medicines_involved.includes(med));
    tagEl.classList.toggle('risky', isRisky);
  });
}

// ── RISK BADGE ───────────────────────────────────────────────
const RISK_META = {
  low: { label: '✅ LOW', desc: 'No significant interactions detected' },
  moderate: { label: '⚠ MODERATE', desc: 'Some caution needed — consult doctor' },
  high: { label: '🔴 HIGH', desc: 'Significant risk — review immediately' },
  critical: { label: '⛔ CRITICAL', desc: 'DANGEROUS — Do not take without doctor review' },
};

function renderRiskBadge(risk) {
  const badge = document.getElementById('risk-badge');
  const label = document.getElementById('risk-label');
  const desc = document.getElementById('risk-desc');
  badge.className = `risk-badge ${risk}`;
  label.textContent = RISK_META[risk]?.label || risk.toUpperCase();
  desc.textContent = RISK_META[risk]?.desc || '';
}

// ── BURDEN SCORE BARS ─────────────────────────────────────────
function renderBurdenScore(burden) {
  if (!burden) return;
  const container = document.getElementById('burden-section');
  const organs = [
    { key: 'kidney', label: '🫘 Kidney' },
    { key: 'liver',  label: '🟤 Liver' },
    { key: 'cardiac', label: '💓 Cardiac' },
    { key: 'bleeding',label: '🩸 Bleeding' },
    { key: 'cns',    label: '🧠 CNS/Brain' },
  ];

  container.innerHTML = organs.map(o => {
    const val = burden[o.key] || 0;
    const pct = (val / 10) * 100;
    const color = val >= 8 ? 'var(--risk-high)' : val >= 5 ? 'var(--risk-mod)' : 'var(--risk-low)';
    return `
      <div class="burden-row">
        <div class="burden-label">${o.label}</div>
        <div class="burden-bar-bg">
          <div class="burden-bar-fill"
               style="width:${pct}%; background:${color};"
               data-target="${pct}"></div>
        </div>
        <div class="burden-val" style="color:${color}">${val}/10</div>
      </div>`;
  }).join('');

  // Animate bars after render
  setTimeout(() => {
    document.querySelectorAll('.burden-bar-fill').forEach(bar => {
      bar.style.width = bar.dataset.target + '%';
    });
  }, 50);

  // Overall score
  const overall = burden.overall || 0;
  const overallColor = overall >= 7 ? 'var(--risk-high)' : overall >= 5 ? 'var(--risk-mod)' : 'var(--risk-low)';
  container.innerHTML += `
    <div style="text-align:right; font-size:0.78rem; margin-top:8px;">
      Overall Burden: <strong style="color:${overallColor}">${overall}/10</strong>
      ${overall >= 7 ? ' — <span style="color:var(--risk-high)">Consider deprescribing review</span>' : ''}
    </div>`;
}

// ── ALERT CARDS ──────────────────────────────────────────────
function renderAlertCards(alerts, overallRisk) {
  const container = document.getElementById('alert-cards-container');
  if (!alerts || !alerts.length) {
    container.innerHTML = `<div class="risk-card low">
      <div class="risk-card-title">✅ No interactions detected</div>
      <div class="risk-explanation" style="margin-top:6px;">
        All scanned medicines appear to be safe together for this patient profile.
      </div>
    </div>`;
    return;
  }

  container.innerHTML = alerts.map((alert, i) => `
    <div class="risk-card ${alert.severity}" id="card-${i}">
      <div class="risk-card-header">
        <div class="risk-card-title">${alert.name}</div>
        <span class="severity-chip ${alert.severity}">${alert.severity.toUpperCase()}</span>
        ${alert.refer_to_doctor ? '<span class="severity-chip" style="background:#d97706;color:#ffffff; margin-left:6px;">CONSULT DOCTOR</span>' : ''}
      </div>

      <div class="risk-meds-involved">
        ${alert.medicines_involved.map(m => `<span class="med-pill">${m}</span>`).join('')}
      </div>

      <!-- Doctor explanation (shown by default) -->
      <div class="risk-explanation doctor-text" id="exp-doctor-${i}">
        ${alert.doctor_explanation}
      </div>

      <!-- Patient explanation (hidden by default) -->
      <div class="risk-explanation patient-text" id="exp-patient-${i}" style="display:none;">
        ${alert.patient_explanation}
      </div>

      <!-- Hindi explanation -->
      <div class="hindi-text" id="exp-hindi-${i}">
        ${HINDI_EXPLANATIONS[alert.rule_id] || alert.patient_explanation}
      </div>

      <span class="evidence-badge">📚 ${alert.evidence}</span>

      <div class="risk-action">
        💡 ${alert.action}
      </div>

      <div style="font-size:0.75rem; color:var(--text-muted); margin-bottom:8px;">
        👁 Monitor: ${alert.monitoring}
      </div>

      <!-- Deprescribing Simulator Button -->
      <button class="deprescribe-btn"
              onclick="simulateRemove('${alert.medicines_involved[0]}', ${i})">
        🔬 What if I remove ${alert.medicines_involved[0]}?
      </button>
      <div class="deprescribe-result" id="deprescribe-result-${i}"></div>
    </div>
  `).join('');
}

// ── DEPRESCRIBING SIMULATOR ──────────────────────────────────
async function simulateRemove(medicineName, cardIndex) {
  const resultEl = document.getElementById(`deprescribe-result-${cardIndex}`);
  resultEl.textContent = '⏳ Simulating...';
  resultEl.classList.add('show');

  try {
    const body = buildRequestBody();
    body.remove_medicine = medicineName;

    const res = await fetch(`${BACKEND_URL}/simulate-remove`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await res.json();

    const dr = data.deprescribe_result;
    const improved = data.new_risk !== data.original_risk;

    resultEl.innerHTML = `
      <strong>Remove ${medicineName}:</strong><br>
      Risk: <strong>${data.original_risk.toUpperCase()}</strong>
      → <strong style="color:var(--risk-low)">${data.new_risk.toUpperCase()}</strong>
      ${improved ? ' ✅ Improved!' : ''}<br>
      ${dr.suggested_alternative ? `<span style="color:var(--risk-low)">Alternative: ${dr.suggested_alternative}</span>` : ''}
    `;
  } catch (e) {
    resultEl.textContent = '❌ Could not reach backend.';
  }
}

// ── VIEW MODE TOGGLE (Doctor / Patient / Hindi) ──────────────
function setMode(mode) {
  currentMode = mode;

  document.getElementById('toggle-doctor').classList.toggle('active', mode === 'doctor');
  document.getElementById('toggle-patient').classList.toggle('active', mode === 'patient');
  document.getElementById('toggle-hindi').classList.toggle('active', mode === 'hindi');

  document.querySelectorAll('.doctor-text').forEach(el => {
    el.style.display = mode === 'doctor' ? 'block' : 'none';
  });
  document.querySelectorAll('.patient-text').forEach(el => {
    el.style.display = mode === 'patient' ? 'block' : 'none';
  });
  document.querySelectorAll('.hindi-text').forEach(el => {
    el.classList.toggle('show', mode === 'hindi');
  });
}

// ── TIMELINE ─────────────────────────────────────────────────
function renderTimeline(data) {
  const container = document.getElementById('timeline-container');
  const riskyMeds = new Set(data.alerts.flatMap(a => a.medicines_involved));

  const rows = scannedMedicines.map(med => {
    const isRisky = riskyMeds.has(med);
    const cls = isRisky ? 'risky' : 'new';
    const icon = isRisky ? '🔴' : '🆕';
    const tag = isRisky ? 'Risk flagged' : 'Newly added';
    return `<div class="timeline-row ${cls}">
      <span class="timeline-icon">${icon}</span>
      <span class="timeline-name">${med}</span>
      <span class="timeline-tag">${tag}</span>
    </div>`;
  });

  ayurvedicMedicines.forEach(med => {
    const isRisky = riskyMeds.has(med);
    rows.push(`<div class="timeline-row ${isRisky ? 'risky' : 'new'}">
      <span class="timeline-icon">${isRisky ? '⚠️' : '🌿'}</span>
      <span class="timeline-name">${med}</span>
      <span class="timeline-tag">Ayurvedic${isRisky ? ' — INTERACTION' : ''}</span>
    </div>`);
  });

  container.innerHTML = rows.join('') || '<div style="color:var(--text-muted); font-size:0.82rem;">No medicines scanned.</div>';
}

// ── DOSE TIMING SCHEDULE ─────────────────────────────────────
function renderTimingSchedule() {
  const container = document.getElementById('timing-schedule');
  // For demo: use medicine class lookup (in real version, call backend)
  // Here we just show the demo schedule
  const schedule = [
    { time: '6:00 AM (Empty stomach)', meds: 'Levothyroxine (if prescribed)' },
    { time: '8:00 AM (With breakfast)', meds: scannedMedicines.filter(m =>
      m.toLowerCase().includes('glycomet') || m.toLowerCase().includes('ecosprin')
    ).join(', ') || 'Antidiabetics, Antiplatelets' },
    { time: '1:00 PM (With food only)', meds: scannedMedicines.filter(m =>
      m.toLowerCase().includes('brufen') || m.toLowerCase().includes('ibuprofen')
    ).join(', ') || 'NSAIDs (if prescribed)' },
    { time: '6:00 PM (Evening)', meds: scannedMedicines.filter(m =>
      m.toLowerCase().includes('stamlo') || m.toLowerCase().includes('amlodipine')
    ).join(', ') || 'Calcium channel blockers' },
    { time: '10:00 PM (After dinner)', meds: scannedMedicines.filter(m =>
      m.toLowerCase().includes('shelcal') || m.toLowerCase().includes('calcium')
    ).join(', ') || 'Calcium supplements' },
  ].filter(row => row.meds && !row.meds.includes('('));

  container.innerHTML = schedule.length
    ? schedule.map(row => `
      <div class="timing-row">
        <div class="timing-time">⏰ ${row.time}</div>
        <div class="timing-meds">${row.meds}</div>
      </div>`).join('')
    : '<div style="color:var(--text-muted); font-size:0.82rem;">Run analysis to see timing.</div>';
}

// ── AUDIT TRAIL ───────────────────────────────────────────────
function renderAuditTrail(data) {
  const el = document.getElementById('audit-content');
  const now = new Date().toLocaleString('en-IN');
  el.innerHTML = `
    <div><strong>Timestamp:</strong> ${now}</div>
    <div><strong>Device:</strong> web-dashboard</div>
    <div><strong>Medicines scanned:</strong> ${scannedMedicines.join(', ')}</div>
    <div><strong>Ayurvedic:</strong> ${ayurvedicMedicines.join(', ') || 'None'}</div>
    <div><strong>Patient:</strong> Age ${document.getElementById('patient-age').value}, CKD: ${document.getElementById('p-ckd').checked}, Diabetes: ${document.getElementById('p-diabetes').checked}</div>
    <div style="margin-top:8px;"><strong>Rules evaluated:</strong></div>
    ${(data.alerts || []).map(a =>
      `<div style="padding-left:8px;">• ${a.rule_id}: ${a.name} →${a.severity.toUpperCase()}</div>`
    ).join('')}
    <div style="margin-top:8px;"><strong>Overall risk:</strong> ${(data.overall_risk || '').toUpperCase()}</div>
    <div><strong>Compartments locked:</strong> ${data.lock_compartments?.join(', ') || 'None'}</div>
    <div><strong>WhatsApp sent:</strong> ${data.whatsapp_sent ? 'Yes ✅' : 'No'}</div>
  `;
}

function toggleAudit() {
  document.getElementById('audit-content').classList.toggle('show');
}

// ═══════════════════════════════════════════════════════════════
// PART 12 — OCR BUTTON + WHATSAPP BACKUP + HINDI VOICE
// (merged by Bhavya's build — do not remove)
// ═══════════════════════════════════════════════════════════════

// ── PRESCRIPTION PHOTO OCR (via backend + Gemini) ──────────────
async function uploadPrescription() {
  const fileInput = document.getElementById('ocr-file');
  if (!fileInput.files || !fileInput.files[0]) return;
  const file = fileInput.files[0];
  fileInput.value = '';

  const formData = new FormData();
  formData.append('image', file);

  try {
    const res = await fetch(`${BACKEND_URL}/scan-prescription`, {
      method: 'POST',
      body: formData
    });
    const data = await res.json();

    if (data.error) {
      alert('OCR failed: ' + data.error);
      return;
    }

    let added = 0;
    (data.medicines || []).forEach(name => {
      document.getElementById('med-input').value = name;
      addMedicine();
      added++;
    });

    let msg = 'Photo read — ' + added + ' medicine(s) added to the scan list.';
    if (data.unrecognized && data.unrecognized.length) {
      msg += '\n\nRead on the prescription but unknown to Electra ' +
             '(verify with doctor):\n- ' + data.unrecognized.join('\n- ');
    }
    if (added === 0 && (!data.unrecognized || !data.unrecognized.length)) {
      msg = 'No medicines could be read. Try a clearer photo.';
    }
    alert(msg);
  } catch (e) {
    alert('Upload failed — is the backend (uvicorn) running? (' + e.message + ')');
  }
}

// ── WHATSAPP CAREGIVER BACKUP (all alerts, live data, no API needed) ──
function notifyCaregiver() {
  if (!lastResponse || !lastResponse.alerts || !lastResponse.alerts.length) {
    alert('Run an analysis first.');
    return;
  }
  const phone = document.getElementById('p-caregiver').value.replace(/[^0-9]/g, '');
  if (!phone) { alert('Enter a caregiver phone number on the left.'); return; }

  let text = 'ELECTRA MEDISAFE ALERT — ' + lastResponse.overall_risk.toUpperCase() + '\n\n';
  lastResponse.alerts.forEach(function(a, i) {
    text += (i + 1) + '. ' + a.name + ' (' + a.severity.toUpperCase() + ')\n'
          + '   Medicines: ' + a.medicines_involved.join(' + ') + '\n'
          + '   Action: ' + a.action + '\n\n';
  });
  text += 'Please contact your doctor before giving these medicines.';

  window.open('https://wa.me/' + phone + '?text=' + encodeURIComponent(text), '_blank');
}

// ── HINDI VOICE (browser speech synthesis — no API needed) ─────
function speakHindi() {
  if (!lastResponse || !lastResponse.alerts || !lastResponse.alerts.length) {
    alert('Run an analysis first.');
    return;
  }
  if (!('speechSynthesis' in window)) {
    alert('This browser cannot speak. Please use Chrome or Edge.');
    return;
  }

  let text = 'चेतावनी। आपकी दवाओं में खतरनाक संयोजन मिला है। ';
  lastResponse.alerts.forEach(function(a, i) {
    const el = document.getElementById('exp-hindi-' + i);
    if (el && el.textContent.trim()) text += el.textContent.trim() + ' ';
  });
  text += 'कृपया डॉक्टर से संपर्क करें।';

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'hi-IN';
  utterance.rate = 0.95;

  const voices = window.speechSynthesis.getVoices();
  const hindi = voices.find(v => v.lang && v.lang.toLowerCase().startsWith('hi'));
  if (hindi) utterance.voice = hindi;

  window.speechSynthesis.cancel();   // stop anything already speaking
  window.speechSynthesis.speak(utterance);
}

// ══════════ NFC TAG ASSIGNMENT ══════════
async function loadTags() {
  try {
    const res = await fetch(`${BACKEND_URL}/tags`);
    const data = await res.json();
    const map = data.map || {};
    const display = data.display || {};
    const pending = data.pending || [];

    const medSel = document.getElementById('tag-med');
    if (medSel && medSel.options.length === 0 && allMedicineNames.length) {
      medSel.innerHTML = allMedicineNames.map(m => `<option value="${m}">${m}</option>`).join('');
    }

    const uidSel = document.getElementById('tag-uid');
    const uids = Object.keys(map);
    const opts = uids.map((u, i) => `<option value="${u}">Tag ${i + 1} — ${display[u] || map[u]}</option>`);
    pending.forEach(u => opts.push(`<option value="${u}">${u} (new — not assigned)</option>`));
    if (uidSel) uidSel.innerHTML = opts.join('') || '<option value="">no tags yet</option>';

    const list = document.getElementById('tag-list');
    if (list) {
      let rows = uids.map((u, i) => `Tag ${i + 1} — <strong>${display[u] || map[u]}</strong> <span style="opacity:0.55">(${u})</span>`);
      pending.forEach(u => rows.push(`<span style="color:#d99a1a">${u} — new tag, choose a medicine and press Assign</span>`));
      list.innerHTML = rows.join('<br>') || 'No tags assigned yet.';
    }
  } catch (e) { /* backend offline — ignore */ }
}

async function assignTag() {
  const uid = document.getElementById('tag-uid').value;
  const medicine = document.getElementById('tag-med').value;
  if (!uid || !medicine) return;
  await fetch(`${BACKEND_URL}/enroll-tag`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ uid: uid, medicine: medicine })
  });
  loadTags();
}

window.addEventListener('load', loadTags);

// ══════════ PHASE 2: patient fields ══════════
function toggleFemaleFields() {
  const female = (document.querySelector('input[name="p-sex"]:checked') || {}).value === 'female';
  const ff = document.getElementById('female-fields');
  const banner = document.getElementById('pregnancy-banner');
  if (ff) ff.style.display = female ? 'block' : 'none';

  const preg = document.getElementById('p-pregnant');
  const bf = document.getElementById('p-breastfeeding');
  const showBanner = female && ((preg && preg.checked) || (bf && bf.checked));
  if (banner) banner.style.display = showBanner ? 'block' : 'none';
}

window.addEventListener('load', toggleFemaleFields);

// ══════════ DOSE REMINDERS ══════════
let schedData = [];

async function loadSchedule() {
  try {
    const res = await fetch(`${BACKEND_URL}/schedule`);
    schedData = await res.json();
    renderSchedule();
  } catch (e) { /* backend offline */ }
}

function renderSchedule() {
  const c = document.getElementById('schedule-rows');
  if (!c) return;
  c.innerHTML = schedData.map((r, i) => `
    <div style="display:flex; gap:4px; margin-bottom:6px; align-items:center;">
      <input type="time" value="${r.time || '08:00'}"
             onchange="schedEdit(${i},'time',this.value)" style="width:86px; font-size:0.85rem; padding:4px; border:1px solid var(--border); border-radius:4px;">
      <input type="text" value="${(r.medicines || []).join(', ')}"
             placeholder="Glycomet 500, Ecosprin 75"
             onchange="schedEdit(${i},'medicines',this.value)"
             style="flex:1; font-size:0.85rem; padding:4px; border:1px solid var(--border); border-radius:4px;">
      <input type="text" value="${r.note || ''}"
             placeholder="Take with breakfast"
             onchange="schedEdit(${i},'note',this.value)"
             style="flex:1; font-size:0.85rem; padding:4px; border:1px solid var(--border); border-radius:4px;">
      <button style="font-size:0.85rem; padding:4px 8px; background:var(--risk-high); color:white; border:none; border-radius:4px; cursor:pointer;" onclick="schedDel(${i})">✕</button>
    </div>`).join('') || '<div style="font-size:0.85rem; color:var(--text-muted); font-weight:500;">No times set.</div>';
}

function schedEdit(i, field, val) {
  if (field === 'medicines') schedData[i].medicines = val.split(',').map(s => s.trim()).filter(Boolean);
  else schedData[i][field] = val;
}
function schedAdd() { schedData.push({ time: '08:00', medicines: [], note: '' }); renderSchedule(); }
function schedDel(i) { schedData.splice(i, 1); renderSchedule(); }

async function saveSchedule() {
  await fetch(`${BACKEND_URL}/schedule`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(schedData)
  });
  loadSchedule();
}

async function testReminder() {
  await fetch(`${BACKEND_URL}/schedule/test`, { method: 'POST' });
  alert('Test reminder sent — check the caregiver phone.');
}

window.addEventListener('load', loadSchedule);

