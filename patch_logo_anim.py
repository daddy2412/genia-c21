with open('app.py', 'r') as f:
    content = f.read()

old_css = '.logo { width: 56px; height: 56px; border-radius: 8px; margin-bottom: 8px; }'
new_css = '''.logo {
            width: 56px; height: 56px; border-radius: 8px; margin-bottom: 8px;
            animation: logoPulse 2.5s ease-in-out infinite;
        }
        @keyframes logoPulse {
            0%, 100% { transform: scale(1) rotate(0deg); }
            50% { transform: scale(1.08) rotate(8deg); }
        }'''
content = content.replace(old_css, new_css, 1)

with open('app.py', 'w') as f:
    f.write(content)

print("Logo animation patch applied.")