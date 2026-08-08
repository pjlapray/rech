import os
import re
import bibtexparser

def clean_str(s):
    if not s:
        return ""
    # Enlève les accolades BibTeX { ... }
    s = re.sub(r'[\{\}]', '', s)
    # Échappe les guillemets doubles pour le YAML
    s = s.replace('"', '\\"')
    return s.strip()

def bibtex_to_academicpages(bib_file):
    with open(bib_file, 'r', encoding='utf-8') as f:
        bib_database = bibtexparser.load(f)

    os.makedirs("_publications", exist_ok=True)

    for entry in bib_database.entries:
        # Clé BibTeX et type d'entrée
        bib_id = entry.get('ID', 'pub')
        entry_type = entry.get('ENTRYTYPE', 'article').lower()

        # Récupération des informations de base
        title = clean_str(entry.get('title', 'Sans titre'))
        year = entry.get('year', '2024')
        month = entry.get('month', '01')
        # Normalisation simple du mois
        if len(month) == 1:
            month = f"0{month}"
        elif not month.isdigit():
            month = "01"

        date_str = f"{year}-{month}-01"
        
        # Journal ou Conférence
        venue = clean_str(entry.get('journal', entry.get('booktitle', '')))
        
        # Auteurs et Liens
        authors = clean_str(entry.get('author', ''))
        doi = entry.get('doi', '')
        url = entry.get('url', '')
        
        # Permalien unique pour Jekyll
        slug = re.sub(r'[^a-zA-Z0-9-]', '-', bib_id).lower()
        permalink = f"/publication/{year}-{slug}"

        # Construction du fichier Markdown
        md_content = f"""---
title: "{title}"
collection: publications
permalink: {permalink}
date: {date_str}
venue: '{venue}'
"""
        if doi:
            md_content += f"paperurl: 'https://doi.org/{doi}'\n"
        elif url:
            md_content += f"paperurl: '{url}'\n"

        # Formatage de la citation sous le titre
        citation = f"{authors} ({year}). &quot;{title}.&quot; <i>{venue}</i>."
        md_content += f"citation: '{citation}'\n"
        md_content += "---\n\n"

        # Résumé (Abstract) s'il existe
        if 'abstract' in entry:
            md_content += f"### Abstract\n\n{clean_str(entry['abstract'])}\n"

        # Écriture du fichier dans _publications/
        filename = f"_publications/{year}-{slug}.md"
        with open(filename, 'w', encoding='utf-8') as out_f:
            out_f.write(md_content)

        print(f"✅ Généré : {filename}")

if __name__ == "__main__":
    # Remplacez 'mes_publications.bib' par le nom de votre fichier
    bib_file = "mes_publications.bib" 
    if os.path.exists(bib_file):
        bibtex_to_academicpages(bib_file)
        print("\n🎉 Toutes les publications ont été créées dans le dossier _publications/ !")
    else:
        print(f"❌ Erreur : Le fichier {bib_file} n'a pas été trouvé à la racine.")