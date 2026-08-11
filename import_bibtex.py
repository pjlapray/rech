import os
import re
import bibtexparser

def clean_latex_accents(s):
    """ Convertit les accents LaTeX courants (\'e, \'E, \^e, etc.) en caractères UTF-8 """
    if not s:
        return ""
    
    # Remplacement des accents TeX/LaTeX courants
    latex_replacements = {
        # Accent grave (\`e, \`a, \`u, etc.)
        r"\`e": "è", r"\`a": "à", r"\`u": "ù", r"\`o": "ò", r"\`i": "ì",
        r"\`E": "È", r"\`A": "À",
        # Accent aigu (\'e, \'a, etc.)
        r"\'e": "é", r"\'a": "á", r"\'i": "í", r"\'o": "ó", r"\'u": "ú",
        r"\'E": "É", r"\'A": "Á",
        # Circonflexe (\^e, \^a, etc.)
        r"\^e": "ê", r"\^a": "â", r"\^i": "î", r"\^o": "ô", r"\^u": "û",
        r"\^E": "Ê", r"\^A": "Â",
        # Tréma (\"e, \"a, etc.)
        r'\"e': "ë", r'\"a': "ä", r'\"i': "ï", r'\"o': "ö", r'\"u': "ü",
        r'\"E': "Ë", r'\"A': "Ä",
        # Cédille (\c{c})
        r"\c{c}": "ç", r"\c{C}": "Ç",
    }
    
    for latex, utf8 in latex_replacements.items():
        s = s.replace(latex, utf8)
        
    return s

def clean_str(s):
    if not s:
        return ""
    # Enlève les accolades BibTeX { }
    s = re.sub(r'[\{\}]', '', s)
    # Convertit les accents TeX en UTF-8
    s = clean_latex_accents(s)
    # Remplace les guillemets doubles par des simples
    s = s.replace('"', "'")
    # Nettoie les espaces multiples
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def format_authors(author_str):
    if not author_str:
        return ""
    authors = clean_str(author_str)
    # Remplace les 'and' du BibTeX par des virgules
    authors = re.sub(r'\s+and\s+', ', ', authors, flags=re.IGNORECASE)
    return authors

def bibtex_to_academicpages(bib_file):
    with open(bib_file, 'r', encoding='utf-8') as f:
        bib_database = bibtexparser.load(f)

    os.makedirs("_publications", exist_ok=True)
    os.makedirs("files/bib", exist_ok=True)

    for entry in bib_database.entries:
        bib_id = entry.get('ID', 'pub')
        
        # 1. Sauvegarde du fichier BibTeX individuel
        db_single = bibtexparser.bibdatabase.BibDatabase()
        db_single.entries = [entry]
        bib_filename = f"files/bib/{bib_id}.bib"
        
        with open(bib_filename, 'w', encoding='utf-8') as out_bib:
            bibtexparser.dump(db_single, out_bib)

        # 2. Métadonnées nettoyées
        title = clean_str(entry.get('title', 'Sans titre'))
        authors = format_authors(entry.get('author', ''))
        year = entry.get('year', '2026')
        month = entry.get('month', '01')
        
        if len(month) == 1:
            month = f"0{month}"
        elif not month.isdigit():
            month = "01"

        date_str = f"{year}-{month}-01"
        venue = clean_str(entry.get('journal', entry.get('booktitle', '')))
        doi = entry.get('doi', '').strip()
        url = entry.get('url', '').strip()
        
        slug = re.sub(r'[^a-zA-Z0-9-]', '-', bib_id).lower()
        permalink = f"/publication/{year}-{slug}"

        # 3. Écriture Markdown avec guillemets simples '...' STRICTS
        md_content = f"""---
title: '{title}'
collection: publications
permalink: {permalink}
date: {date_str}
venue: '{venue}'
authors: '{authors}'
bibfile: '/files/bib/{bib_id}.bib'
"""
        if doi:
            md_content += f"paperurl: 'https://doi.org/{doi}'\n"
        elif url:
            md_content += f"paperurl: '{url}'\n"

        md_content += "---\n\n"

        if 'abstract' in entry:
            md_content += f"### Abstract\n\n{clean_str(entry['abstract'])}\n"

        filename = f"_publications/{year}-{slug}.md"
        with open(filename, 'w', encoding='utf-8') as out_f:
            out_f.write(md_content)

        print(f"✅ Généré : {filename}")

if __name__ == "__main__":
    bib_file = "mes_publications.bib" 
    if os.path.exists(bib_file):
        bibtex_to_academicpages(bib_file)
        print("\n🎉 Régénération terminée !")
    else:
        print(f"❌ Erreur : Le fichier {bib_file} est introuvable.")