#🧠 RAG Chatbot sur CV (Streamlit + Gemini + FAISS)

#📌 Introduction

Ce projet est un Chatbot intelligent basé sur l’architecture RAG (Retrieval-Augmented Generation), capable de répondre uniquement aux questions liées au contenu d’un CV.

L’utilisateur peut importer son CV (PDF ou DOCX), puis interagir avec un assistant qui extrait les informations pertinentes et génère des réponses contextualisées.

Toute question hors sujet est automatiquement refusée afin de garantir un usage strictement centré sur le CV.

🎯 Objectif du projet
Charger un CV (PDF / DOCX)
Extraire et structurer son contenu
Permettre une interaction en langage naturel
Répondre uniquement à partir du CV
Refuser toute question hors périmètre
⚙️ Stack technique
Composant	Technologie	Rôle
LLM	Google Gemini 2.5 Flash (google-genai)	Génération des réponses
Embeddings	sentence-transformers (all-MiniLM-L6-v2)	Représentation sémantique
Vector DB	FAISS	Recherche rapide de similarité
PDF Reader	PyPDF2	Extraction texte PDF
DOCX Reader	python-docx	Lecture Word
UI	Streamlit	Interface web
Variables env	python-dotenv	Gestion sécurisée des clés
🧩 Architecture RAG

Le pipeline est structuré en étapes modulaires :

Chargement du CV
Nettoyage du texte
Chunking (découpage en segments)
Génération des embeddings
Indexation vectorielle (FAISS)
Recherche des chunks pertinents
Construction du prompt
Génération de réponse (Gemini)
Filtrage des questions hors sujet
Rechargement dynamique du CV
Interface utilisateur (Streamlit)
🔄 Fonctionnement du pipeline
1. Chargement du CV

Support des fichiers PDF et DOCX avec extraction automatique du texte.

2. Nettoyage

Suppression des caractères inutiles, espaces multiples et artefacts.

3. Chunking

Découpage en segments de :

300 mots
overlap de 50 mots
4. Embeddings

Chaque chunk est converti en vecteur de 384 dimensions.

5. Vector Store

Index FAISS pour recherche sémantique rapide.

6. Retrieval

Récupération des 4 chunks les plus pertinents.

7. Prompt Engineering

Construction d’un prompt strict limitant les réponses au CV.

8. Génération

Réponse générée via Gemini 2.0 Flash.

9. Sécurité métier
Filtrage des questions hors domaine
Réponse refusée si hors CV
10. Rechargement dynamique

Chaque nouveau CV recrée entièrement le pipeline.

🔐 Sécurité
Clé API stockée dans .env
Fichier .env ignoré via .gitignore
Isolation complète entre deux CVs
Filtrage des questions hors sujet
Prompt restrictif (CV only)
🖥️ Interface utilisateur (Streamlit)
Upload CV (PDF / DOCX)
Chat interactif avec historique
Affichage du CV actif
Reset automatique lors du changement de CV
Messages de refus clairs
📊 Résultats

✔ Extraction correcte des CVs
✔ Réponses précises et contextualisées
✔ Refus des questions hors sujet
✔ Rechargement dynamique fonctionnel
✔ Interface fluide et intuitive

🚀 Lancer le projet
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run app.py
🔮 Améliorations possibles
Support multilingue 🌍
Score de pertinence des chunks
Déploiement Streamlit Cloud ☁️
Support de nouveaux documents (LM, rapports, portfolio)
Amélioration du reranking des résultats


🧠 Conclusion

Ce projet illustre une implémentation complète d’un système RAG appliqué à un cas concret (CV chatbot), combinant :

NLP (embeddings)
Recherche vectorielle (FAISS)
LLM (Gemini)
Interface interactive (Streamlit)

Il constitue une base solide pour des applications IA plus avancées.
