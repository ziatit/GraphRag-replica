# 🏗️ Microservice GraphRAG "Budget Edition" - Implementation Guide

[cite_start]Ten dokument opisuje plan budowy mikroserwisu realizującego logikę GraphRAG opisaną w paperze "From Local to Global"[cite: 2], zoptymalizowaną pod kątem kosztów i wydajności (poziom C0/C1, duże chunki).

## 1. Technology Stack

Wybór technologii podyktowany łatwością konteneryzacji i zgodnością z bibliotekami użytymi w badaniach.

* **Runtime:** `Python 3.11+` (Wymagany ze względu na typowanie i async).
* **API Framework:** `FastAPI` (Lekki, szybki, natywna obsługa asynchroniczności dla równoległych zapytań LLM).
* **Graph Engine:** `NetworkX` (Wystarczający do trzymania grafu w pamięci i serializacji do JSON/Pickle). Nie potrzebujemy Neo4j do MVP.
* [cite_start]**Community Detection:** `graspologic` lub `leidenalg` (Zgodnie z metodologią paperu: algorytm Leiden [cite: 160, 239]).
* **LLM Integration:** `OpenAI API` (lub `LiteLLM` jako warstwa abstrakcji, jeśli chcesz podpiąć lokalnego Ollama/vLLM w przyszłości).
* **Container:** `Docker` (Multi-stage build dla minimalizacji obrazu).
* **Storage:** `Local File System` (Wolumen Dockera) do trzymania zindeksowanego stanu (`graph.gml`, `community_reports.json`).

---

## 2. Architektura Mikroserwisu

Mikroserwis będzie posiadał trzy główne endpointy odpowiadające fazom z paperu:
1.  `POST /ingest` - Przyjmuje tekst, wykonuje chunking i ekstrakcję (buduje graf).
2.  `POST /build-index` - Wykonuje klastrowanie (Leiden) i generuje Community Summaries (C0/C1).
3.  `POST /query` - Obsługuje zapytania globalne metodą Map-Reduce.

---

## 3. Lista Zadań (Task List)

### Faza 0: Setup Projektu i Kontenera
- [ ] **Inicjalizacja Repo:** Struktura katalogów (`/app`, `/data`, `Dockerfile`, `requirements.txt`).
- [ ] **Docker Setup:** Przygotowanie `Dockerfile` dla Pythona.
    - *Tip:* Zadbaj o instalację kompilatorów C++ w obrazie bazowym, są potrzebne dla `leidenalg`/`igraph`.
- [ ] **Environment:** Konfiguracja `.env` (API Keys, ustawienia modelu).

### Faza 1: Ingest & Graph Extraction (Najkosztowniejsza część)
Celem jest zamiana tekstu na surowy graf. [cite_start]Optymalizacja kosztów poprzez duże chunki[cite: 502].

- [ ] **Chunking Service:** Implementacja podziału tekstu.
    - *Parametry:* Chunk size = 2400 tokenów, Overlap = 100 tokenów (optymalizacja kosztów vs recall).
- [ ] **LLM Client:** Wrapper na API (np. OpenAI) z obsługą retry/backoff (kluczowe przy dużej liczbie zapytań).
- [ ] **Entity & Relation Extraction:** Prompt inżynieria.
    - [cite_start]*Zadanie:* Zaimplementuj prompt z **Appendix E.1**.
    - [cite_start]*Optymalizacja:* Wyłącz "Self-Correction"[cite: 508], aby oszczędzić tokeny.
    - *Output:* Parsowanie odpowiedzi LLM do listy krotek `(Source, Target, Description)`.
- [ ] **Graph Builder:** Budowanie obiektu `NetworkX`.
    - *Logika:* Dodawanie węzłów i krawędzi.
    - *Entity Resolution:* Prosta normalizacja nazw (lowercase, stripping) - jeśli nazwy identyczne, scalaj opisy.

### Faza 2: Community Detection & Summarization (Tworzenie indeksu)
To tutaj powstaje "Globalna Pamięć". [cite_start]Skupiamy się tylko na wysokich poziomach (Root/C0)[cite: 225].

- [ ] **Hierarchical Clustering:** Implementacja algorytmu Leiden.
    - [cite_start]*Tool:* Użyj `graspologic.partition.hierarchical_leiden`[cite: 239].
    - *Output:* Mapa `Node ID -> Community ID` (z zachowaniem hierarchii poziomów).
- [ ] **Context Builder (do Summaries):** Logika przygotowania danych dla LLM.
    - *Algorytm:* Dla każdej społeczności zbierz jej węzły i krawędzie. [cite_start]Jeśli przekraczają limit tokenów, sortuj po `node degree` i ucinaj[cite: 172].
- [ ] **Community Summarization:** Generowanie raportów.
    - *Zakres:* Generuj **tylko dla poziomu C0 i C1** (Root i High-Level). [cite_start]Ignoruj liście (C2/C3) dla oszczędności[cite: 290].
    - [cite_start]*Prompt:* Adaptacja promptu z **Appendix E.2**.
- [ ] **Persistence:** Zapisz wygenerowane raporty do pliku JSON (`index_storage`).

### Faza 3: Query Engine (Map-Reduce)
[cite_start]Implementacja logiki "Global Search"[cite: 41, 175].

- [ ] **Map Step (Równoległa Ocena):**
    - *Input:* Zapytanie użytkownika + Lista wszystkich raportów z poziomu C0/C1.
    - *Logic:* Asynchroniczne wysłanie raportów do LLM (użyj `asyncio`).
    - [cite_start]*Prompt:* "Oceń przydatność raportu (0-100) i wyciągnij odpowiedź" (Prompt z **Appendix E.3** ).
- [ ] **Filter & Sort:**
    - *Logic:* Odrzuć odpowiedzi z `score=0`. Posortuj resztę malejąco.
- [ ] **Reduce Step (Final Answer):**
    - [cite_start]*Logic:* Sklejaj najlepsze odpowiedzi cząstkowe aż do zapełnienia Context Window (np. 8k tokenów)[cite: 183].
    - [cite_start]*Prompt:* Generowanie finalnej odpowiedzi globalnej (Prompt z **Appendix E.4** ).

### Faza 4: API & Integration
- [ ] **FastAPI Endpoints:** Spięcie logiki w kontrolery.
- [ ] **Background Tasks:** Oznaczenie endpointów indeksowania jako `BackgroundTasks` w FastAPI (indeksowanie trwa długo, nie chcemy timeoutu HTTP).
- [ ] **Logging:** Dodanie logów strukturalnych (ile tokenów zużyto, ile encji wykryto).

---

## 4. Przykładowa struktura plików

```text
/graphrag-microservice
├── Dockerfile
├── requirements.txt
├── .env
├── /app
│   ├── main.py              # Entrypoint FastAPI
│   ├── config.py            # Ustawienia (chunk size, levels)
│   ├── core/
│   │   ├── extractor.py     # Logika LLM do wyciągania encji
│   │   ├── graph.py         # Obsługa NetworkX i Leiden
│   │   ├── search.py        # Logika Map-Reduce
│   │   └── text_utils.py    # Chunking
│   ├── prompts/             # Pliki tekstowe z promptami z Appendiksów
│   └── models/              # Pydantic models (Request/Response)
└── /data                    # Wolumen na zapisany indeks