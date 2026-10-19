
#!/usr/bin/env python3

import sys
import re
import subprocess
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET


# CONFIGURATION (base des urls) 

BASE_URL = "https://data.geopf.fr/telechargement"
RESOURCE = "BDORTHO"

# Dossier principal de téléchargement
DOWNLOAD_DIR = Path("/home/pviguier/Bureau/bdortho") # on ajoute le dossier au chemin 

# VÉRIFICATION DES ARGUMENTS
# verifie qu'on lui donne deux arguments en lancant le code le nom du .py et le numero de département 
if len(sys.argv) != 2:
    print("Usage : python3 bdortho.py ")
    sys.exit(1)
# récupère le numero de département 
ZONE = sys.argv[1].upper()

print()
print("TELECHARGEMENT BD ORTHO")
print(f"Département : {ZONE}")
print(f"Dossier     : {DOWNLOAD_DIR / ZONE}")
print()

# FONCTION : TÉLÉCHARGER DU XML
# permet de contacter le serveur avec l'url donné et lire la réponse et parcourt le xml 
def get_xml(url):
    print(f"Interrogation : {url}")

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(request) as response:
        data = response.read()

    return ET.fromstring(data)
# RÉCUPÉRATION DES ÉDITIONS
# creation de l'url de l'api pour récupérer le fichier xml principal pour un département 
url = (
    f"{BASE_URL}/resource/{RESOURCE}"
    f"?zone={ZONE}&page=1&limit=50"
)

root = get_xml(url) # on contacte le serveur 


# Namespace XML Atom
# on notifie que c'est des xml au format atom 
ATOM = "{http://www.w3.org/2005/Atom}"

# liste d'éditions : nom des bdortho existantes par département : BDORTHO_1-0_RVB-0M20_JP2-E080_LAMB93_D066_2015-01-01 qu'on rcupère dans le xml entre les  <title> et on ne garde que les RVB 
editions = []


for entry in root.findall(f"{ATOM}entry"):

    title = entry.findtext(f"{ATOM}title")

    if title and "_RVB-" in title:
        editions.append(title)


# Suppression des doublons
editions = sorted(set(editions))


if not editions:
    print()
    print("Aucune édition RVB trouvée.")
    sys.exit(0)


print()
print(f"{len(editions)} édition(s) RVB trouvée(s).")
print()


# TRAITEMENT DE CHAQUE ÉDITION

for edition in editions:

    # Récupération de l'année
# pour chaque edition (année) on crée un dossier, on construit l'url et on récuère le nouveau xml 
    match = re.search(r"_(\d{4})-\d{2}-\d{2}$", edition)

    if match:
        year = match.group(1)
    else:
        year = "inconnu"

    print(f"Année : {year}")

    # Création du dossier

    year_dir = DOWNLOAD_DIR / ZONE / year

    year_dir.mkdir(parents=True, exist_ok=True)

    # Interrogation de la sous-ressource
# on crée l'url pour chaque édition donc chaque année 
    edition_url = (
        f"{BASE_URL}/resource/{RESOURCE}/{edition}"
        f"?page=1&limit=50"
    )

    edition_root = get_xml(edition_url)

  
    # Récupération des URLs des fichiers
#  on récupère les urls de telechargement des fichiers zippes : files = "https://data.geopf.fr/...7z.001"] qui se trouve dans la section href du xml 
    files = []

    for entry in edition_root.findall(f"{ATOM}entry"):

        for link in entry.findall(f"{ATOM}link"):

            href = link.attrib.get("href", "")

            if ".7z." in href:
                files.append(href)

   
    # Suppression des doublons
    files = sorted(set(files))


    if not files:
        print("Aucun fichier trouvé pour cette édition.")
        continue


    print()
    print(f"{len(files)} fichier(s) à télécharger.")
    print()

    # Téléchargement des fichiers finaux 

    for number, file_url in enumerate(files, start=1):

        filename = file_url.split("/")[-1]

        print(f"Fichier {number}/{len(files)}")
        print(filename)

        command = [
            "aria2c",

            # Dossier de destination
            f"--dir={year_dir}",

            # Reprendre un téléchargement interrompu
            "--continue=true",

            # Nombre de tentatives
            "--max-tries=10",

            # Attendre 10 secondes entre les tentatives
            "--retry-wait=10",

            # Timeout
            "--timeout=60",

            # Timeout de connexion
            "--connect-timeout=30",

            # Une seule connexion par fichier
            "--split=1",

            # URL
            file_url,
        ]

        result = subprocess.run(command)

        if result.returncode != 0:

            print("ERREUR DE TELECHARGEMENT")
            print(filename)
        
            # On passe au fichier suivant
            continue

        print()
        print(f"OK : {filename}")


# ============================================================
# FIN
# ============================================================

print()
print("==============================================")
print("TOUS LES TELECHARGEMENTS SONT TERMINÉS")
print("==============================================")
print()
print(f"Les fichiers sont dans :")
print(DOWNLOAD_DIR / ZONE)
print()

