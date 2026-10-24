// ============================================================
// ELECTRA DASHBOARD — dashboard_tabs.js
// 4-Tab Navigation, Patient Presets, Verdict Strip & Sync
// ============================================================

(function () {
  'use strict';

  // ── TAB SWITCHING ──────────────────────────────────────────
  window.switchTab = function (tabId) {
    const btns = document.querySelectorAll('.tab-btn');
    const panes = document.querySelectorAll('.tab-pane');

    btns.forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
    });

    panes.forEach(pane => {
      pane.classList.toggle('active', pane.id === tabId);
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // ── PATIENT PRESETS ────────────────────────────────────────
  window.applyPatientPreset = function (presetKey) {
    const ageEl = document.getElementById('patient-age');
    const kidneyEl = document.getElementById('p-kidney-fn');
    const caregiverEl = document.getElementById('p-caregiver');
    const maleRadio = document.querySelector('input[name="p-sex"][value="male"]');
    const femaleRadio = document.querySelector('input[name="p-sex"][value="female"]');

    const cbIds = [
      'p-diabetes', 'p-hypertension', 'p-ckd', 'p-liver', 'p-hf', 'p-gi',
      'p-pregnant', 'p-breastfeeding', 'p-alcohol',
      'p-hypokalemia', 'p-hypomagnesemia', 'p-bradycardia', 'p-dehydration', 'p-copd', 'p-apnoea'
    ];

    // Reset all checkboxes first
    cbIds.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.checked = false;
    });

    if (presetKey === 'dadi') {
      if (ageEl) ageEl.value = 72;
      if (femaleRadio) femaleRadio.checked = true;
      if (kidneyEl) kidneyEl.value = 'mild';
      if (caregiverEl) caregiverEl.value = '+919876543210';
      ['p-diabetes', 'p-hypertension', 'p-ckd'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.checked = true;
      });
    } else if (presetKey === 'pregnant') {
      if (ageEl) ageEl.value = 28;
      if (femaleRadio) femaleRadio.checked = true;
      if (kidneyEl) kidneyEl.value = 'normal';
      if (caregiverEl) caregiverEl.value = '+919876543210';
      const el = document.getElementById('p-pregnant');
      if (el) el.checked = true;
    } else if (presetKey === 'feeding') {
      if (ageEl) ageEl.value = 30;
      if (femaleRadio) femaleRadio.checked = true;
      if (kidneyEl) kidneyEl.value = 'normal';
      if (caregiverEl) caregiverEl.value = '+919876543210';
      const el = document.getElementById('p-breastfeeding');
      if (el) el.checked = true;
    } else if (presetKey === 'healthy') {
      if (ageEl) ageEl.value = 40;
      if (maleRadio) maleRadio.checked = true;
      if (kidneyEl) kidneyEl.value = 'normal';
      if (caregiverEl) caregiverEl.value = '+919876543210';
    } else if (presetKey === 'clear') {
      if (ageEl) ageEl.value = '';
      if (maleRadio) maleRadio.checked = true;
      if (kidneyEl) kidneyEl.value = 'normal';
      if (caregiverEl) caregiverEl.value = '';
    }

    if (typeof window.toggleFemaleFields === 'function') {
      window.toggleFemaleFields();
    }

    updatePatientSummary();
  };

  // ── UPDATE LIVE PATIENT SUMMARY ───────────────────────────
  function updatePatientSummary() {
    const summaryEl = document.getElementById('verdict-patient-summary');
    if (!summaryEl) return;

    const age = document.getElementById('patient-age')?.value;
    const sex = document.querySelector('input[name="p-sex"]:checked')?.value;
    const kidney = document.getElementById('p-kidney-fn')?.value;
    const isFemale = sex === 'female';

    const conditions = [];
    if (document.getElementById('p-diabetes')?.checked) conditions.push('Diabetes');
    if (document.getElementById('p-hypertension')?.checked) conditions.push('Hypertension');
    if (document.getElementById('p-ckd')?.checked) conditions.push('CKD');
    if (document.getElementById('p-liver')?.checked) conditions.push('Liver');
    if (document.getElementById('p-hf')?.checked) conditions.push('Heart Failure');
    if (document.getElementById('p-gi')?.checked) conditions.push('GI Ulcer');
    if (isFemale && document.getElementById('p-pregnant')?.checked) conditions.push('Pregnant');
    if (isFemale && document.getElementById('p-breastfeeding')?.checked) conditions.push('Breastfeeding');
    if (document.getElementById('p-alcohol')?.checked) conditions.push('Alcohol');
    if (document.getElementById('p-copd')?.checked) conditions.push('COPD');
    if (document.getElementById('p-apnoea')?.checked) conditions.push('Sleep Apnoea');
    if (document.getElementById('p-bradycardia')?.checked) conditions.push('Slow HR');
    if (document.getElementById('p-hypokalemia')?.checked) conditions.push('Low K+');
    if (document.getElementById('p-hypomagnesemia')?.checked) conditions.push('Low Mg2+');
    if (document.getElementById('p-dehydration')?.checked) conditions.push('Dehydration');

    const parts = [];
    if (age) parts.push(`${age}y`);
    if (sex) parts.push(sex === 'female' ? 'F' : 'M');
    if (kidney && kidney !== 'normal') parts.push(`Kidney: ${kidney}`);
    if (conditions.length) {
      parts.push(conditions.slice(0, 3).join(', ') + (conditions.length > 3 ? ` +${conditions.length - 3}` : ''));
    }

    summaryEl.textContent = parts.length ? parts.join(' · ') : 'No profile set';
  }

  // ── UPDATE COUNTS & CHIP ───────────────────────────────────
  function updateCounts() {
    // 1. Med count
    const medContainer = document.getElementById('med-tags-container');
    const ayurContainer = document.getElementById('ayurvedic-tags');
    const medTags = medContainer ? medContainer.querySelectorAll('.med-tag').length : 0;
    const ayurTags = ayurContainer ? ayurContainer.querySelectorAll('.med-tag').length : 0;
    const totalMeds = medTags + ayurTags;
    const medCountEl = document.getElementById('verdict-med-count');
    if (medCountEl) {
      medCountEl.textContent = totalMeds === 1 ? '1 medicine' : `${totalMeds} medicines`;
    }

    // 2. Alert count
    const alertsContainer = document.getElementById('alert-cards-container');
    const alertCards = alertsContainer ? alertsContainer.querySelectorAll('.risk-card').length : 0;
    const alertCountEl = document.getElementById('verdict-alert-count');
    const reportBadgeEl = document.getElementById('report-tab-badge');
    const resultsContainer = document.getElementById('results-container');
    const hasAnalyzed = resultsContainer && resultsContainer.style.display === 'block';

    if (alertCountEl) {
      if (hasAnalyzed) {
        alertCountEl.textContent = alertCards === 1 ? '1 alert' : `${alertCards} alerts`;
        alertCountEl.style.color = alertCards > 0 ? 'var(--risk-high)' : 'var(--risk-low)';
      } else {
        alertCountEl.textContent = '—';
        alertCountEl.style.color = 'inherit';
      }
    }

    if (reportBadgeEl) {
      if (hasAnalyzed && alertCards > 0) {
        reportBadgeEl.textContent = alertCards;
        reportBadgeEl.style.display = 'inline-block';
      } else {
        reportBadgeEl.style.display = 'none';
      }
    }

    // 3. Risk Chip
    const riskChip = document.getElementById('verdict-risk-chip');
    const riskBadge = document.getElementById('risk-badge');
    const riskLabel = document.getElementById('risk-label');
    if (riskChip && riskBadge && riskLabel) {
      if (hasAnalyzed) {
        const currentClasses = riskBadge.className.split(/\s+/);
        const riskLevel = currentClasses.find(c => ['low', 'moderate', 'high', 'critical'].includes(c)) || 'none';
        riskChip.className = `verdict-chip ${riskLevel}`;
        riskChip.textContent = riskLabel.textContent.trim() || riskLevel.toUpperCase();
      } else {
        riskChip.className = 'verdict-chip none';
        riskChip.textContent = 'No Analysis Yet';
      }
    }

    // 4. Sync button loading state
    const realBtn = document.getElementById('analyze-btn');
    const stripBtn = document.querySelector('.verdict-analyze-btn');
    if (realBtn && stripBtn) {
      stripBtn.disabled = realBtn.disabled;
      if (realBtn.classList.contains('loading')) {
        stripBtn.classList.add('loading');
        stripBtn.textContent = '⏳ Analyzing...';
      } else {
        stripBtn.classList.remove('loading');
        stripBtn.textContent = '🔍 ANALYZE';
      }
    }

    // 5. Status card in Tab 4
    const tagList = document.getElementById('tag-list');
    const statusTagCount = document.getElementById('status-tag-count');
    if (tagList && statusTagCount) {
      const text = tagList.innerText || '';
      if (text.includes('No tags assigned')) {
        statusTagCount.textContent = '0 assigned';
      } else {
        const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
        statusTagCount.textContent = `${lines.length} assigned`;
      }
    }

    const schedRows = document.getElementById('schedule-rows');
    const statusSchedCount = document.getElementById('status-sched-count');
    if (schedRows && statusSchedCount) {
      const timeInputs = schedRows.querySelectorAll('input[type="time"]');
      statusSchedCount.textContent = `${timeInputs.length} set`;
    }
  }

  // ── INITIALIZATION & OBSERVERS ─────────────────────────────
  window.addEventListener('DOMContentLoaded', () => {
    // 1. Patient form inputs
    const patientFields = [
      'patient-age', 'p-kidney-fn', 'p-caregiver',
      'p-diabetes', 'p-hypertension', 'p-ckd', 'p-liver', 'p-hf', 'p-gi',
      'p-pregnant', 'p-breastfeeding', 'p-alcohol',
      'p-hypokalemia', 'p-hypomagnesemia', 'p-bradycardia', 'p-dehydration', 'p-copd', 'p-apnoea'
    ];
    patientFields.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('input', updatePatientSummary);
        el.addEventListener('change', updatePatientSummary);
      }
    });

    document.querySelectorAll('input[name="p-sex"]').forEach(r => {
      r.addEventListener('change', updatePatientSummary);
    });

    // 2. Observe med-tags-container and ayurvedic-tags
    const medCont = document.getElementById('med-tags-container');
    if (medCont) {
      new MutationObserver(updateCounts).observe(medCont, { childList: true, subtree: true });
    }
    const ayurCont = document.getElementById('ayurvedic-tags');
    if (ayurCont) {
      new MutationObserver(updateCounts).observe(ayurCont, { childList: true, subtree: true });
    }

    // 3. Observe results-container style display (AUTO-SWITCH TO REPORT TAB!)
    const resultsContainer = document.getElementById('results-container');
    if (resultsContainer) {
      new MutationObserver((mutations) => {
        for (const mutation of mutations) {
          if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
            if (resultsContainer.style.display === 'block') {
              window.switchTab('tab-report');
              updateCounts();
            }
          }
        }
      }).observe(resultsContainer, { attributes: true, attributeFilter: ['style'] });
    }

    // 4. Observe risk-badge and alert-cards-container
    const riskBadge = document.getElementById('risk-badge');
    if (riskBadge) {
      new MutationObserver(updateCounts).observe(riskBadge, { attributes: true, childList: true, subtree: true });
    }
    const alertsCont = document.getElementById('alert-cards-container');
    if (alertsCont) {
      new MutationObserver(updateCounts).observe(alertsCont, { childList: true, subtree: true });
    }

    // 5. Observe analyze-btn loading state
    const analyzeBtn = document.getElementById('analyze-btn');
    if (analyzeBtn) {
      new MutationObserver(updateCounts).observe(analyzeBtn, { attributes: true, childList: true });
    }

    // 6. Observe tag-list and schedule-rows for device status
    const tagList = document.getElementById('tag-list');
    if (tagList) {
      new MutationObserver(updateCounts).observe(tagList, { childList: true, subtree: true, characterData: true });
    }
    const schedRows = document.getElementById('schedule-rows');
    if (schedRows) {
      new MutationObserver(updateCounts).observe(schedRows, { childList: true, subtree: true });
    }

    // Also update when Load Demo button is clicked
    const demoBtn = document.querySelector('.btn-demo');
    if (demoBtn) {
      demoBtn.addEventListener('click', () => {
        setTimeout(() => {
          updatePatientSummary();
          updateCounts();
        }, 50);
      });
    }

    // Initial run
    updatePatientSummary();
    updateCounts();
  });

})();
