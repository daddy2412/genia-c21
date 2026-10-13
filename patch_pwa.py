import re

with open('app.py', 'r') as f:
    content = f.read()

if 'import base64' not in content:
    content = content.replace('import uuid\n', 'import uuid\nimport base64\n', 1)

anchor = '<meta name="viewport" content="width=device-width, initial-scale=1">'
pwa_head = anchor + '''
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#a6192e">
    <link rel="apple-touch-icon" href="/icon.jpg">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="C21 Gold Key">'''
content = content.replace(anchor, pwa_head, 1)

old_close = '    </script>\n</body>\n</html>\n"""\n\nADMIN_PAGE'
sw_register = '''
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js').catch(()=>{});
            });
        }
    </script>
</body>
</html>
"""

ADMIN_PAGE'''
content = content.replace(old_close, sw_register, 1)

new_routes = '''
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

'''
content = content.replace("if __name__ == '__main__':", new_routes + "if __name__ == '__main__':", 1)

with open('app.py', 'w') as f:
    f.write(content)

print("Patch applied successfully.")
