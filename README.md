cd ~/genia-c21

# Insère les nouvelles sections juste avant "## Licence"
python3 - << 'PYEOF'
import re

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

new_sections = '''## Infrastructure hôte (home-lab)

Le serveur `svr-genia` (K3s) tourne comme VM dans un home-lab plus large, hébergé sur deux hôtes physiques Windows avec Hyper-V, sur le domaine `DADDYCONNECTIT` :

| Hôte physique | Rôle |
|---|---|
| `PC-DADDY` | Hôte Hyper-V principal (Site A — serveur OpenVPN) |
| `DESKTOP-J7H10AF` | Hôte Hyper-V secondaire (Site B — client OpenVPN) |

**VMs clés du home-lab :**

| VM | Rôle |
|---|---|
| `SVR-GENIA` | K3s — héberge `genia-c21` (ce projet) |
| `DC-SVR` | Contrôleur de domaine (`192.168.2.20`) |
| `SVR-MON01` | Supervision (Zabbix) |
| `GRAFANA-SRV` | Dashboards Grafana (`192.168.2.25`) |
| `SVR-BACKUP` | Sauvegardes |
| `SRV-APP01` | Applications diverses |
| `Wazuh-Manager` (Ubuntu) | SIEM — gestion Wazuh |
| `SecurityOnion-SOC` | Supervision sécurité réseau (Elastic Fleet) |

**Réseau** : double NAT derrière un modem Bell, liaison site-à-site OpenVPN entre `PC-DADDY` (serveur) et `DESKTOP-J7H10AF` (client) via OPNsense, pour unifier les deux hôtes Hyper-V sur un même réseau de gestion.

> Capture d'écran de la topologie Hyper-V / VMs disponible dans `docs/screenshots/`.

## Monitoring — détails

**Zabbix** (`172.22.82.101:8080`)
- Supervision centralisée des 7 hôtes du home-lab (Windows + Linux)
- Agents déployés sur `DC-SVR`, `SVR-MON01`, `SVR-BACKUP`, `SRV-APP01`, `SVR-WAZUH`, `SVR-GENIA`
- Alertes sur disponibilité, charge CPU/RAM/disque, et services critiques (dont les pods K3s de `genia-c21`)

**Grafana** (`172.22.54.68:3000`)
- Dashboards par hôte, alimentés par Node Exporter (Linux) et Windows Exporter (Windows)
- Métriques : CPU, RAM, disque, réseau, historique et tendances
- Dashboard dédié pour `SVR-GENIA` (ressources du nœud K3s hébergeant `genia-c21`)

**Wazuh** — SIEM / sécurité
- Intégrité des fichiers (FIM), audit système
- Conformité PCI DSS / NIST 800-53
- VMs enrôlées via Elastic Fleet (Security Onion)

'''

content = content.replace("## Licence", new_sections + "## Licence")

with open("README.md", "w", encoding="utf-8") as f:
    f.write(content)

print("README.md mis à jour")
PYEOF
