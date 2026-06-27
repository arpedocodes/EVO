# EVO

An AI-powered desktop assistant that remembers your preferences, executes tasks, and automates your PC through natural language.

---

## 🌟 Highlights

* 🧠 Persistent memory that adapts to your preferences over time
* 🖥️ Desktop automation and system control
* 🔗 Multi-step task execution from natural language commands
* 📅 Calendar management and productivity tools
* 🔍 Internet search and information retrieval
* 🧩 Extensible, tool-based architecture

---

## ℹ️ Overview

EVO is a personal AI assistant built to bridge the gap between conversational AI and practical desktop automation. Rather than just generating text, EVO can call tools, run tasks, and interact directly with your operating system to get real work done.

At its core, EVO explores a simple idea: an assistant that doesn't just respond to instructions, but *remembers* — building a picture of your preferences over time and using it to make every interaction more personal.

---

## 🎥 Demo

See EVO in action — memory, task execution, and system automation.

**Watch the demo:**

https://github.com/user-attachments/assets/39a49de2-2da9-4505-8bb2-8c5ce1d7b83c

---

## 🚀 What EVO Can Do

### 🧠 Memory System
* Stores and recalls user preferences
* Builds context across conversations
* Updates memories dynamically as things change

### 💻 System Automation
* Launches applications
* Executes system commands
* Automates desktop interactions

### 📅 Productivity Tools
* Creates, updates, searches, and deletes calendar events
* Retrieves information from the internet
* Executes Python code on demand

### 🎯 Intelligent Task Execution
* Understands natural language instructions
* Selects and uses the right tool for the job
* Executes multi-step workflows autonomously

---

## 🏗️ Architecture

```text
User Input
     │
     ▼
Language Model
     │
     ▼
Reasoning & Tool Selection
     │
     ├── Memory System
     ├── Calendar Management
     ├── Internet Search
     ├── Code Execution
     └── System Automation
     │
     ▼
Response & Action Execution
```

---

## ⬇️ Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/arpedocodes/EVO.git
cd EVO
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key
TAVILY_API_KEY=your_api_key
```

Run EVO:

```bash
python main.py
```

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Language | Python |
| LLM / Inference | OpenAI API, Ollama |
| Memory / Vector Store | ChromaDB |
| Search | Tavily Search |
| Calendar | Google Calendar API |
| Audio | SoundDevice, PyDub |
| Numerical | NumPy |

---

## 📌 Roadmap

- [ ] Improve long-term memory retrieval
- [ ] Expand system automation capabilities
- [ ] Add plugin architecture
- [ ] Improve reasoning and planning
- [ ] Cross-platform support

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
