# The Unofficial Guide — Project 1

## Project Title

**The Unofficial Livingstone Guide**

This project is a Retrieval-Augmented Generation (RAG) system that helps students ask natural-language questions about Livingstone College student life and receive grounded answers with source attribution.

---

## How to Run

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install requirements.

```powershell
pip install -r requirements.txt
```

3. Add a `.env` file with a Groq API key.

```txt
GROQ_API_KEY=your_key_here
```

4. Run the document pipeline.

```powershell
python src\document_pipeline.py
```

5. Run retrieval testing.

```powershell
python src\embed_retrieve.py
```

6. Run the Gradio app.

```powershell
python app.py
```

Then open:

```txt
http://127.0.0.1:7860
```

---

## Domain

My system covers Livingstone College student survival knowledge. It focuses on professors, student reviews, dining, meal plans, housing, campus life, student resources, and informal student advice.

This knowledge is valuable because official college pages do not always explain what students actually experience day to day. A student may want to know whether the campus feels supportive, what students complain about, how dining works, or what practical advice older students give. That information is spread across review sites, Reddit, official college pages, and dining pages, so a RAG system makes it easier to search and answer questions from multiple sources at once.

---

## Document Sources

| #   | Source                                   | Type                             | URL or file path                                           |
| --- | ---------------------------------------- | -------------------------------- | ---------------------------------------------------------- |
| 1   | Rate My Professors - Livingstone College | Student/professor reviews        | `documents/raw/01_rate_my_professors_livingstone.txt`      |
| 2   | Rate My Professors - Professor Search    | Professor ratings                | `documents/raw/02_rate_my_professors_professor_search.txt` |
| 3   | Niche - Livingstone College Overview     | College overview / ratings       | `documents/raw/03_niche_overview.txt`                      |
| 4   | Niche - Livingstone College Reviews      | Student reviews                  | `documents/raw/04_niche_reviews.txt`                       |
| 5   | Niche - Campus Life                      | Campus life / student polls      | `documents/raw/05_niche_campus_life.txt`                   |
| 6   | Appily - Livingstone Reviews             | Student reviews                  | `documents/raw/06_appily_reviews.txt`                      |
| 7   | Reddit r/HBCU Livingstone Thread         | Informal student advice          | `documents/raw/07_reddit_livingstone_thread.txt`           |
| 8   | Livingstone Student Affairs              | Official student resources       | `documents/raw/08_student_affairs.txt`                     |
| 9   | Livingstone Residence Life               | Official housing information     | `documents/raw/09_residence_life.txt`                      |
| 10  | Livingstone Campus Life                  | Official campus life information | `documents/raw/10_campus_life.txt`                         |
| 11  | LuxeLife Dining Meal Plans               | Dining / meal plan information   | `documents/raw/11_meal_plans.txt`                          |
| 12  | LuxeLife Dining Menu                     | Dining / food options            | `documents/raw/12_dining_menu.txt`                         |

---

## Chunking Strategy

**Chunk size:**
400 words per chunk.

**Overlap:**
75 words of overlap.

**Why these choices fit your documents:**
My documents are mostly short student reviews, official campus pages, Reddit-style advice, and dining information. I chose a word-based chunking strategy instead of a character split because word chunks are easier to inspect and keep readable. A 400-word target chunk size fits the domain because it is large enough to preserve context but still focused enough for semantic search. The 75-word overlap helps prevent important details from being lost if a topic spans a chunk boundary.

Before chunking, I cleaned each document by removing basic HTML tags, extra whitespace, and common web artifacts such as cookie banners, privacy policy text, advertisements, and “read more” text. Each chunk keeps metadata including the source file, source title, URL, source type, chunk index, and word count.

**Final chunk count:**
11 chunks.

The final chunk count is low because the collected documents are short. This is a limitation of the current corpus. In a larger production version, I would collect more full-length documents, more individual student reviews, and more official pages so retrieval has more coverage.

---

## Embedding Model

**Model used:**
`sentence-transformers/all-MiniLM-L6-v2`

**Production tradeoff reflection:**
I used `all-MiniLM-L6-v2` because it is free, runs locally, does not require an API key, and is fast enough for a small student project. It worked well for this corpus because the questions and documents were short and mostly in English.

If I were deploying this system for real users and cost were not a constraint, I would compare stronger embedding models based on retrieval accuracy, context length, latency, multilingual support, and performance on noisy student-generated text. I would also consider whether to use a hosted embedding API for better quality or keep the system local for privacy and lower cost.

---

## Grounded Generation

**System prompt grounding instruction:**
The generation step uses Groq with `llama-3.3-70b-versatile`. The system prompt tells the model:

```txt
You are a grounded RAG assistant for a student guide project.

Rules:
1. Answer using ONLY the provided retrieved document context.
2. Do NOT use outside knowledge.
3. If the retrieved context does not contain enough information, say:
   "I don't have enough information in the provided documents to answer that."
4. Be concise and helpful.
5. Mention source titles naturally in the answer when possible.
```

This prompt is designed to stop the model from answering based on general knowledge. The retrieved chunks are placed into the prompt as numbered source blocks, each with a title, file name, URL, distance score, and text.

**How source attribution is surfaced in the response:**
Source attribution is handled both in the prompt and in the interface. The model is instructed to mention source titles naturally, but the system also programmatically displays the retrieved sources in the Gradio interface. The interface shows each source title, source file, URL, and distance score in the “Retrieved from” box. This means source attribution does not depend only on the LLM remembering to cite sources.

---

## Evaluation Report

