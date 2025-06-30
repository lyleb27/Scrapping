# Scrapping Articles avec Résumé IA et Envoi vers Notion

Ce projet récupère des articles d'un site web, génère un résumé via une IA locale (Ollama), catégorise les articles, puis envoie les données vers une base Notion.

## Fonctionnalités

- Extraction des articles et résumés depuis une URL donnée.
- Vérification de la disponibilité de l'API Ollama locale.
- Catégorisation automatique des articles via IA.
- Résumé IA des articles.
- Envoi des articles dans une base Notion via API.

## Prérequis

- Python 3.8+
- Serveur Ollama local fonctionnel (http://localhost:11434)
- Un token Notion et un ID de base Notion configurés.

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

## Remarques
Veillez à ce que votre serveur Ollama soit en marche pour bénéficier de la génération IA.