with open('app.py', 'r') as f:
    content = f.read()

# 1. Ajoute le champ photo dans le formulaire HTML
old_form = '''            <textarea id="rp_description" data-i18n-ph="describeIssue" placeholder="Describe the issue" rows="3"></textarea>
            <div class="note" data-i18n="keyFeeNote">Note: Lost key/fob replacement fee is $25 CAD.</div>
            <button onclick="submitReport()" data-i18n="submitReport">Submit Report</button>'''
new_form = '''            <textarea id="rp_description" data-i18n-ph="describeIssue" placeholder="Describe the issue" rows="3"></textarea>
            <span class="file-label" data-i18n="issuePhoto">Photo of the issue (optional)</span>
            <input type="file" id="rp_photo" accept="image/*">
            <div class="note" data-i18n="keyFeeNote">Note: Lost key/fob replacement fee is $25 CAD.</div>
            <button type="button" onclick="submitReport()" data-i18n="submitReport">Submit Report</button>'''
content = content.replace(old_form, new_form, 1)

# 2. Ajoute les traductions FR/EN pour le nouveau label
content = content.replace(
    'keyFeeNote: "Note: Lost key/fob replacement fee is $25 CAD.",',
    'keyFeeNote: "Note: Lost key/fob replacement fee is $25 CAD.", issuePhoto: "Photo of the issue (optional)",',
    1
)
content = content.replace(
    'keyFeeNote: "Note : les frais de remplacement de clé/carte sont de 25$ CAD.",',
    'keyFeeNote: "Note : les frais de remplacement de clé/carte sont de 25$ CAD.", issuePhoto: "Photo du problème (optionnel)",',
    1
)

# 3. Change submitReport() pour envoyer un FormData (fichier + texte) au lieu de JSON
old_js = '''        async function submitReport() {
            const payload = {
                name: document.getElementById('rp_name').value,
                address: document.getElementById('rp_address').value,
                contact: document.getElementById('rp_contact').value,
                urgency: document.getElementById('rp_urgency').value,
                description: document.getElementById('rp_description').value
            };
            await fetch('/report', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            alert(I18N[currentLang].reportedOk);
            toggleReport();
        }'''
new_js = '''        async function submitReport() {
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
        }'''
content = content.replace(old_js, new_js, 1)

# 4. Change la route Flask /report pour lire un formulaire multipart au lieu de JSON
old_route = '''@app.route('/report', methods=['POST'])
def report_post():
    data = request.json
    entry = {
        "id": uuid.uuid4().hex,
        "name": data.get("name", ""), "address": data.get("address", ""),
        "contact": data.get("contact", ""), "urgency": data.get("urgency", ""),
        "description": data.get("description", ""), "status": "Open",
        "timestamp": datetime.now().isoformat()
    }'''
new_route = '''@app.route('/report', methods=['POST'])
def report_post():
    data = request.form
    photo_name = save_upload('photo', 'issue')
    entry = {
        "id": uuid.uuid4().hex,
        "name": data.get("name", ""), "address": data.get("address", ""),
        "contact": data.get("contact", ""), "urgency": data.get("urgency", ""),
        "description": data.get("description", ""), "photo": photo_name, "status": "Open",
        "timestamp": datetime.now().isoformat()
    }'''
content = content.replace(old_route, new_route, 1)

# 5. Ajoute la colonne Photo dans le tableau admin
old_admin_header = '<tr><th>Date</th><th>Name</th><th>Address</th><th>Contact</th><th>Urgency</th><th>Description</th><th>Status</th></tr>'
new_admin_header = '<tr><th>Date</th><th>Name</th><th>Address</th><th>Contact</th><th>Urgency</th><th>Description</th><th>Photo</th><th>Status</th></tr>'
content = content.replace(old_admin_header, new_admin_header, 1)

old_admin_row = '''                <td>{{ r.description }}</td>
                <td>
                    <select class="status-select" onchange="updateStatus('{{ r.id }}', this.value)">'''
new_admin_row = '''                <td>{{ r.description }}</td>
                <td>{% if r.photo %}<a class="doc-link" href="/uploads/{{ r.photo }}" target="_blank">View</a>{% endif %}</td>
                <td>
                    <select class="status-select" onchange="updateStatus('{{ r.id }}', this.value)">'''
content = content.replace(old_admin_row, new_admin_row, 1)

with open('app.py', 'w') as f:
    f.write(content)

print("Report photo patch applied successfully.")