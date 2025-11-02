import os
import re
import requests
import time
import logging
import sys
import string


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
compact = "--compact" in sys.argv
repo_dir = os.path.dirname(os.path.dirname(__file__))
scores_dir = os.path.join(repo_dir, "scores")
readme_path = os.path.join(repo_dir, "README.md")
descriptions_dir = os.path.join(repo_dir, "descriptions")
base_url = "https://github.com/269652/my-classical-legacy/raw/refs/heads/main"
os.makedirs(descriptions_dir, exist_ok=True)

disclaimer_path = os.path.join(repo_dir, "DISCLAIMER.md")
with open(disclaimer_path, encoding="utf-8") as f:
    disclaimer = f.read().strip()


def shorten_url_isgd(long_url):
    try:
        resp = requests.get("https://is.gd/create.php", params={"format": "simple", "url": long_url}, timeout=10)
        if resp.status_code == 200:
            return resp.text.strip()
    except Exception as e:
        logging.error(f"Failed to shorten {long_url}: {e}")
    return long_url


def normalize_title(title):
    return ''.join(c for c in title.lower() if c.isalnum())


# Parse README for all links for each piece using the specified algorithm
with open(readme_path, encoding="utf-8") as f:
    readme = f.read()

regen = "--regen" in sys.argv

def normalize_label(label):
    return label.lower().replace('.', '').replace(' ', '')

# Only use text after the scores section
scores_idx = readme.find("## 📑 Scores & Links")
if scores_idx == -1:
    raise Exception("Could not find '## 📑 Scores & Links' in README")
scores_text = readme[scores_idx:]

readme_links = {}
for block in scores_text.split('- **')[1:]:
    # Parse title
    title_match = re.match(r'([^*]+)\*\*', block)
    if not title_match:
        continue
    title = title_match.group(1).strip()
    # Remove title + stars from section
    section = block[title_match.end():].strip()
    # Split section by ' · '
    parts = [p.strip() for p in section.split('·') if p.strip()]
    logging.info(f"Block title: {title}")
    logging.info(f"Parts: {parts}")
    links = {}
    for part in parts:
        md_match = re.match(r'\[([^\]]+)\]\(([^)]+)\)', part)
        if md_match:
            label = normalize_label(md_match.group(1))
            url = md_match.group(2)
            links[label] = url
    logging.info(f"Links for {title}: {links}")
    norm_title = normalize_title(title)
    logging.info(f"Normalized title: {norm_title}")
    readme_links[norm_title] = links
# Process last block


# Helper to parse existing links from output file
def parse_existing_links(filepath):
    links = {}
    if not os.path.isfile(filepath):
        return links
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            for part in line.strip().split("•"):
                part = part.strip()
                if part.startswith("PDF:"):
                    links["pdf"] = part.split(":", 1)[1].strip()
                elif part.startswith("Audio:"):
                    links["audio"] = part.split(":", 1)[1].strip()
                elif part.startswith("MIDI:"):
                    links["midi"] = part.split(":", 1)[1].strip()
                elif part.startswith("Flat.io:"):
                    links["flat.io"] = part.split(":", 1)[1].strip()
                elif part.startswith("Spotify:"):
                    links["spotify"] = part.split(":", 1)[1].strip()
    return links

# For each piece in scores folder, generate description
for fname in os.listdir(scores_dir):
    if not fname.lower().endswith('.pdf'):
        continue
    title = os.path.splitext(fname)[0]
    norm_title = normalize_title(title)
    links = readme_links.get(norm_title, {})
    # If not found, try to match by stripping trailing digits (duration) from README keys
    if not links:
        for k in readme_links:
            k_base = re.sub(r'(\d+[hm])$', '', k)
            if k_base == norm_title:
                links = readme_links[k]
                break
    out_path = os.path.join(descriptions_dir, f"{title}.txt")
    existing_links = parse_existing_links(out_path)
    out_fields = {}
    # PDF
    pdf_url = f'{base_url}/scores/{fname.replace(" ", "%20")}'
    pdf_link = existing_links.get("pdf")
    if regen or not (pdf_link and pdf_link.startswith("https://is.gd/")):
        src_link = links.get("pdf")
        if src_link and (src_link.startswith("https://github.com/") or src_link.startswith("https://media.githubusercontent.com/")):
            pdf_link = shorten_url_isgd(src_link)
            time.sleep(0.5)
        elif src_link:
            pdf_link = src_link
        else:
            pdf_link = shorten_url_isgd(pdf_url)
            time.sleep(0.5)
    out_fields['PDF'] = pdf_link
    # Audio
    audio_url = f'{base_url}/interpretations/suno/{title}.wav'.replace(" ", "%20")
    audio_link = existing_links.get("audio")
    if regen or not (audio_link and audio_link.startswith("https://is.gd/")):
        src_link = links.get("audio")
        if src_link and (src_link.startswith("https://github.com/") or src_link.startswith("https://media.githubusercontent.com/")):
            audio_link = shorten_url_isgd(src_link)
            time.sleep(0.5)
        elif src_link:
            audio_link = src_link
        else:
            audio_link = shorten_url_isgd(audio_url)
            time.sleep(0.5)
    out_fields['Audio'] = audio_link
    # MIDI
    midi_url = f'{base_url}/midi/{title}.mid'.replace(" ", "%20")
    midi_link = existing_links.get("midi")
    if regen or not (midi_link and midi_link.startswith("https://is.gd/")):
        src_link = links.get("midi")
        if src_link and (src_link.startswith("https://github.com/") or src_link.startswith("https://media.githubusercontent.com/")):
            midi_link = shorten_url_isgd(src_link)
            time.sleep(0.5)
        elif src_link:
            midi_link = src_link
        else:
            midi_link = shorten_url_isgd(midi_url)
            time.sleep(0.5)
    out_fields['MIDI'] = midi_link
    # Flat.io
    flatio_url = links.get("flat.io") or links.get("flatio")
    flatio_link = existing_links.get("flat.io") or existing_links.get("flatio")
    if flatio_url:
        if regen or not (flatio_link and flatio_link.startswith("https://is.gd/")):
            if flatio_url.startswith("https://flat.io/"):
                flatio_link = shorten_url_isgd(flatio_url)
                time.sleep(0.5)
            else:
                flatio_link = flatio_url
        out_fields['Flat.io'] = flatio_link
    # Spotify
    spotify_link = links.get("spotify") or existing_links.get("spotify")
    if spotify_link:
        out_fields['Spotify'] = spotify_link
    # Write output in fixed order
    order = ['PDF', 'Audio', 'MIDI', 'Flat.io', 'Spotify']
    output_line = " • ".join(f"{k}: {out_fields[k]}" for k in order if k in out_fields)
    with open(out_path, "w", encoding="utf-8") as out_file:
        out_file.write(output_line + "\n\n" + disclaimer)
    logging.info(f"Wrote description: {out_path}")

