# Aristto

Aristto is an AI assistant for scientific research. It helps researchers ask questions in natural language and get technical, citation‑grounded answers, explore individual papers, and run wide‑coverage literature reviews with strong traceability.

## What It Does
- Answers research questions with inline citations tied to specific paper excerpts.
- Runs a hybrid search pipeline that combines semantic search over passages with metadata search over titles and abstracts, including paywalled paper metadata.
- Uses a RAG pipeline over 200M+ papers with embeddings and full‑text search, tuned for crazy‑fast latency.
- Generates a conversational “thread” per topic so follow‑up questions stay grounded in prior context.
- Offers a “Deep Research” mode that expands a query into multiple search themes and synthesizes a broad literature review (hundreds of papers when filters allow).
- Applies filters for year range, citation count, specific authors, venues, and SJR quartiles to control paper quality and relevance.
- Extracts structured paper insights (summary, methodology, results, datasets, contributions, limitations) on demand.
- Enables “chat with papers” by selecting a set of papers and asking questions across their PDFs.
- Lets users save papers into collections, reopen previous searches, and chat with a collection.
- Supports accounts, email verification, password reset flows, and subscription management.

## Core Experiences

### Research Q&A With Citations
Aristto turns a user question into a focused search query, retrieves relevant contexts from large paper indices, and produces an answer where every statement is backed by inline citations. The UI renders these citations as numbered references so users can jump to the source quickly.

### Deep Research Mode
Deep Research generates multiple thematic search queries, gathers papers from a large academic index, expands the set with referenced works, and validates relevance with LLM‑based context extraction. It then produces a structured, citation‑dense literature review that favors broad coverage and balanced sourcing.

### Chat With Selected Papers
Users can move from search results to a paper‑chat view. Aristto downloads the PDFs (or falls back to abstracts), chunks them, ranks the most relevant passages, and answers questions against that focused evidence set.

### Paper Intelligence Cards
Each paper card can be expanded to show structured extracts like methodology, datasets, results, limitations, and contributions. This is useful for quick triage before diving into full text.

### Library, Collections, and Saved Searches
Papers can be saved into collections, and conversations are stored as saved searches. Users can reopen past threads or start a new chat with a collection of papers.

## How The System Works (High Level)
1. **Query understanding**: A model rewrites a user question into a searchable research query and generates a conversation title.
2. **Hybrid retrieval**: Results come from a semantic vector index (passages) and a metadata index (title + abstract), merged into a unified evidence set.
3. **Filtering**: Year range, citation count, authors, venues, and SJR quartiles are applied before synthesis.
4. **Evidence selection**: For paper chat, PDFs are chunked and ranked; for Q&A and Deep Research, abstracts and extracted contexts are prioritized.
5. **Synthesis with citations**: The LLM produces answers or literature reviews with inline citations tied to paper IDs.

## Data Sources & Indexing
- **OpenAlex** for large‑scale paper metadata (title, abstract, authors, venue, citations, DOI).
- **Semantic Scholar** for passage‑level retrieval via embeddings.
- **Azure Search** for semantic + metadata indices.
- **Optional local vector index utilities** for embedding generation and Qdrant‑based search.

## Architecture Overview
- **Backend**: Flask API providing research search, deep research, paper extraction, chat, and user/billing endpoints.
- **Frontend**: React app with a ChatGPT‑style conversational UI, filters, paper cards, library, and pricing/auth screens.
- **Storage**: MongoDB for papers, conversation history, saved searches, and collections.
- **LLM Providers**: Azure OpenAI (primary), with optional Anthropic and Vertex AI integrations.

## Demo
https://youtu.be/x72P92tjH2s