| #   | Question                                                                    | Expected answer                                                                                                              | System response (summarized)                                                                                                                                                   | Retrieval quality  | Response accuracy             |
| --- | --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------ | ----------------------------- |
| 1   | What do students say are the main strengths of Livingstone College?         | Students describe Livingstone as close-knit, supportive, family-like, full of HBCU pride, and helpful for student growth.    | The system answered that students describe Livingstone as close-knit, supportive, welcoming, diverse, and helpful for academic and personal growth. It cited Niche and Appily. | Relevant           | Accurate                      |
| 2   | What are common complaints students mention about Livingstone College?      | Common complaints include organization, housing, dining, communication, transportation, and outdated facilities.             | The system listed campus organization, communication, facilities, dining options, academic/career resources, student activities, transportation, and housing.                  | Relevant           | Accurate                      |
| 3   | What should a new student know before coming to Livingstone?                | Students should stay organized, follow up with offices, keep copies of documents, get involved, and advocate for themselves. | The system said students should expect a supportive environment, get involved, prepare for slower processes, keep financial aid documents, and advocate for themselves.        | Relevant           | Accurate                      |
| 4   | What dining or meal plan information is available for Livingstone students? | Dining documents mention meal plans, commuter plans, dining hall use, bonus points, and unused meal/refund rules.            | The system described resident and commuter meal plans, City Market, City Market Takeout, dining dollars/bonus points, and the 19-meal resident plan.                           | Relevant           | Accurate                      |
| 5   | What scholarships does Livingstone offer for computer science students?     | The documents do not contain enough information, so the system should refuse to answer.                                      | The system said it did not have enough information in the provided documents to answer.                                                                                        | Partially relevant | Accurate as a limitation case |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

The full evaluation output is saved in `evaluation_results.md`.

---

## Failure Case Analysis

**Question that failed:**
What scholarships does Livingstone offer for computer science students?

**What the system returned:**
The system returned: “I don't have enough information in the provided documents to answer that.”

**Root cause tied to a specific pipeline stage:**
This was a document coverage limitation caused by the ingestion/document collection stage. The retriever returned general Livingstone-related sources such as Reddit, Appily, Niche, and Campus Life, but none of those chunks contained specific information about computer science scholarships. The retrieved chunks were related to Livingstone College generally, but not directly related to scholarship information.

This was not a generation failure because the model correctly refused to answer instead of hallucinating. It was a corpus limitation: the raw documents did not include official financial aid pages, scholarship pages, or computer science department funding resources.

**What I would change to fix it:**
I would add official financial aid pages, scholarship documents, department-specific resources, and any student discussions about scholarships to the raw document collection. Then I would rerun the document pipeline, rebuild the ChromaDB vector store, and retest retrieval on scholarship-related questions.

---

## Spec Reflection

**One way the spec helped you during implementation:**
The planning spec helped me keep the project organized before writing code. It made me define the domain, document sources, chunking strategy, retrieval approach, evaluation questions, and architecture before building the system. This made implementation easier because each milestone had a clear purpose: first collect documents, then clean and chunk them, then embed and retrieve, then generate grounded answers.

The spec also helped me evaluate the system honestly. Since the evaluation questions were written before generation was added, I could test whether the system was actually retrieving useful chunks rather than just producing answers that sounded correct.

**One way your implementation diverged from the spec, and why:**
My planning document originally expected chunks of about 350-500 words with 75 words of overlap, and the implementation used 400-word chunks with 75-word overlap. The main divergence was that the final chunk count was much lower than expected because the collected documents were short. Most documents became one chunk each.

Another divergence was that some sources could not be scraped directly because sites like Rate My Professors and menu pages can be difficult to extract automatically. I handled this by saving clean plain-text versions of the sources into local `.txt` files, which matched the project guidance to start with plain text when scraping is difficult.

---

## AI Usage

**Instance 1**

- _What I gave the AI:_
  I gave the AI my project domain, document list, chunking strategy, and Milestone 3 requirements. I asked it to help create a document pipeline that loads raw `.txt` files, cleans text, splits documents into chunks, and saves sample chunks for inspection.

- _What it produced:_
  It produced a Python script called `document_pipeline.py` that reads files from `documents/raw`, extracts metadata, cleans text, creates overlapping chunks, writes `chunks.jsonl`, and prints sample chunks.

- _What I changed or overrode:_
  I adjusted the cleaning logic because it was initially too aggressive and skipped one of the meal plan documents. I also fixed metadata extraction so source titles appeared correctly in the sample chunks.

**Instance 2**

- _What I gave the AI:_
  I gave the AI my Retrieval Approach section, which specified `all-MiniLM-L6-v2`, ChromaDB, and top-k retrieval. I asked it to help build the embedding and retrieval pipeline for Milestone 4.

- _What it produced:_
  It produced `embed_retrieve.py`, which loads chunks from `chunks.jsonl`, embeds them using SentenceTransformers, stores them in ChromaDB with metadata, and tests retrieval on three evaluation questions.

- _What I changed or overrode:_
  I checked the retrieval output manually and confirmed that the returned chunks were relevant and had distance scores mostly below 0.5. I also decided not to commit the generated `chroma_db/` folder because it can be regenerated by running the script.

**Instance 3**

- _What I gave the AI:_
  I gave the AI the Milestone 5 requirements for grounded generation and a Gradio interface. I asked it to connect retrieval to Groq and to make sure answers only used retrieved context.

- _What it produced:_
  It produced `query.py` for grounded generation and `app.py` for the Gradio interface.

- _What I changed or overrode:_
  I made sure the source list was appended programmatically in the interface instead of relying only on the LLM to cite sources. I also tested an out-of-scope scholarship question to confirm the system refused to answer when the documents did not contain enough information.
