import os
import re
import bibtexparser

def clean_latex_accents(s):
    if not s:
        return ""
    latex_replacements = {
        r"{\oe}": "œ", r"\oe": "œ", r"{\OE}": "Œ", r"\OE": "Œ",
        r"{\ae}": "æ", r"\ae": "æ", r"{\AE}": "Æ", r"\AE": "Æ",
        r"\&": "&",
        r"\`e": "è", r"\`a": "à", r"\`u": "ù", r"\`o": "ò", r"\`i": "ì",
        r"\`E": "È", r"\`A": "À",
        r"\'e": "é", r"\'a": "á", r"\'i": "í", r"\'o": "ó", r"\'u": "ú",
        r"\'E": "É", r"\'A": "Á",
        r"\^e": "ê", r"\^a": "â", r"\^i": "î", r"\^o": "ô", r"\^u": "û",
        r"\^E": "Ê", r"\^A": "Â",
        r'\"e': "ë", r'\"a': "ä", r'\"i': "ï", r'\"o': "ö", r'\"u': "ü",
        r'\"E': "Ë", r'\"A': "Ä",
        r"\c{c}": "ç", r"\c{C}": "Ç",
        r"~": " ",
    }
    for latex, utf8 in latex_replacements.items():
        s = s.replace(latex, utf8)
    return s

def clean_str(s):
    if not s:
        return ""
    s = re.sub(r'[\{\}]', '', s)
    s = clean_latex_accents(s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def format_authors(author_str):
    if not author_str:
        return ""
    raw_authors = re.split(r'\s+and\s+', author_str, flags=re.IGNORECASE)
    formatted_authors = []
    for author in raw_authors:
        author = clean_str(author)
        if not author:
            continue
        if ',' in author:
            parts = author.split(',', 1)
            last_name = parts[0].strip()
            first_name = parts[1].strip()
            formatted_authors.append(f"{first_name} {last_name}")
        else:
            formatted_authors.append(author)
    return ", ".join(formatted_authors)

def get_category(entry_type):
    """ Mappe le type BibTeX vers la catégorie souhaitée """
    entry_type = entry_type.lower()
    if entry_type == 'article':
        return "Journal Articles"
    elif entry_type in ['inproceedings', 'conference', 'proceedings']:
        return "Peer Reviewed Conference Papers"
    else:
        return "Technical Reports and Miscellaneous"

def bibtex_to_academicpages(bib_file):
    with open(bib_file, 'r', encoding='utf-8') as f:
        bib_database = bibtexparser.load(f)

    os.makedirs("_publications", exist_ok=True)
    os.makedirs("files/bib", exist_ok=True)

    for entry in bib_database.entries:
        bib_id = entry.get('ID', 'pub')
        entry_type = entry.get('ENTRYTYPE', 'article')
        
        # 1. Sauvegarde du fichier BibTeX individuel
        db_single = bibtexparser.bibdatabase.BibDatabase()
        db_single.entries = [entry]
        bib_filename = f"files/bib/{bib_id}.bib"
        
        with open(bib_filename, 'w', encoding='utf-8') as out_bib:
            bibtexparser.dump(db_single, out_bib)

        # 2. Métadonnées nettoyées
        title = clean_str(entry.get('title', 'Sans titre'))
        title_yaml = title.replace("'", "''")
        
        authors = format_authors(entry.get('author', ''))
        authors_yaml = authors.replace("'", "''")
        
        category = get_category(entry_type)
        
        year = entry.get('year', '2026')
        month = entry.get('month', '01')
        
        if len(month) == 1:
            month = f"0{month}"
        elif not month.isdigit():
            month = "01"

        date_str = f"{year}-{month}-01"
        venue = clean_str(entry.get('journal', entry.get('booktitle', '')))
        venue_yaml = venue.replace("'", "''")
        
        doi = entry.get('doi', '').strip()
        url = entry.get('url', '').strip()
        
        slug = re.sub(r'[^a-zA-Z0-9-]', '-', bib_id).lower()
        permalink = f"/publication/{year}-{slug}"

        # 3. Écriture Markdown avec champ category
        md_content = f"""---
title: '{title_yaml}'
collection: publications
category: '{category}'
permalink: {permalink}
date: {date_str}
venue: '{venue_yaml}'
authors: '{authors_yaml}'
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

        print(f"✅ Généré [{category}] : {filename}")

if __name__ == "__main__":
    bib_file = "mes_publications.bib" 
    if os.path.exists(bib_file):
        bibtex_to_academicpages(bib_file)
        print("\n🎉 Régénération terminée !")
    else:
        print(f"❌ Erreur : Le fichier {bib_file} est introuvable.")