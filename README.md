# ⚡ NOVA – Smart Action Agent

> **"Ask. Decide. Act."**

An autonomous, tool-calling AI agent powered by **Google Gemini** and **Streamlit**. NOVA accepts natural-language user requests, intelligently decides which specialized Python tool is needed, executes the function with live data, and synthesizes a grounded, human-readable response.

---

## 🌟 Overview

Traditional chatbots only predict text and often hallucinate when asked for real-time data, precise math, or exact string manipulations. **NOVA (Smart Action Agent)** bridges this gap by turning the Gemini Large Language Model into an autonomous decision-maker equipped with real Python tools.

Instead of hardcoded keyword rules, NOVA leverages Gemini's native **Function Calling / Tool Calling** mechanism to inspect arguments, execute Python code safely, and explain the results back to the user in natural language.

---

## 🏗️ Core Architecture & Flow

```
+-------------------------------------------------------------+
|                     1. User Request                         |
|           "What's the weather in Mumbai?"                   |
+-------------------------------------------------------------+
                              │
                              ▼
+-------------------------------------------------------------+
|             2. Gemini LLM (Autonomous Decision)            |
|       Decides required tool: get_weather(city="Mumbai")     |
+-------------------------------------------------------------+
                              │
                              ▼
+-------------------------------------------------------------+
|               3. Python Tool Execution Engine               |
|       Calls Open-Meteo API -> Coordinates -> Weather Metrics|
+-------------------------------------------------------------+
                              │
                              ▼
+-------------------------------------------------------------+
|             4. Function Result Returned to Gemini           |
|      { "temperature_c": 29.5, "condition": "Mainly clear" } |
+-------------------------------------------------------------+
                              │
                              ▼
+-------------------------------------------------------------+
|             5. Natural Language Response Synthesis          |
|    "Mumbai is currently 29.5°C with mainly clear skies..."  |
+-------------------------------------------------------------+
                              │
                              ▼
+-------------------------------------------------------------+
|                   6. Streamlit Web Dashboard                |
|    Displays Agent Activity badge + Tool Result + Response   |
+-------------------------------------------------------------+
```

---

## 🛠️ Integrated Tools

| Tool | Icon | Purpose | Key Features & Safeguards |
| :--- | :---: | :--- | :--- |
| **Calculator** | 🧮 | Mathematical calculations & percentages | Safe AST (Abstract Syntax Tree) parsing without unsafe `eval()`. Handles `+`, `-`, `*`, `/`, `%`, `**`, `//`, `()`, division by zero, and natural percentages (`25% of 840`). |
| **Weather Lookup** | 🌤️ | Real-time global weather | Two-step Open-Meteo workflow: geocoding city names to coordinates, then fetching current weather conditions, temperatures (°C/°F), wind speeds, and WMO codes. Requires no API key. |
| **Text Utility** | 📝 | String & text processing | Performs `uppercase`, `lowercase`, `word_count`, `character_count`, and `reverse`. Gracefully handles empty inputs and whitespace. |
| **GitHub Repo Info** | 🐙 | Public repository statistics | Queries public GitHub REST API for star count, forks, primary language, issues, license, and repository description. Works without authentication. |

---

## 🧪 Robust Edge Case Handling

NOVA is engineered to handle edge cases gracefully without crashing:

1. **Division by Zero (`10 / 0`)**: Safely caught by AST evaluator; returns friendly message instead of a runtime crash.
2. **Unknown Weather Cities (`xyzabcunknowncity`)**: Open-Meteo geocoding gracefully reports that coordinates could not be resolved.
3. **Nonexistent GitHub Repos (`abcxyz/not-a-real-repository`)**: Handles HTTP 404 cleanly and suggests checking spelling.
4. **Empty or Whitespace-only Text Input**: Safe defaults returned (e.g., word count = 0) without exceptions.
5. **Network / Timeout Failures**: Wrapped with timeout parameters and user-friendly error banners.
6. **Missing API Keys**: Friendly sidebar alert and instructions instead of an unhandled exception.

---

## 💻 Tech Stack

- **Language:** Python 3.10+
- **Frontend / UI:** [Streamlit](https://streamlit.io/)
- **LLM Engine:** Google Gemini (`gemini-3.7-flash` via official `google-genai` SDK)
- **APIs:** Open-Meteo Geocoding & Weather APIs, GitHub REST API
- **Testing:** `pytest`

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/nova-agent.git
cd nova-agent
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file from the provided `.env.example`:
```bash
cp .env.example .env
```
Add your Google Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
*(You can also enter your key directly inside the Streamlit sidebar during demo/testing).*

### 5. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🎯 Demo Prompts

Click any of the built-in demo buttons in the UI or type the following:

- 🌤️ **Weather:** `"What is the weather in Mumbai?"`
- 🧮 **Calculator:** `"Calculate 25% of 840"`
- 📝 **Text Utility:** `"Count the words in this sentence"`
- 🐙 **GitHub Lookup:** `"Tell me about google/gemini-api"`
- 🧪 **Edge Case:** `"Calculate 10 / 0"`

---

## 🔬 Running Unit Tests

NOVA includes a comprehensive test suite covering all tools, AST math safety, edge cases, and mocked Gemini agent workflows.

Run all tests:
```bash
python -m pytest tests -v
```

Expected output:
```
============================= 22 passed in 9.41s =============================
```

---

## 📂 Project Structure

```
nova-agent/
│
├── app.py                  # Streamlit Web UI with chat, activity badges, & demo prompts
├── agent.py                # Gemini Agent with native Function/Tool Calling & chat history
├── requirements.txt        # Minimal required dependencies
├── README.md               # Complete project documentation
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules (.env, __pycache__, etc.)
│
├── tools/
│   ├── __init__.py         # Package exports
│   ├── calculator.py       # Safe AST-based math evaluator
│   ├── weather.py          # Open-Meteo geocoding & forecast lookup
│   ├── text_utils.py       # Word/char counts, case change, string reversal
│   └── github.py           # GitHub public repository info lookup
│
└── tests/
    ├── __init__.py
    ├── test_tools.py       # 17 comprehensive unit tests for all 4 tools
    └── test_agent.py       # 5 unit tests for agent tool calling pipeline
```

---

## 🔮 Future Roadmap

- 🔍 **Web Search & Grounding Tool**: Search current live web results.
- 📁 **File & Code Execution Sandbox**: Execute Python scripts in an isolated container.
- 🧠 **Persistent Conversation Memory**: SQLite / session storage for long-term task state.
- 🎙️ **Voice Input & Output**: Bidirectional speech support via Gemini Live API.

---

## 📄 License

MIT License. Free for educational and open-source hackathon use.
