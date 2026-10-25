/**
 * SheCare AI / SurvivorCare AI - Security Agency Contact & Emergency Incident Reporting System
 * 
 * Enables survivors in danger and bystanders / witnesses of violent scenarios to:
 * 1. Contact security agencies (Police 15 / 112, Rescue 1122, Edhi 115, Women Helplines 1099/181, CPLC 1102).
 * 2. Share live GPS location coordinates, area address, and Google Maps pin link.
 * 3. Formulate structured incident reports (survivor distress or witness observation).
 * 4. Dispatch via 1-tap Phone Call, SMS, WhatsApp, Clipboard Copy, or Native Share.
 * 5. Securely log incidents locally for legal evidence and survivor protection.
 */

const AgencyReporting = {
  // Pre-configured official security and emergency agencies
  agencies: {
    Pakistan: [
      { id: 'pk-police-15', name: 'Police Emergency (Rescue 15)', phone: '15', type: 'police', desc: 'Immediate police response & armed dispatch' },
      { id: 'pk-rescue-1122', name: 'Rescue 1122 (Ambulance & Fire)', phone: '1122', type: 'rescue', desc: 'Emergency trauma ambulance and rescue squad' },
      { id: 'pk-edhi-115', name: 'Edhi Foundation Ambulance', phone: '115', type: 'rescue', desc: 'Nationwide emergency ambulance network' },
      { id: 'pk-women-1099', name: 'National Women Helpline (MOHR)', phone: '1099', type: 'helpline', desc: 'Ministry of Human Rights crisis intervention' },
      { id: 'pk-vawc-1043', name: 'Punjab Women Protection (VAWC)', phone: '1043', type: 'helpline', desc: 'Violence Against Women Centre & Safe City' },
      { id: 'pk-cplc-1102', name: 'CPLC Karachi Police Liaison', phone: '1102', type: 'police', desc: 'Citizen-Police Liaison Committee crime control' }
    ],
    India: [
      { id: 'in-emergency-112', name: 'National Emergency Helpline', phone: '112', type: 'emergency', desc: 'Integrated Police, Medical & Fire response' },
      { id: 'in-women-181', name: 'Women Helpline (Domestic Abuse)', phone: '181', type: 'helpline', desc: 'National Commission for Women 24/7 lifeline' },
      { id: 'in-police-100', name: 'Police Control Room', phone: '100', type: 'police', desc: 'State police emergency dispatch' },
      { id: 'in-ambulance-108', name: 'National Ambulance Service', phone: '108', type: 'rescue', desc: 'Emergency medical services' }
    ],
    International: [
      { id: 'intl-us-911', name: 'USA & Canada Emergency (911)', phone: '911', type: 'emergency', desc: 'Police, Fire and EMS Dispatch' },
      { id: 'intl-uk-999', name: 'UK National Emergency (999)', phone: '999', type: 'emergency', desc: 'Police and Ambulance Service' },
      { id: 'intl-eu-112', name: 'European Emergency Number (112)', phone: '112', type: 'emergency', desc: 'Universal emergency dispatch' }
    ]
  },

  // State
  state: {
    reporterRole: 'survivor', // 'survivor' or 'witness'
    incidentType: 'assault',
    lat: null,
    lng: null,
    areaName: '',
    landmark: '',
    details: '',
    selectedTags: [],
    targetAgencyPhone: '15'
  },

  // Initialize
  init() {
    this.setupEventListeners();
  },

  setupEventListeners() {
    // Open modal button
    const btnOpen = document.getElementById('btnOpenAgencyReportModal');
    if (btnOpen) {
      btnOpen.addEventListener('click', () => this.openReportModal());
    }

    // Modal role buttons
    const roleBtns = document.querySelectorAll('.agency-role-btn');
    roleBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const role = btn.getAttribute('data-role');
        this.setReporterRole(role);
      });
    });

    // Incident type selector
    const selectType = document.getElementById('agencyIncidentType');
    if (selectType) {
      selectType.addEventListener('change', (e) => {
        this.state.incidentType = e.target.value;
        this.updatePreview();
      });
    }

    // Landmark input
    const inputLandmark = document.getElementById('agencyReportLandmark');
    if (inputLandmark) {
      inputLandmark.addEventListener('input', (e) => {
        this.state.landmark = e.target.value;
        this.updatePreview();
      });
    }

    // Details textarea
    const inputDetails = document.getElementById('agencyReportDetails');
    if (inputDetails) {
      inputDetails.addEventListener('input', (e) => {
        this.state.details = e.target.value;
        this.updatePreview();
      });
    }

    // Quick situation chips
    document.querySelectorAll('.agency-situation-chip').forEach(chip => {
      chip.addEventListener('click', (e) => {
        e.preventDefault();
        const tag = chip.getAttribute('data-tag');
        this.toggleSituationTag(tag, chip);
      });
    });

    // Refresh GPS button inside modal
    const btnGps = document.getElementById('btnAgencyRefreshGps');
    if (btnGps) {
      btnGps.addEventListener('click', () => this.detectDeviceGps());
    }

    // Send SMS
    const btnSms = document.getElementById('btnAgencySendSms');
    if (btnSms) {
      btnSms.addEventListener('click', () => this.dispatchViaSms());
    }

    // Share WhatsApp
    const btnWa = document.getElementById('btnAgencySendWhatsApp');
    if (btnWa) {
      btnWa.addEventListener('click', () => this.dispatchViaWhatsApp());
    }

    // Copy to clipboard
    const btnCopy = document.getElementById('btnAgencyCopyReport');
    if (btnCopy) {
      btnCopy.addEventListener('click', () => this.copyReportToClipboard());
    }

    // Native Share
    const btnShare = document.getElementById('btnAgencyNativeShare');
    if (btnShare) {
      btnShare.addEventListener('click', () => this.dispatchViaNativeShare());
    }

    // Save locally
    const btnSave = document.getElementById('btnAgencySaveReport');
    if (btnSave) {
      btnSave.addEventListener('click', () => this.saveReportLocally());
    }
  },

  // Open the report modal with optional prefill
  openReportModal(prefill = {}) {
    // 1. Sync location from NearbyPlaces if available
    if (typeof NearbyPlaces !== 'undefined' && NearbyPlaces.currentLocation) {
      this.state.lat = NearbyPlaces.currentLocation.lat;
      this.state.lng = NearbyPlaces.currentLocation.lng;
      this.state.areaName = NearbyPlaces.currentLocation.name || 'Selected Location';
    } else {
      // Default to Lahore center if location unset
      this.state.lat = 31.5204;
      this.state.lng = 74.3587;
      this.state.areaName = 'Lahore, Pakistan (Default area - click GPS to detect)';
    }

    // 2. Apply prefill
    if (prefill.role) this.state.reporterRole = prefill.role;
    if (prefill.incidentType) this.state.incidentType = prefill.incidentType;
    if (prefill.agencyPhone) this.state.targetAgencyPhone = prefill.agencyPhone;
    if (prefill.landmark) this.state.landmark = prefill.landmark;
    if (prefill.details) this.state.details = prefill.details;

    // 3. Update UI fields
    this.updateModalUi();
    this.updatePreview();

    // 4. Open Modal via App
    if (typeof App !== 'undefined' && App.openModal) {
      App.openModal('modalAgencyReport');
    } else {
      const m = document.getElementById('modalAgencyReport');
      if (m) m.classList.add('active');
    }
  },

  // Open report modal prefilled for a specific agency/place from the map
  openReportForPlace(placeName, placePhone, placeLat = null, placeLng = null) {
    const cleanPhone = (placePhone || '15').replace(/[^0-9+]/g, '');
    this.openReportModal({
      targetAgencyPhone: cleanPhone || '15',
      landmark: `Direct report to: ${decodeURIComponent(placeName)} (${placePhone})`
    });
  },

  // Switch between Survivor in Danger vs. Witness / Bystander
  setReporterRole(role) {
    this.state.reporterRole = role;
    document.querySelectorAll('.agency-role-btn').forEach(btn => {
      if (btn.getAttribute('data-role') === role) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    const roleBanner = document.getElementById('agencyRoleBanner');
    if (roleBanner) {
      if (role === 'survivor') {
        roleBanner.className = 'alert-box alert-danger';
        roleBanner.innerHTML = '<strong>🔴 SURVIVOR DISTRESS DISPATCH:</strong> You are reporting that you are personally in immediate danger. Your live GPS coordinates will be prioritized for rapid emergency police & medical response.';
      } else {
        roleBanner.className = 'alert-box alert-warning';
        roleBanner.innerHTML = '<strong>🟡 WITNESS / BYSTANDER INCIDENT REPORT:</strong> You are reporting an ongoing violent crime, assault, or scenario you observed. Your report helps security agencies locate and protect victims immediately.';
      }
    }

    this.updatePreview();
  },

  // Toggle quick situation tag
  toggleSituationTag(tag, element) {
    const idx = this.state.selectedTags.indexOf(tag);
    if (idx > -1) {
      this.state.selectedTags.splice(idx, 1);
      if (element) element.classList.remove('active');
    } else {
      this.state.selectedTags.push(tag);
      if (element) element.classList.add('active');
    }
    this.updatePreview();
  },

  // Detect GPS directly from inside modal
  detectDeviceGps() {
    if (!navigator.geolocation) {
      alert('Browser geolocation is unavailable on this device. You can type your location instead.');
      return;
    }

    const btn = document.getElementById('btnAgencyRefreshGps');
    if (btn) btn.innerHTML = '⏳ Locating...';

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        this.state.lat = Math.round(pos.coords.latitude * 10000) / 10000;
        this.state.lng = Math.round(pos.coords.longitude * 10000) / 10000;
        this.state.areaName = `Current GPS Pin [${this.state.lat}, ${this.state.lng}]`;
        
        // Sync back to NearbyPlaces
        if (typeof NearbyPlaces !== 'undefined' && NearbyPlaces.setUserCoordinates) {
          NearbyPlaces.setUserCoordinates(this.state.lat, this.state.lng, 'Device GPS (Reporting)', true);
        }

        this.updateModalUi();
        this.updatePreview();
        if (btn) btn.innerHTML = '📍 Use My GPS';
        if (typeof App !== 'undefined' && App.showToast) {
          App.showToast('GPS coordinates acquired for emergency report!', 'success');
        }
      },
      (err) => {
        if (btn) btn.innerHTML = '📍 Use My GPS';
        alert('Could not acquire device GPS. You can type the area or street address in the landmark box.');
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  },

  // Generate structured dispatch message
  generateReportText() {
    const isSurvivor = this.state.reporterRole === 'survivor';
    const header = isSurvivor
      ? '🚨 [CRITICAL SURVIVOR DISTRESS REPORT]'
      : '👁️ [WITNESS / BYSTANDER INCIDENT REPORT]';

    const typeLabels = {
      assault: 'Physical Assault / Sexual Violence Threat',
      harassment: 'Stalking / Menacing Pursuit / Harassment',
      domestic: 'Domestic Violence / Hostage / Trapped',
      medical: 'Medical Emergency / Severe Trauma / Bleeding',
      kidnapping: 'Attempted Abduction / Illegal Detention',
      crime: 'Witnessed Violent Crime / Suspicious Armed Individuals',
      other: 'Emergency Safety Incident'
    };

    const typeStr = typeLabels[this.state.incidentType] || 'Emergency Safety Incident';
    const latStr = this.state.lat ? this.state.lat.toFixed(5) : 'Unknown';
    const lngStr = this.state.lng ? this.state.lng.toFixed(5) : 'Unknown';
    const mapUrl = this.state.lat && this.state.lng
      ? `https://maps.google.com/?q=${latStr},${lngStr}`
      : 'Coordinates unavailable';

    const tagsStr = this.state.selectedTags.length > 0
      ? `\nURGENT FLAGS: ${this.state.selectedTags.join(', ')}`
      : '';

    const landmarkStr = this.state.landmark ? `\nLANDMARK / ADDRESS: ${this.state.landmark}` : '';
    const detailsStr = this.state.details ? `\nSITUATION DETAILS: ${this.state.details}` : '';

    const reporterNote = isSurvivor
      ? 'I am in immediate danger and require emergency security/police/medical dispatch to this exact location.'
      : 'I am a bystander/witness reporting an emergency scenario at this location. Please dispatch security/rescue units immediately.';

    const timeStr = new Date().toLocaleString();

    return `${header}
INCIDENT: ${typeStr}
LOCATION: ${this.state.areaName}
GPS COORDINATES: ${latStr}, ${lngStr}
LIVE MAP PIN: ${mapUrl}${landmarkStr}${tagsStr}${detailsStr}
ACTION REQUESTED: ${reporterNote}
TIMESTAMP: ${timeStr}
DISPATCHED VIA: SheCare AI Emergency System`;
  },

  // Update UI display inside modal
  updateModalUi() {
    const coordsEl = document.getElementById('agencyReportCoords');
    if (coordsEl) {
      coordsEl.innerText = this.state.lat && this.state.lng
        ? `${this.state.lat.toFixed(4)}° N, ${this.state.lng.toFixed(4)}° E`
        : 'Coordinates not detected';
    }

    const areaEl = document.getElementById('agencyReportAreaName');
    if (areaEl) {
      areaEl.innerText = this.state.areaName || 'Area unselected';
    }

    const mapLink = document.getElementById('agencyReportMapLink');
    if (mapLink && this.state.lat && this.state.lng) {
      mapLink.href = `https://maps.google.com/?q=${this.state.lat},${this.state.lng}`;
      mapLink.style.display = 'inline-flex';
    }

    const inputLandmark = document.getElementById('agencyReportLandmark');
    if (inputLandmark && !inputLandmark.value) {
      inputLandmark.value = this.state.landmark;
    }

    const inputDetails = document.getElementById('agencyReportDetails');
    if (inputDetails && !inputDetails.value) {
      inputDetails.value = this.state.details;
    }
  },

  // Update live preview box
  updatePreview() {
    const previewEl = document.getElementById('agencyReportPreview');
    if (previewEl) {
      previewEl.value = this.generateReportText();
    }
  },

  // Dispatch via Native SMS
  dispatchViaSms() {
    const targetPhone = (this.state.targetAgencyPhone || '15').replace(/[^0-9+]/g, '');
    const reportText = this.generateReportText();
    const encoded = encodeURIComponent(reportText);

    // Truthful log
    this.logIncidentLocally('SMS App Handshake', targetPhone);

    const smsUrl = `sms:${targetPhone}?body=${encoded}`;
    window.location.href = smsUrl;

    if (typeof App !== 'undefined' && App.showToast) {
      App.showToast('Opened SMS composer. Tap Send to dispatch to agency.', 'info');
    }
  },

  // Dispatch via WhatsApp
  dispatchViaWhatsApp() {
    const reportText = this.generateReportText();
    const encoded = encodeURIComponent(reportText);

    this.logIncidentLocally('WhatsApp Handshake', 'Broadcast');

    const waUrl = `https://wa.me/?text=${encoded}`;
    window.open(waUrl, '_blank', 'noopener,noreferrer');

    if (typeof App !== 'undefined' && App.showToast) {
      App.showToast('Opened WhatsApp composer with report and live map pin.', 'success');
    }
  },

  // Copy full report to clipboard
  copyReportToClipboard() {
    const reportText = this.generateReportText();
    navigator.clipboard.writeText(reportText).then(() => {
      const btn = document.getElementById('btnAgencyCopyReport');
      if (btn) {
        const orig = btn.innerHTML;
        btn.innerHTML = '✅ Copied to Clipboard!';
        setTimeout(() => { btn.innerHTML = orig; }, 2500);
      }
      if (typeof App !== 'undefined' && App.showToast) {
        App.showToast('Emergency Report & Location copied to clipboard!', 'success');
      }
    }).catch(err => {
      alert('Could not copy automatically. You can copy the text manually from the preview box.');
    });
  },

  // Native Share
  dispatchViaNativeShare() {
    const reportText = this.generateReportText();
    const mapUrl = this.state.lat && this.state.lng
      ? `https://maps.google.com/?q=${this.state.lat},${this.state.lng}`
      : 'https://maps.google.com';

    if (navigator.share) {
      navigator.share({
        title: 'EMERGENCY INCIDENT REPORT - SHECARE AI',
        text: reportText,
        url: mapUrl
      }).then(() => {
        this.logIncidentLocally('Device Native Share', 'Multiple Apps');
        if (typeof App !== 'undefined' && App.showToast) {
          App.showToast('Incident report shared via device.', 'success');
        }
      }).catch(e => {
        console.log('Share canceled or dismissed');
      });
    } else {
      this.copyReportToClipboard();
    }
  },

  // Log incident securely in localStorage for evidentiary backup
  logIncidentLocally(channel, recipient) {
    const reportItem = {
      id: 'INC-' + Date.now().toString(36).toUpperCase(),
      timestamp: new Date().toISOString(),
      role: this.state.reporterRole,
      type: this.state.incidentType,
      lat: this.state.lat,
      lng: this.state.lng,
      area: this.state.areaName,
      landmark: this.state.landmark,
      details: this.state.details,
      tags: this.state.selectedTags,
      channel: channel,
      recipient: recipient,
      status: 'DISPATCHED_TO_DEVICE'
    };

    try {
      const existing = JSON.parse(localStorage.getItem('survivorcare_incident_reports') || '[]');
      existing.unshift(reportItem);
      // Keep up to 50 reports locally
      if (existing.length > 50) existing.length = 50;
      localStorage.setItem('survivorcare_incident_reports', JSON.stringify(existing));
    } catch (e) {
      console.warn('Could not save incident log locally:', e);
    }

    return reportItem;
  },

  // Manual save from modal button
  saveReportLocally() {
    const item = this.logIncidentLocally('Manual Save / Evidence Record', 'Local Archive');
    if (typeof App !== 'undefined' && App.showToast) {
      App.showToast(`Incident report saved locally with ID: ${item.id}`, 'success');
    } else {
      alert(`Incident report saved locally with ID: ${item.id}\nPreserved for legal and protection evidence.`);
    }
  }
};

// Global attachment
if (typeof window !== 'undefined') {
  window.AgencyReporting = AgencyReporting;
}
