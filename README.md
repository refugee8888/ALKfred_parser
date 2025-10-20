🧬 ALKfred

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

GNU GENERAL PUBLIC LICENSE - The GNU General Public License is a free, copyleft license for software and other kinds of works.

👋 Final Note

ALKfred isn’t production-ready. It’s messy, it breaks, and I’m still figuring things out as I go. But it’s real, it’s important to me, and it’s how I’m learning to code.

If you want to give feedback, open an issue. If you want to build with me, fork it and send a PR. And if you just want to follow the journey, hit ⭐.

Thanks for reading.

— Paul


## 💻 Running ALKfred

ALKfred runs in a fully reproducible **Docker** environment — no manual setup needed.
Everything (Python version, dependencies, environment) is consistent across macOS, Windows, and Linux.

---

### 🐳 Quick Start (Docker Desktop or CLI)

```bash
# 1. Clone the repository
git clone https://github.com/refugee8888/ALKfred_parser.git
cd ALKfred_parser

# 2. Create your local .env file
cp src/.env.example src/.env
# (add your CIViC / OpenAI API keys, etc.)

# 3. Build the Docker image
docker compose build

# 4. Run any script, for example:
docker compose run --rm alkfred python civic_parser.py
```

#### 🧩 Notes

* Local data and databases live in `./data` and are **mounted** into `/app/data` inside the container.
* The `.env` file is **mounted read-only** into `/app/.env`.
* Nothing sensitive is baked into the image.

---

### ⚙️ Common Commands

| Task                            | Command                                                        |
| ------------------------------- | -------------------------------------------------------------- |
| Run main CLI                    | `docker compose run --rm alkfred python saver_llm_refactor.py` |
| Open interactive shell          | `docker compose run --rm alkfred bash`                         |
| Rebuild after dependency change | `docker compose build --no-cache`                              |
| Stop all containers             | `docker compose down`                                          |

---

## 🧠 Developing inside a Dev Container *(recommended for Mac + Windows)*

If you’re using **Cursor** or **VS Code**, you can develop directly inside a **Dev Container** for consistent dependencies and environment.

1. Open the project folder.
2. When prompted, click **“Reopen in Container.”**
3. Wait for the container to build (first time only).
4. Run and test your scripts normally — all dependencies are preinstalled.
5. Commit and push changes as usual (Git runs on your host filesystem).

> 💡 This ensures identical environments on macOS and Windows, while keeping your local files and Git history intact.

---

## 🧹 Maintenance

| Action                             | What to do                                                              |
| ---------------------------------- | ----------------------------------------------------------------------- |
| **Add a new dependency**           | Edit `requirements.txt` → Rebuild container                             |
| **Update Docker image**            | `docker compose build`                                                  |
| **Temporary install for testing**  | Inside container: `pip install lib` → then pin it in `requirements.txt` |
| **Clean up old containers/images** | `docker system prune`                                                   |

---

## 🔐 Security Notes

* **Never commit** your real `.env` file or actual datasets.
* Only commit `.env.example` for placeholders.
* Sensitive data stays local in `./data/` and `.env`.

