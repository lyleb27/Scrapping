import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re

# Configuration
NOTION_TOKEN = "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"
NOTION_DATABASE_ID = "21e3342b-9620-8050-89a4-d66f5e59441b"
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma3:latest"

# -------- Extraction des articles avec résumé du site --------
def extract_articles(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = []

    for article in soup.select('article.mt-3'):
        # Titre dans le <h3> contenu dans le <a>
        a_tag = article.find('a', class_='font-bold')
        title = ""
        if a_tag:
            h3 = a_tag.find('h3')
            if h3:
                title = h3.get_text(strip=True)
        
        if not title or len(title) <= 5:
            continue

        # Résumé dans le div.newsletter-html, concaténation des <p>
        summary = ""
        summary_div = article.find('div', class_='newsletter-html')
        if summary_div:
            paragraphs = summary_div.find_all('p')
            summary = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

            if not summary:
                summary = summary_div.get_text(strip=True)

        articles.append({
            "title": title,
            "summary": summary
        })

    return articles

# -------- Vérification Ollama --------
def is_ollama_available():
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        response.raise_for_status()
        return True
    except:
        print("⚠️ Ollama non disponible, mode fallback activé.")
        return False

# -------- Connexion à l'IA via Ollama --------
def query_ollama(prompt):
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        print(f"⚠️ Erreur Ollama : {e}")
        return None

def categorize_article(article_title):
    prompt = f"""Catégorise cet article en UNE SEULE catégorie parmi :
- Stratégie Marketing
- Innovation Produit
- Réseaux Sociaux
- Analytics/Data
- E-commerce
- Contenu/SEO
- Tendances Tech
- Autre

Article : {article_title}

Réponds uniquement avec le nom exact de la catégorie :"""
    result = query_ollama(prompt)
    return result if result else "Inconnu"

def generate_ia_summary(text):
    prompt = f"Résume ce texte en 2 à 3 phrases claires et concises :\n\n{text}\n\n Je ne veux que le résumé sans autres informations ou exolications."
    result = query_ollama(prompt)
    return result if result else "Résumé IA indisponible"

# -------- Extraction de la date depuis l'URL --------
def extract_date_from_url(url):
    match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", url)
    if match:
        return match.group(1)
    else:
        return datetime.now().strftime("%Y-%m-%d")

# -------- Envoi vers Notion --------
def send_to_notion(title, ia_summary, category, source_url, publication_date, original_summary=""):
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Titre": {"title": [{"text": {"content": title[:200]}}]},
            "Résumé IA": {"rich_text": [{"text": {"content": ia_summary[:2000]}}]},
            "Catégorie(s) IA": {"rich_text": [{"text": {"content": category}}]},
            "URL": {"url": source_url},
            "Date de parution": {"date": {"start": publication_date}},
            "Résumé": {"rich_text": [{"text": {"content": original_summary[:2000]}}]}
        }
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
    if response.status_code in (200, 201):
        print(f"✅ Envoyé à Notion : {title[:50]}...")
    else:
        print(f"❌ Erreur Notion : {response.status_code} - {response.text}")

# -------- Pipeline complet --------
def process_articles(url):
    ollama_available = is_ollama_available()
    publication_date = extract_date_from_url(url)

    articles = extract_articles(url)
    print(f"\n📰 {len(articles)} articles trouvés.\n")

    for idx, article in enumerate(articles, 1):
        title = article["title"]
        summary = article["summary"]
        print(f"{idx}. {title}")

        try:
            if ollama_available:
                category = categorize_article(title)
                ia_summary = generate_ia_summary(summary)
            else:
                category = "Inconnu"
                ia_summary = "Résumé IA indisponible"

            if not summary:
                summary = "Résumé indisponible"

            print(f"   📄 Résumé site : {summary}")
            print(f"   🧠 Résumé IA : {ia_summary}")
            print(f"   🗂️ Catégorie IA : {category}")

            send_to_notion(title, ia_summary, category, url, publication_date, original_summary=summary)

            time.sleep(1)

        except Exception as e:
            print(f"❌ Erreur traitement : {e}")
            continue

if __name__ == "__main__":
    target_url = "https://tldr.tech/marketing/2025-06-26"  # Change selon besoin
    process_articles(target_url)
