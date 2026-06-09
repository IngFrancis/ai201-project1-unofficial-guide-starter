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

6. Run the evaluation script.

```powershell
python src\evaluate.py
```

7. Run the Gradio app.

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

| #   | Source                                   | Type                             | URL                                                                 | Local file                                                 |
| --- | ---------------------------------------- | -------------------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------- |
| 1   | Rate My Professors - Livingstone College | Student/professor reviews        | https://www.ratemyprofessors.com/school/5306                        | `documents/raw/01_rate_my_professors_livingstone.txt`      |
| 2   | Rate My Professors - Professor Search    | Professor ratings                | https://www.ratemyprofessors.com/search/professors/5306?q=*         | `documents/raw/02_rate_my_professors_professor_search.txt` |
| 3   | Niche - Livingstone College Overview     | College overview / ratings       | https://www.niche.com/colleges/livingstone-college/                 | `documents/raw/03_niche_overview.txt`                      |
| 4   | Niche - Livingstone College Reviews      | Student reviews                  | https://www.niche.com/colleges/livingstone-college/reviews/         | `documents/raw/04_niche_reviews.txt`                       |
| 5   | Niche - Campus Life                      | Campus life / student polls      | https://www.niche.com/colleges/livingstone-college/campus-life/     | `documents/raw/05_niche_campus_life.txt`                   |
| 6   | Appily - Livingstone Reviews             | Student reviews                  | https://www.appily.com/colleges/livingstone-college/reviews         | `documents/raw/06_appily_reviews.txt`                      |
| 7   | Reddit r/HBCU Livingstone Thread         | Informal student advice          | https://www.reddit.com/r/HBCU/comments/1mipw1z/livingstone_college/ | `documents/raw/07_reddit_livingstone_thread.txt`           |
| 8   | Livingstone Student Affairs              | Official student resources       | https://livingstone.edu/students/                                   | `documents/raw/08_student_affairs.txt`                     |
| 9   | Livingstone Residence Life               | Official housing information     | https://livingstone.edu/students/residence-life/                    | `documents/raw/09_residence_life.txt`                      |
| 10  | Livingstone Campus Life                  | Official campus life information | https://livingstone.edu/campus-life/                                | `documents/raw/10_campus_life.txt`                         |
| 11  | LuxeLife Dining Meal Plans               | Dining / meal plan information   | https://www.luxelifedining.com/livingstone-mealplans                | `documents/raw/11_meal_plans.txt`                          |
| 12  | LuxeLife Dining Menu                     | Dining / food options            | https://www.luxelifedining.com/livingstone-menu                     | `documents/raw/12_dining_menu.txt`                         |

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

## Sample Chunks

Below are five labeled sample chunks from the processed document collection. Each chunk keeps its source document name so retrieved answers can be traced back to the original document.

### Sample Chunk 1

**Source document:** `04_niche_reviews.txt`
**Source title:** Niche - Livingstone College Reviews

Students describe Livingstone College as a close-knit and supportive environment. Reviews mention school pride, diversity, smaller class sizes, approachable professors and staff, and opportunities for academic and personal growth. Some students also mention that the college has areas that could improve, such as communication, campus organization, housing, dining, facilities, transportation, and academic or career resources.

### Sample Chunk 2

**Source document:** `06_appily_reviews.txt`
**Source title:** Appily - Livingstone College Reviews

Student reviews on Appily describe Livingstone as a student-friendly campus with helpful staff and professors. The reviews highlight a supportive environment where students can build relationships and receive guidance. Some reviews also point out areas where the student experience could improve, including campus resources, organization, and student services.

### Sample Chunk 3

**Source document:** `07_reddit_livingstone_thread.txt`
**Source title:** Reddit r/HBCU - Livingstone College Thread

The Reddit thread gives informal advice about attending Livingstone College. It suggests that students should be prepared to advocate for themselves, keep copies of important financial aid and housing documents, and follow up when processes move slowly. The thread also encourages students to make friends and build community while understanding that some campus systems may feel underfunded or slow.

### Sample Chunk 4

**Source document:** `10_campus_life.txt`
**Source title:** Livingstone College Campus Life

The Livingstone College Campus Life source describes student life as including friendship, activities, housing, Greek life, learning communities, dining, and experiences in Salisbury. This source gives an official view of campus life and helps answer questions about student involvement and the overall campus environment.

### Sample Chunk 5

**Source document:** `11_meal_plans.txt`
**Source title:** LuxeLife Dining - Livingstone Meal Plans

The meal plan source explains that Livingstone students have access to resident and commuter meal plans. The resident meal plan shown includes 19 meals per week, and meals can be used at City Market or City Market Takeout. Commuter plans are described as convenient and budget-friendly, valid for one semester, and non-transferable.

---

## Embedding Model

**Model used:**
`sentence-transformers/all-MiniLM-L6-v2`

**Production tradeoff reflection:**
I used `all-MiniLM-L6-v2` because it is free, runs locally, does not require an API key, and is fast enough for a small student project. It worked well for this corpus because the questions and documents were short and mostly in English.

If I were deploying this system for real users and cost were not a constraint, I would compare stronger embedding models based on retrieval accuracy, context length, latency, multilingual support, and performance on noisy student-generated text. I would also consider whether to use a hosted embedding API for better quality or keep the system local for privacy and lower cost.

---

## Retrieval Test Results

I tested retrieval using three representative queries from my evaluation plan. The system returned the top chunks using ChromaDB and `all-MiniLM-L6-v2` embeddings.

