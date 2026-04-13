import os
import re
import numpy as np
import streamlit as st
import google.generativeai as genai
import faiss
import PyPDF2
from docx import Document
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# 0. Configuration
# ─────────────────────────────────────────────
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
GEMINI_MODEL = "gemini-2.5-flash"


# ─────────────────────────────────────────────
# 1. Chargement du CV
# ─────────────────────────────────────────────
def load_cv(file) -> str:
    """Lit un fichier PDF ou DOCX et retourne son texte brut."""
    name = file.name.lower()

    if name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        text = "\n".join(
            page.extract_text() or "" for page in reader.pages
        )

    elif name.endswith(".docx"):
        doc = Document(file)
        text = "\n".join(para.text for para in doc.paragraphs)

    else:
        raise ValueError("Format non supporté. Utilise un PDF ou DOCX.")

    return text


# ─────────────────────────────────────────────
# 2. Prétraitement
# ─────────────────────────────────────────────
def clean_text(text: str) -> str:
    """Nettoie le texte : espaces multiples, sauts de ligne excessifs, caractères parasites."""
    text = re.sub(r'\r\n|\r', '\n', text)          # normalise les retours chariot
    text = re.sub(r'\n{3,}', '\n\n', text)         # max 2 sauts de ligne
    text = re.sub(r'[ \t]+', ' ', text)            # espaces multiples → un seul
    text = re.sub(r'[^\x00-\x7FÀ-ÿ]', '', text)   # supprime les caractères non standards
    return text.strip()


# ─────────────────────────────────────────────
# 3. Chunking
# ─────────────────────────────────────────────
def chunk_document(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """Découpe le texte en chunks de taille fixe avec overlap."""
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap  # avance avec overlap

    return chunks


# ─────────────────────────────────────────────
# 4. Embeddings
# ─────────────────────────────────────────────
def build_embeddings(chunks: list[str], model: SentenceTransformer) -> np.ndarray:
    """Transforme les chunks en vecteurs numériques via HuggingFace."""
    embeddings = model.encode(chunks, show_progress_bar=False)
    return np.array(embeddings, dtype="float32")


# ─────────────────────────────────────────────
# 5. Indexation FAISS
# ─────────────────────────────────────────────
def create_vector_store(chunks: list[str], embeddings: np.ndarray) -> dict:
    """Stocke les vecteurs dans un index FAISS et garde les chunks associés."""
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return {"index": index, "chunks": chunks}


# ─────────────────────────────────────────────
# 6. Recherche
# ─────────────────────────────────────────────
def retrieve_relevant_chunks(question: str, store: dict, k: int = 4) -> list[str]:
    """Récupère les k chunks les plus proches de la question."""
    query_vec = EMBED_MODEL.encode([question])
    query_vec = np.array(query_vec, dtype="float32")
    _, indices = store["index"].search(query_vec, k)
    return [store["chunks"][i] for i in indices[0] if i < len(store["chunks"])]


# ─────────────────────────────────────────────
# 7. Construction du Prompt
# ─────────────────────────────────────────────
def build_prompt(question: str, context: str) -> str:
    """Construit le prompt envoyé à Gemini."""
    return f"""Tu es un assistant spécialisé dans l'analyse de CV.
Tu dois répondre UNIQUEMENT à partir du contenu du CV fourni ci-dessous.
Si la question ne concerne pas le CV ou si l'information n'est pas dans le CV,
réponds exactement : "Je ne peux répondre qu'aux questions relatives au CV chargé."

CV :
{context}

Question : {question}

Réponse :"""


# ─────────────────────────────────────────────
# 8. Génération de la réponse
# ─────────────────────────────────────────────
def generate_answer(prompt: str) -> str:
    """Envoie le prompt à Gemini et retourne la réponse."""
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()


# ─────────────────────────────────────────────
# 9. Sécurité métier
# ─────────────────────────────────────────────
def answer_cv_only(question: str, store: dict) -> str:
    """Pipeline complet : recherche + prompt + génération avec garde-fou."""
    # Mots-clés hors sujet évidents (couche de sécurité supplémentaire)
    off_topic_keywords = [
        "météo", "recette", "film", "sport", "actualité",
        "politique", "histoire du monde", "blague", "jeu"
    ]
    q_lower = question.lower()
    if any(kw in q_lower for kw in off_topic_keywords):
        return "Je ne peux répondre qu'aux questions relatives au CV chargé."

    # Recherche des chunks pertinents
    relevant_chunks = retrieve_relevant_chunks(question, store)
    context = "\n\n".join(relevant_chunks)

    # Construction du prompt et génération
    prompt = build_prompt(question, context)
    answer = generate_answer(prompt)
    return answer


# ─────────────────────────────────────────────
# 10. Rechargement dynamique
# ─────────────────────────────────────────────
def reload_vector_store(file) -> dict:
    """Recharge entièrement le vector store à partir d'un nouveau CV."""
    raw_text = load_cv(file)
    clean = clean_text(raw_text)
    chunks = chunk_document(clean)
    embeddings = build_embeddings(chunks, EMBED_MODEL)
    store = create_vector_store(chunks, embeddings)
    return store


# ─────────────────────────────────────────────
# 11. Interface Streamlit
# ─────────────────────────────────────────────
def run_streamlit_app():
    st.set_page_config(page_title="Chatbot RAG — CV", page_icon="📄")
    st.title("📄 Chatbot RAG sur CV")
    st.caption("Posez des questions sur votre CV — Propulsé par Gemini + HuggingFace")

    # Initialisation de la session
    if "store" not in st.session_state:
        st.session_state.store = None
    if "history" not in st.session_state:
        st.session_state.history = []
    if "cv_name" not in st.session_state:
        st.session_state.cv_name = None

    # ── Sidebar : upload du CV ──
    with st.sidebar:
        st.header("📂 Charger un CV")
        uploaded_file = st.file_uploader(
            "Choisissez un fichier PDF ou DOCX",
            type=["pdf", "docx"]
        )

        if uploaded_file is not None:
            # Détecte si c'est un nouveau CV
            if uploaded_file.name != st.session_state.cv_name:
                with st.spinner("⏳ Chargement et indexation du CV..."):
                    try:
                        st.session_state.store = reload_vector_store(uploaded_file)
                        st.session_state.cv_name = uploaded_file.name
                        st.session_state.history = []  # reset historique
                        st.success(f"✅ CV chargé : **{uploaded_file.name}**")
                    except Exception as e:
                        st.error(f"Erreur : {e}")

        # Affiche le CV actif
        if st.session_state.cv_name:
            st.info(f"📄 CV actif : **{st.session_state.cv_name}**")
        else:
            st.warning("Aucun CV chargé. Veuillez en uploader un.")

    # ── Zone de chat ──
    if st.session_state.store is None:
        st.info("👈 Commencez par charger un CV dans la barre latérale.")
        return

    # Affiche l'historique
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Zone de saisie
    question = st.chat_input("Posez une question sur le CV...")

    if question:
        # Affiche la question utilisateur
        st.session_state.history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        # Génère la réponse
        with st.chat_message("assistant"):
            with st.spinner("Recherche en cours..."):
                answer = answer_cv_only(question, st.session_state.store)
            st.markdown(answer)

        st.session_state.history.append({"role": "assistant", "content": answer})


# ─────────────────────────────────────────────
# Point d'entrée
# ─────────────────────────────────────────────
if __name__ == "__main__":
    run_streamlit_app()