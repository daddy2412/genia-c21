from flask import Flask, request, jsonify, render_template_string, send_from_directory, Response
from functools import wraps
from anthropic import Anthropic
import os
import random
import json
import csv
import io
import uuid
import base64
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from werkzeug.utils import secure_filename
from buildings_data import BUILDINGS_INFO

app = Flask(__name__)
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

MOCK_MODE = True

WAITLIST_FILE = "waitlist.json"
REPORTS_FILE = "reports.json"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Century21")

SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "daddymundele24@gmail.com")

LOGO_B64 = "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"

def send_notification(subject, body):
    if not SMTP_USER or not SMTP_PASS:
        print(f"[EMAIL SKIPPED - no SMTP config] {subject}")
        return
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = NOTIFY_EMAIL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, NOTIFY_EMAIL, msg.as_string())
        print(f"[EMAIL SENT] {subject}")
    except Exception as e:
        print(f"[EMAIL FAILED] {e}")

def check_auth(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def authenticate():
    return Response(
        'Authentication required to access the admin dashboard.',
        401,
        {'WWW-Authenticate': 'Basic realm="Admin Area"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

SYSTEM_PROMPT_BASE = f"""You are the virtual assistant for Century 21 Gold Key Realty Ltd.,
a real estate agency based in Steinbach, Manitoba, serving Steinbach, La Broquerie,
St. Pierre Jolys, Blumenort, and Mitchell.

Your role:
1. Help prospective tenants find an available rental (by city, bedrooms, budget)
2. If nothing matches, offer to add them to the waiting list
3. Help current tenants troubleshoot simple issues before calling
4. Answer general rental questions and policies

Tone: professional, warm, efficient.

Current available listings:
1. 209-530 Wilson, Steinbach, MB - $1,045/mo - 1 bed, 1 bath - Pet Friendly - Available Oct 1, 2026
2. 366 Main St (3bdrm), Steinbach, MB - $1,850/mo starting - 3 bed, 2 bath - 1114 sqft
3. 366 Main St (2bdrm), Steinbach, MB - $1,535/mo - 2 bed, 2 bath - 993 sqft
4. 116 Imperial, Steinbach, MB - $1,750/mo - 3 bed, 1 bath - 1254 sqft - Available immediately
5. 21 Parkhill, Steinbach, MB - $1,850/mo - 4 bed, 3 bath - Available Nov 1, 2026
6. 9 Rachel Lane, La Broquerie, MB - $2,200/mo - 3 bed, 1 bath - Utilities/snow/lawn included
7. 208-353 Sabourin, St. Pierre Jolys, MB - $995/mo - 1 bed - 625 sqft
8. 16-72 Crestview, Blumenort, MB - $1,350/mo - 2 bed, 2 bath - 980 sqft - Pet Friendly
9. 307-73 Essex, Steinbach, MB - $1,475/mo - 3 bed, 2 bath - 1058 sqft - Available Nov 1, 2026
10. 530 Wilson (2bed), Steinbach, MB - $1,445/mo - 2 bed, 2 bath - Pet Friendly - Available Oct 1
11. 203-353 Sabourin, St. Pierre Jolys, MB - $1,295/mo - 2 bed, 2 bath - 825 sqft - Pet Friendly
12. 30 Primrose, Mitchell, MB - $1,295/mo - 2 bed, 1 bath - Pet Friendly
13. 1-196 Chapel, Steinbach, MB - $1,295/mo - 3 bed, 1 bath - 999 sqft
14. 310-353 Sabourin, St. Pierre Jolys, MB - $1,300/mo - 2 bed, 1 bath - 825 sqft - Pet Friendly
15. 205-63 Essex, Steinbach, MB - $1,295/mo - 2 bed, 1 bath - 844 sqft - Available Oct 1
16. 14 Country Lane, Blumenort, MB - $2,350/mo - 5 bed, 2 bath
17. 103-63 Essex, Steinbach, MB - $1,295/mo - 2 bed, 1 bath - Available immediately

{BUILDINGS_INFO}

Rental policies:
- Lost key/fob replacement fee: $25 CAD.

Out of scope: price negotiation, lease terms (redirect to human agent), serious
emergencies like fire or major water damage (give phone: 204-326-4459 immediately).

If you don't know something, offer phone (204-326-4459) or email (rentals@goldkey21.com).
Never invent property info."""

MOCK_RESPONSES = {
    "en": [
        "Thanks for reaching out! Based on our current listings, we have a 2-bedroom apartment at 530 Wilson in Steinbach for $1,445/mo, pet-friendly, available October 1st. Would you like more details or to schedule a viewing?",
        "I understand you're having a power outage. Could you tell me which building/address you're in? I can guide you to your electrical panel.",
        "That property is currently fully rented, but I'd be happy to add you to our waiting list! Could you share your name and phone number or email?",
    ],
    "fr": [
        "Merci de nous contacter! Selon nos annonces actuelles, nous avons un 2 chambres au 530 Wilson à Steinbach pour 1 445$/mois, animaux acceptés, disponible le 1er octobre. Voulez-vous plus de détails ou planifier une visite?",
        "Je comprends que vous avez une panne de courant. Pouvez-vous me dire dans quel immeuble/adresse vous êtes? Je peux vous guider vers votre panneau électrique.",
        "Ce logement est actuellement loué, mais je peux vous ajouter à notre liste d'attente! Pouvez-vous partager votre nom et votre numéro de téléphone ou courriel?",
    ]
}

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Century 21 Gold Key Assistant</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#a6192e">
    <link rel="apple-touch-icon" href="/icon.jpg">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="C21 Gold Key">
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, 'Segoe UI', Arial, sans-serif; max-width: 640px; margin: 0 auto; padding: 0; background: #f5f5f5; }
        .header { background: #a6192e; color: white; padding: 20px; text-align: center; position: relative; }
        .logo {
            width: 56px; height: 56px; border-radius: 8px; margin-bottom: 8px;
            animation: logoPulse 2.5s ease-in-out infinite;
        }
        @keyframes logoPulse {
            0%, 100% { transform: scale(1) rotate(0deg); }
            50% { transform: scale(1.08) rotate(8deg); }
        }
        .header h2 { margin: 0; font-size: 1.4em; }
        .header p { margin: 5px 0 0; font-size: 0.85em; opacity: 0.9; }
        .header a { color: white; font-size: 0.75em; opacity: 0.8; }
        .lang-switch { position: absolute; top: 15px; right: 15px; font-size: 0.85em; }
        .lang-switch button { background: none; border: 1px solid rgba(255,255,255,0.5); color: white; padding: 3px 8px; border-radius: 4px; cursor: pointer; font-size: 0.9em; font-weight: normal; }
        .lang-switch button.active { background: white; color: #a6192e; font-weight: bold; }
        .container { padding: 15px; }
        #chat { background: white; border-radius: 10px; height: 350px; overflow-y: auto; padding: 15px; margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
        .user { text-align: right; margin: 10px 0; }
        .user span { background: #a6192e; color: white; padding: 8px 14px; border-radius: 14px 14px 2px 14px; display: inline-block; max-width: 80%; text-align: left; }
        .bot { text-align: left; margin: 10px 0; }
        .bot span { background: #eee; color: #222; padding: 8px 14px; border-radius: 14px 14px 14px 2px; display: inline-block; max-width: 80%; }
        .input-row { display: flex; gap: 8px; }
        input, select, textarea { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 8px; font-size: 1em; font-family: inherit; }
        button { padding: 12px 20px; background: #a6192e; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
        button:hover { background: #8a1526; }
        .action-buttons { display: flex; gap: 8px; margin-bottom: 10px; }
        .waitlist-btn, .report-btn { font-size: 0.85em; padding: 8px 14px; flex: 1; }
        .waitlist-btn { background: #555; }
        .report-btn { background: #cc6600; }
        #waitlistForm, #reportForm { display: none; background: white; padding: 15px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); max-height: 500px; overflow-y: auto; }
        #waitlistForm input, #waitlistForm select, #waitlistForm textarea,
        #reportForm input, #reportForm select, #reportForm textarea { margin-bottom: 8px; width: 100%; }
        .form-row { display: flex; gap: 8px; }
        .form-row input, .form-row select { flex: 1; }
        .form-label { font-size: 0.8em; color: #666; margin-bottom: 2px; margin-top: 10px; font-weight: bold; text-transform: uppercase; }
        .note { font-size: 0.75em; color: #888; margin-top: -4px; margin-bottom: 6px; }
        .file-label { font-size: 0.8em; color: #444; margin-bottom: 3px; display: block; }
    </style>
</head>
<body>
    <div class="header">
        <div class="lang-switch">
            <button id="btnEN" onclick="setLang('en')">EN</button>
            <button id="btnFR" onclick="setLang('fr')">FR</button>
        </div>
        <img class="logo" src="data:image/jpeg;base64,LOGO_PLACEHOLDER" alt="Century 21">
        <h2 data-i18n="title">Century 21 Gold Key Realty</h2>
        <p data-i18n="subtitle">Virtual Assistant - Steinbach, MB</p>
        <p><a href="/admin">Admin Dashboard</a></p>
    </div>
    <div class="container">
        <div class="action-buttons">
            <button class="waitlist-btn" onclick="toggleWaitlist()" data-i18n="joinWaitlist">+ Join Waiting List</button>
            <button class="report-btn" onclick="toggleReport()" data-i18n="reportIssue">Report an Issue</button>
        </div>

        <form id="waitlistForm" onsubmit="return false;">
            <div class="form-label" data-i18n="contactInfo">Contact Info</div>
            <input type="text" id="wl_name" data-i18n-ph="fullName" placeholder="Full name">
            <input type="text" id="wl_contact" data-i18n-ph="phoneEmail" placeholder="Phone or email">

            <div class="form-label" data-i18n="rentalPrefs">Rental Preferences</div>
            <select id="wl_city">
                <option value="" data-i18n="selectCity">Select preferred city</option>
                <option value="Steinbach">Steinbach</option>
                <option value="La Broquerie">La Broquerie</option>
                <option value="St. Pierre Jolys">St. Pierre Jolys</option>
                <option value="Blumenort">Blumenort</option>
                <option value="Mitchell">Mitchell</option>
                <option value="Other" data-i18n="otherNoPref">Other / No preference</option>
            </select>
            <input type="text" id="wl_bedrooms" data-i18n-ph="bedroomsWanted" placeholder="Bedrooms wanted">
            <input type="text" id="wl_budget" data-i18n-ph="budget" placeholder="Budget (max $/month)">
            <span class="file-label" data-i18n="moveInDate">Desired move-in date</span>
            <input type="date" id="wl_movein">

            <div class="form-label" data-i18n="household">Household Composition</div>
            <div class="form-row">
                <input type="number" id="wl_adults" data-i18n-ph="adults" placeholder="Adults" min="0">
                <input type="number" id="wl_children" data-i18n-ph="childrenU5" placeholder="Children under 5" min="0">
            </div>
            <div class="form-row">
                <select id="wl_pets">
                    <option value="No" data-i18n="noPets">No pets</option>
                    <option value="Yes - cat(s)" data-i18n="yesCats">Yes - cat(s)</option>
                    <option value="Yes - dog(s)" data-i18n="yesDogs">Yes - dog(s)</option>
                    <option value="Yes - other" data-i18n="yesOtherPet">Yes - other pet(s)</option>
                </select>
                <select id="wl_smoker">
                    <option value="No" data-i18n="nonSmoker">Non-smoker</option>
                    <option value="Yes" data-i18n="smoker">Smoker</option>
                </select>
            </div>

            <div class="form-label" data-i18n="vehicle">Vehicle</div>
            <select id="wl_has_vehicle">
                <option value="No" data-i18n="noVehicle">No vehicle</option>
                <option value="Yes" data-i18n="yesVehicle">Yes, I have a vehicle</option>
            </select>
            <div class="form-row">
                <input type="text" id="wl_vehicle_model" data-i18n-ph="makeModel" placeholder="Make / model (e.g. Honda Civic)">
                <input type="text" id="wl_vehicle_year" data-i18n-ph="year" placeholder="Year (e.g. 2021)">
            </div>

            <div class="form-label" data-i18n="employment">Employment &amp; Income</div>
            <select id="wl_employment">
                <option value="Full-time" data-i18n="fullTime">Employed - Full-time</option>
                <option value="Part-time" data-i18n="partTime">Employed - Part-time</option>
                <option value="Self-employed" data-i18n="selfEmployed">Self-employed</option>
                <option value="Student" data-i18n="student">Student</option>
                <option value="Other" data-i18n="other">Other</option>
            </select>
            <input type="text" id="wl_employer" data-i18n-ph="employerName" placeholder="Employer name">
            <input type="text" id="wl_income" data-i18n-ph="monthlyIncome" placeholder="Monthly income ($)">

            <div class="form-label" data-i18n="references">References</div>
            <div class="form-row">
                <input type="text" id="wl_landlord_name" data-i18n-ph="prevLandlordName" placeholder="Previous landlord - name">
                <input type="text" id="wl_landlord_contact" data-i18n-ph="prevLandlordContact" placeholder="Previous landlord - phone/email">
            </div>
            <div class="form-row">
                <input type="text" id="wl_personalref_name" data-i18n-ph="personalRefName" placeholder="Personal reference - name">
                <input type="text" id="wl_personalref_contact" data-i18n-ph="personalRefContact" placeholder="Personal reference - phone/email">
            </div>

            <div class="form-label" data-i18n="reasonMoving">Reason for Moving</div>
            <select id="wl_reason">
                <option value="Need more space" data-i18n="needSpace">Need more space</option>
                <option value="Downsizing" data-i18n="downsizing">Downsizing</option>
                <option value="Job relocation" data-i18n="jobReloc">Job relocation</option>
                <option value="Closer to work/school" data-i18n="closerWork">Closer to work/school</option>
                <option value="End of current lease" data-i18n="endLease">End of current lease</option>
                <option value="Other" data-i18n="other">Other</option>
            </select>

            <div class="form-label" data-i18n="documents">Documents (optional)</div>
            <span class="file-label" data-i18n="photoId">Photo ID</span>
            <input type="file" id="wl_id_doc">
            <span class="file-label" data-i18n="proofIncome">Proof of income</span>
            <input type="file" id="wl_income_doc">

            <button type="button" onclick="submitWaitlist()" data-i18n="submit">Submit</button>
        </form>

        <div id="reportForm">
            <input type="text" id="rp_name" data-i18n-ph="fullName" placeholder="Full name">
            <input type="text" id="rp_address" data-i18n-ph="buildingAddress" placeholder="Building address / unit number">
            <input type="text" id="rp_contact" data-i18n-ph="phoneEmail" placeholder="Phone or email">
            <select id="rp_urgency">
                <option value="Low" data-i18n="low">Low - can wait a few days</option>
                <option value="Medium" data-i18n="medium">Medium - needs attention soon</option>
                <option value="High" data-i18n="high">High - urgent, needs quick response</option>
                <option value="Emergency" data-i18n="emergency">Emergency - fire, flood, gas smell (call 204-326-4459 directly!)</option>
            </select>
            <textarea id="rp_description" data-i18n-ph="describeIssue" placeholder="Describe the issue" rows="3"></textarea>
            <span class="file-label" data-i18n="issuePhoto">Photo of the issue (optional)</span>
            <input type="file" id="rp_photo" accept="image/*">
            <div class="note" data-i18n="keyFeeNote">Note: Lost key/fob replacement fee is $25 CAD.</div>
            <button type="button" onclick="submitReport()" data-i18n="submitReport">Submit Report</button>
        </div>

        <div id="chat"></div>
        <div class="input-row">
            <input type="text" id="msg" data-i18n-ph="askPlaceholder" placeholder="Ask about apartments, report an issue..." onkeypress="if(event.key==='Enter') send()">
            <button onclick="send()" data-i18n="send">Send</button>
        </div>
    </div>

    <script>
        let history = [];
        let currentLang = 'en';

        const I18N = {
            en: {
                title: "Century 21 Gold Key Realty", subtitle: "Virtual Assistant - Steinbach, MB",
                joinWaitlist: "+ Join Waiting List", reportIssue: "Report an Issue",
                contactInfo: "Contact Info", fullName: "Full name", phoneEmail: "Phone or email",
                rentalPrefs: "Rental Preferences", selectCity: "Select preferred city", otherNoPref: "Other / No preference",
                bedroomsWanted: "Bedrooms wanted", budget: "Budget (max $/month)", moveInDate: "Desired move-in date",
                household: "Household Composition", adults: "Adults", childrenU5: "Children under 5",
                noPets: "No pets", yesCats: "Yes - cat(s)", yesDogs: "Yes - dog(s)", yesOtherPet: "Yes - other pet(s)",
                nonSmoker: "Non-smoker", smoker: "Smoker", vehicle: "Vehicle",
                noVehicle: "No vehicle", yesVehicle: "Yes, I have a vehicle",
                makeModel: "Make / model (e.g. Honda Civic)", year: "Year (e.g. 2021)",
                employment: "Employment & Income", fullTime: "Employed - Full-time", partTime: "Employed - Part-time",
                selfEmployed: "Self-employed", student: "Student", other: "Other",
                employerName: "Employer name", monthlyIncome: "Monthly income ($)",
                references: "References", prevLandlordName: "Previous landlord - name",
                prevLandlordContact: "Previous landlord - phone/email",
                personalRefName: "Personal reference - name", personalRefContact: "Personal reference - phone/email",
                reasonMoving: "Reason for Moving", needSpace: "Need more space", downsizing: "Downsizing",
                jobReloc: "Job relocation", closerWork: "Closer to work/school", endLease: "End of current lease",
                documents: "Documents (optional)", photoId: "Photo ID", proofIncome: "Proof of income",
                submit: "Submit", buildingAddress: "Building address / unit number",
                low: "Low - can wait a few days", medium: "Medium - needs attention soon",
                high: "High - urgent, needs quick response",
                emergency: "Emergency - fire, flood, gas smell (call 204-326-4459 directly!)",
                describeIssue: "Describe the issue (e.g. power outage, leak, lost key)",
                keyFeeNote: "Note: Lost key/fob replacement fee is $25 CAD.", issuePhoto: "Photo of the issue (optional)",
                submitReport: "Submit Report", askPlaceholder: "Ask about apartments, report an issue...",
                send: "Send", addedWaitlist: "You have been added to the waiting list!",
                reportedOk: "Your issue has been reported. Our team will follow up soon. For emergencies, please call 204-326-4459 directly.",
                you: "You", assistant: "Assistant"
            },
            fr: {
                title: "Century 21 Gold Key Realty", subtitle: "Assistant virtuel - Steinbach, MB",
                joinWaitlist: "+ Liste d'attente", reportIssue: "Signaler un problème",
                contactInfo: "Coordonnées", fullName: "Nom complet", phoneEmail: "Téléphone ou courriel",
                rentalPrefs: "Préférences de location", selectCity: "Choisir une ville", otherNoPref: "Autre / Aucune préférence",
                bedroomsWanted: "Nombre de chambres souhaité", budget: "Budget (max $/mois)", moveInDate: "Date d'emménagement souhaitée",
                household: "Composition du ménage", adults: "Adultes", childrenU5: "Enfants de moins de 5 ans",
                noPets: "Aucun animal", yesCats: "Oui - chat(s)", yesDogs: "Oui - chien(s)", yesOtherPet: "Oui - autre animal",
                nonSmoker: "Non-fumeur", smoker: "Fumeur", vehicle: "Véhicule",
                noVehicle: "Aucun véhicule", yesVehicle: "Oui, j'ai un véhicule",
                makeModel: "Marque / modèle (ex. Honda Civic)", year: "Année (ex. 2021)",
                employment: "Emploi et revenu", fullTime: "Emploi - Temps plein", partTime: "Emploi - Temps partiel",
                selfEmployed: "Travailleur autonome", student: "Étudiant", other: "Autre",
                employerName: "Nom de l'employeur", monthlyIncome: "Revenu mensuel ($)",
                references: "Références", prevLandlordName: "Ancien propriétaire - nom",
                prevLandlordContact: "Ancien propriétaire - téléphone/courriel",
                personalRefName: "Référence personnelle - nom", personalRefContact: "Référence personnelle - téléphone/courriel",
                reasonMoving: "Raison du déménagement", needSpace: "Besoin de plus d'espace", downsizing: "Réduction d'espace",
                jobReloc: "Relocalisation d'emploi", closerWork: "Plus proche du travail/école", endLease: "Fin du bail actuel",
                documents: "Documents (optionnel)", photoId: "Pièce d'identité", proofIncome: "Preuve de revenu",
                submit: "Soumettre", buildingAddress: "Adresse de l'immeuble / numéro d'unité",
                low: "Faible - peut attendre quelques jours", medium: "Moyen - nécessite une attention prochaine",
                high: "Élevé - urgent, réponse rapide requise",
                emergency: "Urgence - feu, inondation, odeur de gaz (appelez le 204-326-4459 directement!)",
                describeIssue: "Décrivez le problème (ex. panne de courant, fuite, clé perdue)",
                keyFeeNote: "Note : les frais de remplacement de clé/carte sont de 25$ CAD.", issuePhoto: "Photo du problème (optionnel)",
                submitReport: "Signaler", askPlaceholder: "Posez une question, signalez un problème...",
                send: "Envoyer", addedWaitlist: "Vous avez été ajouté à la liste d'attente!",
                reportedOk: "Votre problème a été signalé. Notre équipe vous contactera bientôt. Pour une urgence, appelez le 204-326-4459 directement.",
                you: "Vous", assistant: "Assistant"
            }
        };

        function applyLang(lang) {
            currentLang = lang;
            document.getElementById('btnEN').classList.toggle('active', lang === 'en');
            document.getElementById('btnFR').classList.toggle('active', lang === 'fr');
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (I18N[lang][key]) el.textContent = I18N[lang][key];
            });
            document.querySelectorAll('[data-i18n-ph]').forEach(el => {
                const key = el.getAttribute('data-i18n-ph');
                if (I18N[lang][key]) el.placeholder = I18N[lang][key];
            });
        }

        function setLang(lang) { applyLang(lang); }
        applyLang('en');

        function toggleWaitlist() {
            const form = document.getElementById('waitlistForm');
            document.getElementById('reportForm').style.display = 'none';
            form.style.display = form.style.display === 'none' ? 'block' : 'none';
        }

        function toggleReport() {
            const form = document.getElementById('reportForm');
            document.getElementById('waitlistForm').style.display = 'none';
            form.style.display = form.style.display === 'none' ? 'block' : 'none';
        }

        async function submitWaitlist() {
            const fd = new FormData();
            fd.append('name', document.getElementById('wl_name').value);
            fd.append('contact', document.getElementById('wl_contact').value);
            fd.append('city', document.getElementById('wl_city').value);
            fd.append('bedrooms', document.getElementById('wl_bedrooms').value);
            fd.append('budget', document.getElementById('wl_budget').value);
            fd.append('move_in_date', document.getElementById('wl_movein').value);
            fd.append('adults', document.getElementById('wl_adults').value);
            fd.append('children_under_5', document.getElementById('wl_children').value);
            fd.append('pets', document.getElementById('wl_pets').value);
            fd.append('smoker', document.getElementById('wl_smoker').value);
            fd.append('has_vehicle', document.getElementById('wl_has_vehicle').value);
            fd.append('vehicle_model', document.getElementById('wl_vehicle_model').value);
            fd.append('vehicle_year', document.getElementById('wl_vehicle_year').value);
            fd.append('employment', document.getElementById('wl_employment').value);
            fd.append('employer', document.getElementById('wl_employer').value);
            fd.append('income', document.getElementById('wl_income').value);
            fd.append('landlord_name', document.getElementById('wl_landlord_name').value);
            fd.append('landlord_contact', document.getElementById('wl_landlord_contact').value);
            fd.append('personalref_name', document.getElementById('wl_personalref_name').value);
            fd.append('personalref_contact', document.getElementById('wl_personalref_contact').value);
            fd.append('reason', document.getElementById('wl_reason').value);

            const idDoc = document.getElementById('wl_id_doc').files[0];
            const incomeDoc = document.getElementById('wl_income_doc').files[0];
            if (idDoc) fd.append('id_doc', idDoc);
            if (incomeDoc) fd.append('income_doc', incomeDoc);

            await fetch('/waitlist', { method: 'POST', body: fd });
            alert(I18N[currentLang].addedWaitlist);
            toggleWaitlist();
        }

        async function submitReport() {
            const fd = new FormData();
            fd.append('name', document.getElementById('rp_name').value);
            fd.append('address', document.getElementById('rp_address').value);
            fd.append('contact', document.getElementById('rp_contact').value);
            fd.append('urgency', document.getElementById('rp_urgency').value);
            fd.append('description', document.getElementById('rp_description').value);
            const photo = document.getElementById('rp_photo').files[0];
            if (photo) fd.append('photo', photo);
            await fetch('/report', { method: 'POST', body: fd });
            alert(I18N[currentLang].reportedOk);
            toggleReport();
        }

        async function send() {
            const input = document.getElementById('msg');
            const chat = document.getElementById('chat');
            const text = input.value.trim();
            if (!text) return;
            chat.innerHTML += `<div class="user"><span><b>${I18N[currentLang].you}:</b> ${text}</span></div>`;
            input.value = '';
            history.push({role: "user", content: text});
            chat.scrollTop = chat.scrollHeight;

            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({messages: history, lang: currentLang})
            });
            const data = await res.json();
            chat.innerHTML += `<div class="bot"><span><b>${I18N[currentLang].assistant}:</b> ${data.reply}</span></div>`;
            history.push({role: "assistant", content: data.reply});
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
""".replace("LOGO_PLACEHOLDER", LOGO_B64)

ADMIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard - Century 21 Gold Key</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, 'Segoe UI', Arial, sans-serif; max-width: 1500px; margin: 0 auto; padding: 0; background: #f5f5f5; }
        .header { background: #a6192e; color: white; padding: 20px; text-align: center; }
        .header h2 { margin: 0; }
        .header a { color: white; font-size: 0.85em; margin: 0 8px; }
        .section { padding: 20px; overflow-x: auto; }
        .section h3 { border-bottom: 2px solid #a6192e; padding-bottom: 8px; }
        .export-btn { display: inline-block; background: #2e7d32; color: white; padding: 6px 14px; border-radius: 6px; font-size: 0.8em; text-decoration: none; margin-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 1px 4px rgba(0,0,0,0.1); margin-bottom: 30px; }
        th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; font-size: 0.85em; white-space: nowrap; }
        th { background: #333; color: white; }
        tr:hover { background: #f9f9f9; }
        .badge { padding: 3px 10px; border-radius: 12px; font-size: 0.8em; font-weight: bold; color: white; }
        .badge-Emergency { background: #cc0000; }
        .badge-High { background: #e67300; }
        .badge-Medium { background: #d4a017; }
        .badge-Low { background: #888; }
        .badge-yes { background: #a6192e; }
        .badge-no { background: #999; }
        .status-select { padding: 4px 8px; border-radius: 6px; font-size: 0.8em; border: 1px solid #ccc; }
        .empty { padding: 20px; text-align: center; color: #999; font-style: italic; }
        a.doc-link { color: #a6192e; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h2>Admin Dashboard</h2>
        <a href="/">← Back to Assistant</a>
    </div>
    <div class="section">
        <h3>🔧 Reported Issues ({{ reports|length }})</h3>
        <a class="export-btn" href="/export/reports">⬇ Export CSV</a>
        {% if reports %}
        <table>
            <tr><th>Date</th><th>Name</th><th>Address</th><th>Contact</th><th>Urgency</th><th>Description</th><th>Photo</th><th>Status</th></tr>
            {% for r in reports|reverse %}
            <tr>
                <td>{{ r.timestamp[:16] }}</td>
                <td>{{ r.name }}</td>
                <td>{{ r.address }}</td>
                <td>{{ r.contact }}</td>
                <td><span class="badge badge-{{ r.urgency }}">{{ r.urgency }}</span></td>
                <td>{{ r.description }}</td>
                <td>{% if r.photo %}<a class="doc-link" href="/uploads/{{ r.photo }}" target="_blank">View</a>{% endif %}</td>
                <td>
                    <select class="status-select" onchange="updateStatus('{{ r.id }}', this.value)">
                        <option value="Open" {% if r.status == 'Open' %}selected{% endif %}>Open</option>
                        <option value="In Progress" {% if r.status == 'In Progress' %}selected{% endif %}>In Progress</option>
                        <option value="Resolved" {% if r.status == 'Resolved' %}selected{% endif %}>Resolved</option>
                    </select>
                </td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <div class="empty">No issues reported yet.</div>
        {% endif %}

        <h3>📋 Waiting List ({{ waitlist|length }})</h3>
        <a class="export-btn" href="/export/waitlist">⬇ Export CSV</a>
        {% if waitlist %}
        <table>
            <tr>
                <th>Date</th><th>Name</th><th>Contact</th><th>City</th><th>Bed</th><th>Budget</th>
                <th>Move-in</th><th>Adults</th><th>Kids&lt;5</th><th>Pets</th><th>Smoker</th>
                <th>Vehicle</th><th>Model</th><th>Year</th><th>Employment</th><th>Employer</th>
                <th>Income</th><th>Prev. Landlord</th><th>Personal Ref</th><th>Reason</th><th>Docs</th>
            </tr>
            {% for w in waitlist|reverse %}
            <tr>
                <td>{{ w.timestamp[:16] }}</td>
                <td>{{ w.name }}</td>
                <td>{{ w.contact }}</td>
                <td>{{ w.city }}</td>
                <td>{{ w.bedrooms }}</td>
                <td>{{ w.budget }}</td>
                <td>{{ w.move_in_date }}</td>
                <td>{{ w.adults }}</td>
                <td>{{ w.children_under_5 }}</td>
                <td>{{ w.pets }}</td>
                <td><span class="badge badge-{{ 'yes' if w.smoker == 'Yes' else 'no' }}">{{ w.smoker }}</span></td>
                <td>{{ w.has_vehicle }}</td>
                <td>{{ w.vehicle_model }}</td>
                <td>{{ w.vehicle_year }}</td>
                <td>{{ w.employment }}</td>
                <td>{{ w.employer }}</td>
                <td>{{ w.income }}</td>
                <td>{{ w.landlord_name }} ({{ w.landlord_contact }})</td>
                <td>{{ w.personalref_name }} ({{ w.personalref_contact }})</td>
                <td>{{ w.reason }}</td>
                <td>
                    {% if w.id_doc %}<a class="doc-link" href="/uploads/{{ w.id_doc }}" target="_blank">ID</a>{% endif %}
                    {% if w.income_doc %} | <a class="doc-link" href="/uploads/{{ w.income_doc }}" target="_blank">Income</a>{% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <div class="empty">No one on the waiting list yet.</div>
        {% endif %}
    </div>
    <script>
        async function updateStatus(id, newStatus) {
            await fetch('/report/status', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: id, status: newStatus})
            });
            location.reload();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/admin')
@requires_auth
def admin():
    waitlist = []
    reports = []
    if os.path.exists(WAITLIST_FILE):
        with open(WAITLIST_FILE, "r") as f:
            waitlist = json.load(f)
    if os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, "r") as f:
            reports = json.load(f)
    return render_template_string(ADMIN_PAGE, waitlist=waitlist, reports=reports)

@app.route('/uploads/<path:filename>')
@requires_auth
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/export/waitlist')
@requires_auth
def export_waitlist():
    waitlist = []
    if os.path.exists(WAITLIST_FILE):
        with open(WAITLIST_FILE, "r") as f:
            waitlist = json.load(f)
    output = io.StringIO()
    if waitlist:
        writer = csv.DictWriter(output, fieldnames=waitlist[0].keys())
        writer.writeheader()
        writer.writerows(waitlist)
    return Response(output.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=waitlist.csv"})

@app.route('/export/reports')
@requires_auth
def export_reports():
    reports = []
    if os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, "r") as f:
            reports = json.load(f)
    output = io.StringIO()
    if reports:
        writer = csv.DictWriter(output, fieldnames=reports[0].keys())
        writer.writeheader()
        writer.writerows(reports)
    return Response(output.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=reports.csv"})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    lang = data.get('lang', 'en')

    if MOCK_MODE:
        reply = random.choice(MOCK_RESPONSES.get(lang, MOCK_RESPONSES["en"]))
        prefix = "[MODE TEST]" if lang == "en" else "[MODE TEST]"
        return jsonify({"reply": f"{prefix} {reply}"})

    lang_instruction = "Respond in French." if lang == "fr" else "Respond in English."
    system_prompt = f"{SYSTEM_PROMPT_BASE}\n\n{lang_instruction}"

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=500,
        system=system_prompt,
        messages=messages
    )
    return jsonify({"reply": response.content[0].text})

def save_upload(file_key, prefix):
    file = request.files.get(file_key)
    if file and file.filename:
        safe_name = secure_filename(file.filename)
        stored_name = f"{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_name}"
        file.save(os.path.join(UPLOAD_FOLDER, stored_name))
        return stored_name
    return ""

@app.route('/waitlist', methods=['POST'])
def waitlist_post():
    form = request.form
    id_doc_name = save_upload('id_doc', 'id')
    income_doc_name = save_upload('income_doc', 'income')

    entry = {
        "id": uuid.uuid4().hex,
        "name": form.get("name", ""), "contact": form.get("contact", ""),
        "city": form.get("city", ""), "bedrooms": form.get("bedrooms", ""),
        "budget": form.get("budget", ""), "move_in_date": form.get("move_in_date", ""),
        "adults": form.get("adults", ""), "children_under_5": form.get("children_under_5", ""),
        "pets": form.get("pets", ""), "smoker": form.get("smoker", ""),
        "has_vehicle": form.get("has_vehicle", ""), "vehicle_model": form.get("vehicle_model", ""),
        "vehicle_year": form.get("vehicle_year", ""), "employment": form.get("employment", ""),
        "employer": form.get("employer", ""), "income": form.get("income", ""),
        "landlord_name": form.get("landlord_name", ""), "landlord_contact": form.get("landlord_contact", ""),
        "personalref_name": form.get("personalref_name", ""), "personalref_contact": form.get("personalref_contact", ""),
        "reason": form.get("reason", ""), "id_doc": id_doc_name, "income_doc": income_doc_name,
        "timestamp": datetime.now().isoformat()
    }

    entries = []
    if os.path.exists(WAITLIST_FILE):
        with open(WAITLIST_FILE, "r") as f:
            entries = json.load(f)
    entries.append(entry)
    with open(WAITLIST_FILE, "w") as f:
        json.dump(entries, f, indent=2)

    send_notification(f"New waiting list entry: {entry['name']}",
        f"Name: {entry['name']}\nContact: {entry['contact']}\nCity: {entry['city']}\n"
        f"Bedrooms: {entry['bedrooms']}\nBudget: {entry['budget']}\nMove-in: {entry['move_in_date']}")

    return jsonify({"status": "added", "entry": entry})

@app.route('/report', methods=['POST'])
def report_post():
    data = request.form
    photo_name = save_upload('photo', 'issue')
    entry = {
        "id": uuid.uuid4().hex,
        "name": data.get("name", ""), "address": data.get("address", ""),
        "contact": data.get("contact", ""), "urgency": data.get("urgency", ""),
        "description": data.get("description", ""), "photo": photo_name, "status": "Open",
        "timestamp": datetime.now().isoformat()
    }
    entries = []
    if os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, "r") as f:
            entries = json.load(f)
    entries.append(entry)
    with open(REPORTS_FILE, "w") as f:
        json.dump(entries, f, indent=2)

    send_notification(f"New issue reported: {entry['urgency']} - {entry['address']}",
        f"Name: {entry['name']}\nAddress: {entry['address']}\nContact: {entry['contact']}\n"
        f"Urgency: {entry['urgency']}\nDescription: {entry['description']}")

    return jsonify({"status": "reported", "entry": entry})

@app.route('/report/status', methods=['POST'])
@requires_auth
def update_report_status():
    data = request.json
    report_id = data.get("id")
    new_status = data.get("status")
    entries = []
    if os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, "r") as f:
            entries = json.load(f)
    for entry in entries:
        if entry.get("id") == report_id:
            entry["status"] = new_status
            break
    with open(REPORTS_FILE, "w") as f:
        json.dump(entries, f, indent=2)
    return jsonify({"status": "updated"})


@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "Century 21 Gold Key Realty Assistant",
        "short_name": "C21 Gold Key",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#f5f5f5",
        "theme_color": "#a6192e",
        "icons": [{"src": "/icon.jpg", "sizes": "200x200", "type": "image/jpeg"}]
    })

@app.route('/sw.js')
def service_worker():
    sw_code = """
const CACHE_NAME = 'c21-assistant-v1';
self.addEventListener('install', (e) => { self.skipWaiting(); });
self.addEventListener('activate', (e) => { self.clients.claim(); });
self.addEventListener('fetch', (e) => {
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
"""
    return Response(sw_code, mimetype='application/javascript')

@app.route('/icon.jpg')
def app_icon():
    return Response(base64.b64decode(LOGO_B64), mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)