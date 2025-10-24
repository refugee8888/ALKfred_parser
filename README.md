nu🧬 ALKfred

Hi, I’m Paul. I don’t come from a computer science background — I actually run a small video editing business in Romania. In 2025, I decided to learn Python from scratch, and instead of going through endless tutorials, I wanted to build something that mattered to me. That’s how ALKfred was born.

I’m not an expert programmer (far from it), and a lot of this project has been me stumbling, googling, breaking code, and piecing things back together. But along the way, I’ve learned how to work with APIs, parse JSON, use ontologies, and organize code into something bigger than a toy script.

ALKfred is my attempt to create a tool that helps track and eventually predict resistance mutations in ALK-positive non-small cell lung cancer (NSCLC). Patients eventually develop resistance to ALK inhibitors, but the knowledge about which mutations cause which resistance is scattered across databases like CIViC, BioPortal, MONDO, and NCIt. ALKfred’s goal is to bring those pieces together in one place.

🚀 What it Can Do Right Now

Pull resistance evidence items from CIViC via GraphQL

Query BioPortal ontologies (still experimental)

Parse variant names, aliases, and associated diseases

Store results in JSON-based resistance rule databases

📂 Repo Structure
ALKfred/
├── data/
│   ├── curated_resistance_db.json
│   ├── mutation_resistance_db.json
│   ├── raw_bioportal_db.json
│   └── ALK_Positive_Lung_Non_Small_Cell_Cancer.json
├── src/
│   ├── data_modules/
│   │   ├── api_calls.py
│   │   ├── bioportal_parser.py
│   │   ├── bioportal_query_mini.py
│   │   └── civic_parser.py
│   ├── resistance_builder.py
│   ├── saver_llm_refactor.py
│   └── utils.py

🎯 Roadmap

This project is still in its early stages. Here’s where I’d like it to go:

 Clean up and extend BioPortal integration

 Improve parsing logic for more mutations and diseases

 Add proper unit tests (none yet)

 Build a simple API/CLI interface

 Long-term: explore predictive modeling of mutation evolution

🤝 Why I’m Sharing This

I’ve been building ALKfred mostly alone, but I’d love to hear from others. Maybe you’re a researcher, a bioinformatics dev, or just someone learning Python who wants to work on something meaningful.

If you see bad code — tell me.

If you know a better way — show me.

If you just want to hang out and talk bioinformatics/Python — even better.

Even the smallest contributions (fixing a typo, improving a README, writing one test) would mean a lot.

🛠️ Tech Stack

Python 3.12

Libraries: requests, dotenv, json

Data Sources: CIViC, BioPortal, MONDO, NCIt

📜 License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).
You may freely use, modify, and distribute ALKfred, provided all derived works remain open source under the same license.

See LICENSE for details.

⸻

🗺️ Roadmap
	•	Add MONDO + NCIT ontology enrichment (BioPortal API)
	•	CLI subcommands for query and filtering
	•	Export to parquet / CSV
	•	Add GitHub Actions for continuous testing
	•	Extend to multi-gene fetching

⸻

🧩 Maintainer

Independent Data Engineer Paul Ostaci
Maintains ETL, schema, and CLI stack for oncology data pipelines.

