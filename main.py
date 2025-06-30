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

# Liste dynamique des mots-clés utilisés pendant l'exécution
existing_keywords = set()

# -------- Extraction des articles avec résumé du site --------
def extract_articles(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = []

    for article in soup.select('article.mt-3'):
        a_tag = article.find('a', class_='font-bold')
        title = ""
        if a_tag:
            h3 = a_tag.find('h3')
            if h3:
                title = h3.get_text(strip=True)

        if not title or len(title) <= 5:
            continue

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

# -------- Résumé IA --------
def summarize_article(summary):
    prompt = f"""Texte original :
{summary}

Ta tâche : Fournir directement un résumé concis de 2 à 3 lignes. 
Réponds uniquement avec le résumé. Ne fais pas d’introduction ni de conclusion :"""
    
    result = query_ollama(prompt)
    return result if result else "Résumé IA indisponible"

# -------- Génération des mots-clés --------
def generate_keywords(summary_ia):
    prompt = f"""Voici un résumé : {summary_ia}

Donne trois mots-clés courts et pertinents séparés par une virgule, sans explication :"""
    result = query_ollama(prompt)
    if not result:
        return []

    # Nettoyage basique des mots-clés
    keywords = [kw.strip().lower() for kw in result.split(',') if kw.strip()]
    return keywords

# -------- Gestion des catégories dynamiques --------
def get_or_add_keywords(keywords):
    final_keywords = []
    for kw in keywords:
        if kw.lower() in existing_keywords:
            final_keywords.append(kw)
        else:
            existing_keywords.add(kw.lower())
            final_keywords.append(kw)
    return final_keywords

# -------- Extraction de la date depuis l'URL --------
def extract_date_from_url(url):
    match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", url)
    if match:
        return match.group(1)
    else:
        return datetime.now().strftime("%Y-%m-%d")

# -------- Envoi vers Notion --------
def send_to_notion(title, summary, summary_ia, keywords, source_url, publication_date):
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Titre": {"title": [{"text": {"content": title[:200]}}]},
            "Résumé": {"rich_text": [{"text": {"content": summary[:2000]}}]},
            "Résumé IA": {"rich_text": [{"text": {"content": summary_ia[:2000]}}]},
            "Catégorie(s) IA": {"multi_select": [{"name": kw} for kw in keywords]},
            "URL": {"url": source_url},
            "Date de parution": {"date": {"start": publication_date}}
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
            if not summary:
                summary = "Résumé indisponible"

            summary_ia = summarize_article(summary)
            keywords_generated = generate_keywords(summary_ia)
            keywords_to_use = get_or_add_keywords(keywords_generated)

            print(f"   📄 Résumé site : {summary}")
            print(f"   📑 Résumé IA : {summary_ia}")
            print(f"   🏷️ Mots-clés : {keywords_to_use}")

            send_to_notion(title, summary, summary_ia, keywords_to_use, url, publication_date)

            time.sleep(1)

        except Exception as e:
            print(f"❌ Erreur traitement : {e}")
            continue

if __name__ == "__main__":
    target_url = "https://tldr.tech/marketing/2025-06-27"  # Change selon besoin
    process_articles(target_url)
