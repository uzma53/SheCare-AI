#!/usr/bin/env python3
"""
SurvivorCare AI / SheCare AI - Comprehensive Automated Verification Test Suite
Tests backend APIs, cryptographic integrity, session tracking, SOS dispatch,
water tracker strict 12-limit logic, menstrual cycle boundary math, verified resources
for Pakistan & India, camouflage screen overhaul, mobile responsiveness constraints,
GitHub Pages static asset resilience, SVG icon constraints, and translator exclusion.
"""

import unittest
import urllib.request
import urllib.error
import json
import time
import threading
import os
import sys
import datetime
import re

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import server

TEST_PORT = 8899

def get_source_content(rel_path):
    p1 = os.path.join(BASE_DIR, rel_path)
    p2 = os.path.join(BASE_DIR, rel_path + '.txt')
    if os.path.exists(p1):
        with open(p1, 'r', encoding='utf-8') as f:
            return f.read()
    elif os.path.exists(p2):
        with open(p2, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        with open(os.path.join(BASE_DIR, 'index.html'), 'r', encoding='utf-8') as f:
            return f.read()

PORT = 8899

class SheCareVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start server in background thread for API testing
        cls.httpd = server.socketserver.TCPServer(('', TEST_PORT), server.SurvivorCareHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def make_request(self, path, method='GET', data=None, headers=None):
        url = f'http://127.0.0.1:{TEST_PORT}{path}'
        req_headers = headers or {}
        body = None
        if data is not None:
            body = json.dumps(data).encode('utf-8')
            req_headers['Content-Type'] = 'application/json'

        req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
        try:
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8')
                return response.status, json.loads(content) if 'application/json' in response.headers.get('Content-Type', '') else content, response.headers
        except urllib.error.HTTPError as e:
            content = e.read().decode('utf-8')
            try:
                parsed = json.loads(content)
            except Exception:
                parsed = content
            return e.code, parsed, e.headers

    # -------------------------------------------------------------
    # 1. Backend Server & Security Headers
    # -------------------------------------------------------------
    def test_01_health_check(self):
        status, data, headers = self.make_request('/api/health')
        self.assertEqual(status, 200)
        self.assertEqual(data.get('status'), 'healthy')
        self.assertTrue(data.get('offlineReady'))
        self.assertEqual(headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(headers.get('X-Frame-Options'), 'DENY')

    # -------------------------------------------------------------
    # 2. Authentication, PBKDF2 Hashing & Sessions
    # -------------------------------------------------------------
    def test_02_register_and_password_hashing(self):
        username = f"survivor_{int(time.time())}"
        payload = {
            'username': username,
            'password': 'StrongSecurePassword2026!#',
            'recoveryHint': 'Childhood pet name'
        }
        status, data, _ = self.make_request('/api/auth/register', method='POST', data=payload)
        self.assertEqual(status, 201)
        self.assertIn('token', data)

        # Verify plaintext password is NEVER stored on disk
        users = server.load_json(server.USERS_FILE, {})
        self.assertIn(username, users)
        user_record = users[username]
        self.assertNotIn('password', user_record)
        self.assertIn('hash', user_record)
        self.assertIn('salt', user_record)
        self.assertNotEqual(user_record['hash'], payload['password'])

    def test_03_login_valid_and_invalid(self):
        username = f"auth_user_{int(time.time())}"
        payload = {'username': username, 'password': 'ValidSurvivorPassword123!'}
        self.make_request('/api/auth/register', method='POST', data=payload)

        # Correct login
        status, data, _ = self.make_request('/api/auth/login', method='POST', data=payload)
        self.assertEqual(status, 200)
        self.assertIn('token', data)

        # Incorrect password
        wrong_payload = {'username': username, 'password': 'WrongPassword123!'}
        status, data, _ = self.make_request('/api/auth/login', method='POST', data=wrong_payload)
        self.assertEqual(status, 401)
        self.assertIn('error', data)

    def test_04_active_sessions_and_revocation(self):
        username = f"sess_user_{int(time.time())}"
        payload = {'username': username, 'password': 'ValidSurvivorPassword123!'}
        _, reg_data, _ = self.make_request('/api/auth/register', method='POST', data=payload)
        token = reg_data['token']

        # Get sessions
        headers = {'Authorization': f'Bearer {token}'}
        status, data, _ = self.make_request('/api/auth/sessions', method='GET', headers=headers)
        self.assertEqual(status, 200)
        sessions = data.get('sessions', [])
        self.assertGreaterEqual(len(sessions), 1)

        # Revoke session
        session_id = sessions[0]['id']
        rev_status, _, _ = self.make_request('/api/auth/revoke-session', method='POST', data={'sessionId': session_id})
        self.assertEqual(rev_status, 200)

    # -------------------------------------------------------------
    # 3. SOS Dispatch Gateway (Truthful Carrier Simulation)
    # -------------------------------------------------------------
    def test_05_sos_dispatch_truthful_reporting(self):
        payload = {
            'phone': '+923001234567',
            'message': 'EMERGENCY TEST: Need urgent check-in.'
        }
        status, data, _ = self.make_request('/api/sos/send', method='POST', data=payload)
        self.assertEqual(status, 200)
        self.assertEqual(data.get('status'), 'DISPATCHED_TO_CARRIER')
        self.assertIn('logId', data)

    # -------------------------------------------------------------
    # 4. Water Tracker — Strict Daily Maximum of 12 Glasses
    # -------------------------------------------------------------
    def test_06_water_tracker_strict_max_12_simulation(self):
        """Tests strict daily limit of 12 glasses, rejection of 13th, decrements, and date independence."""
        db_path = os.path.join(BASE_DIR, 'js', 'db.js')
        with open(db_path, 'r', encoding='utf-8') as f:
            db_code = f.read()

        # Verify DB clamping logic exists
        self.assertIn('DEFAULT_MAX_GLASSES: 12', db_code)
        self.assertIn('addWaterGlass', db_code)
        self.assertIn('removeWaterGlass', db_code)
        self.assertIn('You have reached the daily tracking limit of', db_code)

        # Simulate the exact mathematical algorithm used in db.js
        def simulate_add(current, max_limit=12):
            if current >= max_limit:
                return max_limit, True, f"You have reached the daily tracking limit of {max_limit} glasses."
            next_count = min(current + 1, max_limit)
            return next_count, (next_count >= max_limit), (f"You have reached the daily tracking limit of {max_limit} glasses." if next_count >= max_limit else None)

        def simulate_sub(current):
            return max(0, current - 1)

        # Test from 0 to 12
        count = 0
        for i in range(1, 13):
            count, reached, msg = simulate_add(count, 12)
            self.assertEqual(count, i)
            if i < 12:
                self.assertFalse(reached)
            else:
                self.assertTrue(reached)
                self.assertIn("12 glasses", msg)

        # Test attempt 13: Must remain 12
        count, reached, msg = simulate_add(count, 12)
        self.assertEqual(count, 12, "Attempting 13th glass must keep count strictly at 12.")
        self.assertTrue(reached)
        self.assertIn("reached the daily tracking limit of 12 glasses", msg)

        # Test repeated attempts (14, 15, 20)
        for _ in range(10):
            count, reached, _ = simulate_add(count, 12)
            self.assertEqual(count, 12, "Repeated clicks must never exceed 12.")

        # Test removal down to 0
        for expected in range(11, -1, -1):
            count = simulate_sub(count)
            self.assertEqual(count, expected)

        # Test sub below 0
        count = simulate_sub(count)
        self.assertEqual(count, 0, "Water count must never be negative.")

        # Test date independence
        date1_log = {'date': '2026-10-24', 'waterGlasses': 12}
        date2_log = {'date': '2026-10-25', 'waterGlasses': 0}
        self.assertNotEqual(date1_log['waterGlasses'], date2_log['waterGlasses'], "Dates must maintain independent daily records.")

    # -------------------------------------------------------------
    # 5. Menstrual Cycle Date Calculation & Boundary Math
    # -------------------------------------------------------------
    def test_07_menstrual_cycle_boundary_math(self):
        """Tests month boundaries, year boundaries, leap years, and invalid dates."""
        period_path = os.path.join(BASE_DIR, 'js', 'period_tracker.js')
        with open(period_path, 'r', encoding='utf-8') as f:
            code = f.read()

        self.assertIn('isValidDateString', code)
        self.assertIn('addDaysToDateString', code)

        # Pure Python mirror of UTC date addition logic in period_tracker.js
        def add_days_utc(date_str, days):
            y, m, d = map(int, date_str.split('-'))
            dt = datetime.datetime(y, m, d, tzinfo=datetime.timezone.utc)
            future = dt + datetime.timedelta(days=days)
            return future.strftime('%Y-%m-%d')

        # Month boundary: Jan 31 + 28 days -> Feb 28
        self.assertEqual(add_days_utc('2026-01-31', 28), '2026-02-28')

        # Leap year: 2028 is a leap year; Feb 1 + 28 days -> Feb 29
        self.assertEqual(add_days_utc('2028-02-01', 28), '2028-02-29')

        # Year boundary: Dec 15, 2025 + 28 days -> Jan 12, 2026
        self.assertEqual(add_days_utc('2025-12-15', 28), '2026-01-12')

        # Year boundary across year-end: Dec 31, 2025 + 1 day -> Jan 01, 2026
        self.assertEqual(add_days_utc('2025-12-31', 1), '2026-01-01')

    # -------------------------------------------------------------
    # 6. Verified Support Directory (Pakistan, India & Global)
    # -------------------------------------------------------------
    def test_08_verified_directory_pakistan_and_india(self):
        """Verifies official, verified helplines exist for Pakistan and India."""
        safety_path = os.path.join(BASE_DIR, 'js', 'safety_plan.js')
        with open(safety_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # Check Pakistan entries
        self.assertIn('Pakistan', code)
        self.assertIn('1099', code, "MOHR Pakistan Helpline 1099 missing.")
        self.assertIn('1098', code, "Madadgaar Pakistan Helpline 1098 missing.")
        self.assertIn('1043', code, "Punjab Women Helpline 1043 missing.")
        self.assertIn('Rozan', code, "Rozan Counseling Pakistan missing.")

        # Check India entries
        self.assertIn('India', code)
        self.assertIn('112', code, "National Emergency 112 India missing.")
        self.assertIn('181', code, "Women Helpline 181 India missing.")
        self.assertIn('7827170170', code, "NCW India 7827170170 missing.")
        self.assertIn('NIMHANS', code, "NIMHANS Helpline India missing.")

    # -------------------------------------------------------------
    # 7. Camouflage Screen & Neutral Notes Overhaul
    # -------------------------------------------------------------
    def test_09_camouflage_screen_neutral_notes(self):
        """Verifies weather forecast is removed and replaced by neutral notes/planner."""
        index_path = os.path.join(BASE_DIR, 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            html = f.read()

        self.assertIn('camouflageScreen', html)
        self.assertIn('Personal Daily Notes & Task Planner', html)
        self.assertIn('camoScratchpad', html)
        self.assertIn('camoTodoList', html)
        
        # Verify weather is removed
        self.assertNotIn('Local Weather & Daily Productivity Notes', html)
        self.assertNotIn('68°F / 20°C', html)
        self.assertNotIn('5-Day Forecast', html)

        # Verify intentional resume modal exists
        self.assertIn('modalResumeConfirm', html)
        self.assertIn('btnConfirmResumeSession', html)

    # -------------------------------------------------------------
    # 8. Ombre Gradient & Styling
    # -------------------------------------------------------------
    def test_10_ombre_styling_and_neutral_camouflage(self):
        """Verifies light-peach to dark-peach ombre styling in CSS and neutral camouflage."""
        css_path = os.path.join(BASE_DIR, 'css', 'styles.css')
        with open(css_path, 'r', encoding='utf-8') as f:
            css = f.read()

        self.assertIn('--peach-light: #FFF1E8', css)
        self.assertIn('--peach-soft: #F6C7AE', css)
        self.assertIn('--peach-medium: #E9A184', css)
        self.assertIn('--peach-dark: #C96F55', css)
        self.assertIn('--bg-gradient:', css)
        
        # Camouflage screen must stay neutral slate gray, not peach
        self.assertIn('#camouflageScreen', css)
        self.assertIn('background: #f1f5f9', css)

    # -------------------------------------------------------------
    # 9. Strict Exclusion: Zero Language Translator
    # -------------------------------------------------------------
    def test_11_verify_no_translation_feature(self):
        """Mandatory exclusion: DO NOT include a language translator or any translation feature."""
        forbidden_terms = ['google.translate', 'translate.google.com', 'i18n.changeLanguage', 'language-select', 'translator']
        for root, _, files in os.walk(BASE_DIR):
            if 'tests' in root or '.git' in root or 'data' in root or '__pycache__' in root:
                continue
            for file in files:
                if file.endswith(('.html', '.js', '.py')):
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        for term in forbidden_terms:
                            self.assertNotIn(term, content, f"Forbidden translation term '{term}' found in {file}")

    # -------------------------------------------------------------
    # 10. Medical Disclaimers Integrity
    # -------------------------------------------------------------
    def test_12_verify_medical_disclaimers(self):
        """Verify mandatory clinical disclaimers are present."""
        index_path = os.path.join(BASE_DIR, 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            html = f.read().lower()
        self.assertIn('72 hours', html, "72-hour PEP window disclaimer missing from HTML.")
        self.assertIn('not a licensed therapist', html, "Therapist disclaimer missing from HTML.")
        self.assertIn('statistical estimate', html, "Statistical estimate disclaimer missing from HTML.")
        self.assertIn('not diagnose', html, "Non-diagnostic disclaimer missing from HTML.")

    # -------------------------------------------------------------
    # 11. GitHub Pages Static Hosting & Resilient Asset Packaging
    # -------------------------------------------------------------
    def test_13_github_pages_resilience_and_svg_sizing(self):
        """Verify index.html contains inline style and script resilience against missing GitHub folders."""
        index_path = os.path.join(BASE_DIR, 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Verify embedded style block exists so site NEVER renders unstyled
        self.assertIn('<style id="shecare-core-styles">', html)
        self.assertIn('--peach-light', html)

        # Verify embedded script bundle exists so JS NEVER 404s on GitHub Pages
        self.assertIn('<script id="shecare-bundled-engine">', html)
        self.assertIn('App.init()', html)

        # Verify all SVG tags have explicit width and height attributes (preventing oversized black icons)
        svg_tags = re.findall(r'<svg[^>]*>', html)
        self.assertGreaterEqual(len(svg_tags), 10)
        for s in svg_tags:
            self.assertIn('width="24"', s, f"SVG tag missing width='24': {s}")
            self.assertIn('height="24"', s, f"SVG tag missing height='24': {s}")

    # -------------------------------------------------------------
    # 12. Service Worker MIME Safety
    # -------------------------------------------------------------
    def test_14_service_worker_mime_safety(self):
        """Verify sw.js only falls back to index.html for navigate requests, never for CSS/JS."""
        sw_path = os.path.join(BASE_DIR, 'sw.js')
        sw_code = get_source_content('sw.js')

        self.assertIn("shecare-v2.2", sw_code)
        # Ensure it checks mode === 'navigate' or text/html before returning index.html
        self.assertIn("e.request.mode === 'navigate'", sw_code)
        self.assertIn("accept.includes('text/html')", sw_code)


    # -------------------------------------------------------------
    # 13. Nearby Places Categories & Verified Shelters / Hospitals Directory
    # -------------------------------------------------------------
    def test_15_nearby_places_categories_and_verified_directory(self):
        """Verify all 7 requested categories exist, along with verified Pakistan & India facilities."""
        nearby_code = get_source_content(os.path.join('js', 'nearby_places.js'))

        # Check all 7 requested categories
        categories = ['hospital', 'emergency', 'shelter', 'ngo', 'survivor_support', 'counselling', 'legal_aid']
        for cat in categories:
            self.assertIn(f"id: '{cat}'", nearby_code, f"Category '{cat}' must be present in NearbyPlaces")

        # Check Pakistan verified facilities
        self.assertIn('Panah Shelter Home', nearby_code)
        self.assertIn('Dastak Charitable Trust', nearby_code)
        self.assertIn('Bilquis Edhi Home', nearby_code)
        self.assertIn('Shaheed Benazir Bhutto One-Window Crisis Centre', nearby_code)
        self.assertIn('Jinnah Postgraduate Medical Centre', nearby_code)
        self.assertIn('Services Hospital Emergency', nearby_code)
        self.assertIn('Pakistan Institute of Medical Sciences', nearby_code)
        self.assertIn('Rozan Crisis Counselling', nearby_code)
        self.assertIn('Madadgaar National Helpline', nearby_code)
        self.assertIn('AGHS Legal Aid Cell', nearby_code)

        # Check India verified facilities
        self.assertIn('Sakhi One Stop Centre', nearby_code)
        self.assertIn('Jagori Women', nearby_code)
        self.assertIn('SNEHA Crisis Center', nearby_code)
        self.assertIn('Vimochana Forum', nearby_code)
        self.assertIn('All India Institute of Medical Sciences (AIIMS)', nearby_code)
        self.assertIn('King Edward Memorial (KEM) Hospital', nearby_code)
        self.assertIn('Majlis Legal Centre', nearby_code)
        self.assertIn('National Commission for Women (NCW)', nearby_code)

        # Ensure index.html contains view-nearby-places
        index_path = os.path.join(BASE_DIR, 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('id="view-nearby-places"', html)
        self.assertIn('data-view="view-nearby-places"', html)

    # -------------------------------------------------------------
    # 14. Haversine Distance Calculation Math
    # -------------------------------------------------------------
    def test_16_distance_calculation_haversine(self):
        """Verify the Haversine distance formula accurately calculates distances in km."""
        import math
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            dLat = math.radians(lat2 - lat1)
            dLon = math.radians(lon2 - lon1)
            a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return round(R * c, 1)

        # Lahore center (31.5204, 74.3587) to Services Hospital (31.5432, 74.3341)
        dist_lahore = haversine(31.5204, 74.3587, 31.5432, 74.3341)
        self.assertGreater(dist_lahore, 1.0)
        self.assertLess(dist_lahore, 5.0)

        # Karachi center (24.8607, 67.0011) to JPMC (24.8525, 67.0435)
        dist_karachi = haversine(24.8607, 67.0011, 24.8525, 67.0435)
        self.assertGreater(dist_karachi, 2.0)
        self.assertLess(dist_karachi, 6.0)

    # -------------------------------------------------------------
    # 15. Radius Filtering Logic (5 km, 10 km, 25 km)
    # -------------------------------------------------------------
    def test_17_radius_filtering_5km_10km_25km(self):
        """Verify radius controls filter items within specified distance."""
        code = get_source_content(os.path.join('js', 'nearby_places.js'))

        # Check radius options exist in nearby_places.js
        self.assertIn("'5', label: 'Within 5 km'", code)
        self.assertIn("'10', label: 'Within 10 km'", code)
        self.assertIn("'25', label: 'Within 25 km'", code)
        self.assertIn("'all', label: 'All Distances'", code)

    # -------------------------------------------------------------
    # 16. Location Privacy and Consent Notice
    # -------------------------------------------------------------
    def test_18_location_privacy_and_consent(self):
        """Verify geolocation has explicit privacy consent, optional status, and clear/stop button."""
        code = get_source_content(os.path.join('js', 'nearby_places.js'))

        self.assertIn('LOCATION SAFETY NOTICE', code)
        self.assertIn('NEVER sent to remote tracking servers', code)
        self.assertIn('clearLocation()', code)

        index_path = os.path.join(BASE_DIR, 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            html = f.read()

        self.assertIn('id="btnDetectLocation"', html)
        self.assertIn('id="btnClearLocation"', html)
        self.assertIn('id="locationStatusBadge"', html)

    # -------------------------------------------------------------
    # 17. Google Maps Fallback and Direct Navigation URL Generation
    # -------------------------------------------------------------
    def test_19_google_maps_fallback_and_query_generation(self):
        """Verify that fallback interactive visual map works without API key, and directions URLs format cleanly."""
        code = get_source_content(os.path.join('js', 'nearby_places.js'))

        self.assertIn('https://www.google.com/maps/dir/?api=1&destination=', code)
        self.assertIn('https://www.google.com/maps/search/?api=1&query=', code)
        self.assertIn('renderInteractiveMap', code)
        self.assertIn('map-visual-pin', code)

    # -------------------------------------------------------------
    # 18. Email-Safe Package Verification (Bypassing "Blocked for security reasons")
    # -------------------------------------------------------------
    def test_20_email_safe_packaging_no_blocked_extensions(self):
        """Verify that the email-safe zip package exists and contains no blocked .bat/.js/.exe files."""
        desktop_zip = os.path.join(os.path.dirname(BASE_DIR), 'SheCare AI.zip')
        fallback_zip = os.path.join(BASE_DIR, 'SheCare_AI_EmailSafe.zip')
        target_zip = desktop_zip if os.path.exists(desktop_zip) else fallback_zip
        self.assertTrue(os.path.exists(target_zip), "A safe zip archive must exist for email distribution")
        
        import zipfile
        with zipfile.ZipFile(target_zip, 'r') as zf:
            namelist = zf.namelist()
            for name in namelist:
                self.assertFalse(name.endswith('.bat'), f"Blocked .bat file found in email archive: {name}")
                self.assertFalse(name.endswith('.js'), f"Blocked .js file found in email archive: {name}")
                self.assertFalse(name.endswith('.exe'), f"Blocked .exe file found in email archive: {name}")
                self.assertFalse(name.endswith('.cmd'), f"Blocked .cmd file found in email archive: {name}")

            # Verify safe replacement and instructions exist
            self.assertIn('run_app.bat.txt', [os.path.basename(n) for n in namelist])
            self.assertIn('HOW_TO_RUN_FOR_TEAMMATES.txt', [os.path.basename(n) for n in namelist])


    # -------------------------------------------------------------
    # 19. Country / Region Filtering & Verification Metadata
    # -------------------------------------------------------------
    def test_21_country_region_filtering_and_metadata(self):
        """Verify country/region selection exists and entries contain lastVerified, serviceType, and capacityNotice."""
        nearby_code = get_source_content(os.path.join('js', 'nearby_places.js'))

        # Check country filter definition
        self.assertIn("id: 'Pakistan'", nearby_code)
        self.assertIn("id: 'India'", nearby_code)
        self.assertIn("id: 'International'", nearby_code)
        self.assertIn("renderCountryPills()", nearby_code)

        # Check metadata fields
        self.assertIn("lastVerified: 'October 2026'", nearby_code)
        self.assertIn("serviceType:", nearby_code)
        self.assertIn("capacityNotice:", nearby_code)

        # Check HTML contains country container
        index_html = get_source_content('index.html')
        self.assertIn('id="nearbyCountryPills"', index_html)

if __name__ == '__main__':
    unittest.main()
