# 📚 TLDR Tech Scraper & Notion Uploader

Ce projet récupère des articles d'un site web, génère un résumé via une IA locale (Ollama), catégorise les articles, puis envoie les données vers une base Notion.

## Fonctionnalités

✅ Extraction des articles depuis la page cible.  
✅ Résumé court en anglais.  
✅ Résumé court rédigé par IA en français (plus agréable à l'écoute).  
✅ Génération d’un fichier audio par article.  
✅ Génération d’un fichier audio combiné pour tous les articles d’une catégorie.  
✅ Envoi automatique vers une base Notion (via l’API Notion).  
✅ Génération automatique des mots-clés IA pour classification dynamique.  
✅ Ajout du chemin local du fichier audio dans Notion.

## Prérequis

- Python 3.8+
- Serveur Ollama local fonctionnel (http://localhost:11434)
- Un token Notion et un ID de base Notion configurés avec :
```
"Titre": Titre,
"Résumé": text,
"Résumé IA": text,
"Catégorie(s) IA": selection multiple,
"URL": url,
"Date de parution": date,
"Audio Résumé": text
```

## Installation

1. Cloner le repo
2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

Modifier les variables de configuration (NOTION_TOKEN, NOTION_DATABASE_ID, OLLAMA_URL et OLLAMA_MODEL) dans le script.

## Usage
Lancer le script :

```bash
python main.py
```
Par défaut, il scrape les articles de l'URL définie dans target_url.
```bash
target_url → Lien TLDR de la page à scraper.
```
## Remarques
Veillez à ce que votre serveur Ollama soit en marche pour bénéficier de la génération IA.