### Retrieval Test 1

**Query:** What do students say are the main strengths of Livingstone College?

**Top returned chunks:**

1. `04_niche_reviews.txt` — Niche - Livingstone College Reviews — distance: 0.2499
2. `06_appily_reviews.txt` — Appily - Livingstone College Reviews — distance: 0.2702
3. `10_campus_life.txt` — Livingstone College Campus Life — distance: 0.3299
4. `07_reddit_livingstone_thread.txt` — Reddit r/HBCU - Livingstone College Thread — distance: 0.3318

**Why the returned chunks are relevant:**
The top two chunks are directly relevant because they contain student review language about Livingstone’s strengths, including support, community, helpful professors/staff, smaller classes, diversity, and campus pride. The campus life and Reddit chunks also add useful context about student life and community.

### Retrieval Test 2

**Query:** What are common complaints students mention about Livingstone College?

**Top returned chunks:**

1. `04_niche_reviews.txt` — Niche - Livingstone College Reviews — distance: 0.286
2. `06_appily_reviews.txt` — Appily - Livingstone College Reviews — distance: 0.3055
3. `07_reddit_livingstone_thread.txt` — Reddit r/HBCU - Livingstone College Thread — distance: 0.3212
4. `10_campus_life.txt` — Livingstone College Campus Life — distance: 0.4033

**Why the returned chunks are relevant:**
These chunks are relevant because they include student perspectives and informal advice, which are the best sources for complaints and lived experience. The Niche and Appily chunks directly mention concerns such as organization, communication, facilities, dining, housing, transportation, and student resources.

### Retrieval Test 3

**Query:** What dining or meal plan information is available for Livingstone students?

**Top returned chunks:**

1. `12_dining_menu.txt` — LuxeLife Dining - Livingstone Dining Menu — distance: 0.2022
2. `11_meal_plans.txt` — LuxeLife Dining - Livingstone Meal Plans — distance: 0.2834
3. `10_campus_life.txt` — Livingstone College Campus Life — distance: 0.3628
4. `07_reddit_livingstone_thread.txt` — Reddit r/HBCU - Livingstone College Thread — distance: 0.4622

**Why the returned chunks are relevant:**
The top two chunks are directly about dining and meal plans, so retrieval worked especially well for this query. The system correctly prioritized the LuxeLife Dining sources over general campus-life or student-advice sources.

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

## Example Responses

### Example Response 1

**User query:** What do students say are the main strengths of Livingstone College?

**System response:**
According to the Niche reviews page, students describe Livingstone College as close-knit, supportive, and helpful for academic and personal growth. They mention approachable professors and staff, smaller class sizes, school pride, diversity, and a welcoming environment as the main strengths. Similarly, Appily reviews also highlight the student-friendly campus environment and willing staff and professors.

**Source attribution shown:**

- Niche - Livingstone College Reviews — `04_niche_reviews.txt`
- Appily - Livingstone College Reviews — `06_appily_reviews.txt`
- Livingstone College Campus Life — `10_campus_life.txt`
- Reddit r/HBCU - Livingstone College Thread — `07_reddit_livingstone_thread.txt`

### Example Response 2

**User query:** What dining or meal plan information is available for Livingstone students?

**System response:**
According to the LuxeLife Dining meal plan document, Livingstone College offers resident and commuter meal plans that can be used at City Market or City Market Takeout. The resident plan shown is a 19-meal plan, which gives students 19 meals per week. Commuter meal plans are valid for one semester and are non-transferable. The dining menu source also mentions dining dollars or bonus points for retail locations.

**Source attribution shown:**

- LuxeLife Dining - Livingstone Dining Menu — `12_dining_menu.txt`
- LuxeLife Dining - Livingstone Meal Plans — `11_meal_plans.txt`
- Livingstone College Campus Life — `10_campus_life.txt`

### Out-of-Scope Refusal Example

**User query:** What scholarships does Livingstone offer for computer science students?

**System response:**
I don't have enough information in the provided documents to answer that.

**Why this matters:**
This shows that the system does not try to invent information when the retrieved documents do not contain the answer.

---

## Query Interface

The project uses a Gradio web interface.

**Input field:**
The user enters a natural-language question about Livingstone College student life, dining, housing, professors, or campus resources.

**Output fields:**
The interface returns two outputs:

1. **Answer** — a grounded response generated only from retrieved document context.
2. **Retrieved from** — a source list showing the source title, file name, distance score, and URL for each retrieved chunk.

### Sample Interaction Transcript

**User input:**
What should a new student know before coming to Livingstone?

**Answer output:**
Before coming to Livingstone, a new student should know that the college offers a mix of friendship, activities, housing, Greek life, learning communities, food, and local Salisbury experiences. Students describe Livingstone as close-knit and supportive, but they also mention areas that could improve, including organization and communication. Informal Reddit advice suggests that students should keep copies of financial aid documents, follow up when processes move slowly, make friends, and advocate for themselves.

**Retrieved from output:**

- Livingstone College Campus Life — `10_campus_life.txt` — distance: 0.3732
- Niche - Livingstone College Reviews — `04_niche_reviews.txt` — distance: 0.3945
- Reddit r/HBCU - Livingstone College Thread — `07_reddit_livingstone_thread.txt` — distance: 0.4162
- Appily - Livingstone College Reviews — `06_appily_reviews.txt` — distance: 0.4456

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
