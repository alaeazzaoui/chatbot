# 🧠 RAG Chatbot sur CV (Streamlit + Gemini + FAISS)

## 📌 Introduction

Ce projet est un chatbot intelligent basé sur l’architecture **RAG (Retrieval-Augmented Generation)**, capable de répondre uniquement aux questions liées au contenu d’un CV.

L’utilisateur peut charger son CV (PDF ou DOCX) puis dialoguer avec un assistant qui extrait les informations pertinentes et génère des réponses strictement basées sur ce document.

Toute question hors périmètre est automatiquement refusée.

---

## 🎯 Objectif

- Charger un CV (PDF / DOCX)
- Extraire et nettoyer son contenu
- Découper le texte en chunks
- Créer des embeddings sémantiques
- Effectuer une recherche vectorielle
- Générer des réponses avec un LLM
- Garantir des réponses uniquement basées sur le CV

---

## ⚙️ Technologies utilisées

- **Streamlit** : interface utilisateur
- **Google Gemini 2.0 Flash (google-genai)** : génération de réponses
- **Sentence Transformers (all-MiniLM-L6-v2)** : embeddings
- **FAISS** : recherche vectorielle
- **PyPDF2** : lecture de fichiers PDF
- **python-docx** : lecture de fichiers DOCX
- **python-dotenv** : gestion des variables d’environnement

---

## 🧩 Architecture du pipeline RAG

Le pipeline est composé de 11 étapes :

1. Chargement du CV  
2. Nettoyage du texte  
3. Découpage en chunks  
4. Calcul des embeddings  
5. Indexation vectorielle (FAISS)  
6. Recherche des chunks pertinents  
7. Construction du prompt  
8. Génération de réponse (Gemini)  
9. Filtrage des questions hors sujet  
10. Rechargement dynamique du CV  
11. Interface utilisateur Streamlit  

---

## 🔄 Fonctionnement détaillé

### 📥 Chargement du CV
Support des fichiers PDF et DOCX avec extraction automatique du texte.

### 🧹 Nettoyage
Suppression des caractères spéciaux, espaces multiples et sauts de ligne inutiles.

### ✂️ Chunking
Découpage du texte en segments de :
- 300 mots
- overlap de 50 mots

### 🧠 Embeddings
Transformation des chunks en vecteurs de 384 dimensions.

### 📦 Vector Store
Indexation des embeddings avec FAISS pour recherche rapide.

### 🔍 Retrieval
Récupération des 4 chunks les plus pertinents selon la question.

### 📝 Prompt Engineering
Construction d’un prompt imposant des réponses uniquement basées sur le CV.

### 🤖 Génération
Utilisation de Gemini 2.0 Flash pour générer la réponse.

### 🔒 Sécurité métier
- Filtrage des questions hors sujet
- Réponses refusées si non liées au CV

### 🔁 Rechargement dynamique
Chaque nouveau CV recrée entièrement le pipeline.

---

## 🔐 Sécurité

- Clé API stockée dans un fichier `.env`
- Protection via `python-dotenv`
- Isolation complète entre plusieurs CVs
- Filtrage des questions hors domaine
- Prompt strict limitant les réponses au CV

---

## 🖥️ Interface Streamlit

- Upload de CV (PDF / DOCX)
- Chat interactif avec historique
- Affichage du CV actif
- Réinitialisation automatique lors du changement de CV
- Messages de refus clairs pour questions hors périmètre

---

## 📊 Résultats

- Extraction correcte des CVs
- Réponses précises et contextualisées
- Refus des questions hors CV
- Rechargement dynamique fonctionnel
- Interface fluide et intuitive

---

## 🚀 Lancer le projet

```bash
pip install -r requirements.txt
streamlit run app.py
