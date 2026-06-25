# EVO 

An AI-powered desktop assistant that remembers user preferences, executes tasks, and automates interactions with your PC through natural language commands.

---

## 🌟 Highlights

* Persistent memory that adapts to user preferences
* Desktop automation and system control
* Multi-step task execution through natural language
* Calendar management and productivity tools
* Internet search and information retrieval
* Extensible tool-based architecture

---

## ℹ️ Overview

EVO is a personal AI assistant built to bridge the gap between conversational AI and practical desktop automation. Instead of only generating text, EVO can use tools, execute tasks, and interact with the operating system to accomplish real-world actions.

The project explores the idea of an assistant that not only responds to instructions but also remembers user preferences and uses them to provide more personalized interactions over time.

---

## 🎥 Demo

A demonstration showcasing EVO's capabilities, including memory, task execution, and system automation.

**Watch Demo:** 
https://github.com/user-attachments/assets/ccfacc27-3706-44cf-aaff-a61fe130419c

---

## 🚀 What EVO Can Do

### 🧠 Memory System

* Store and recall user preferences
* Build context across interactions
* Update memories dynamically

### 💻 System Automation

* Launch applications
* Execute system commands
* Automate desktop interactions

### 📅 Productivity Tools

* Create, update, search, and delete calendar events
* Retrieve information from the internet
* Execute Python code when required

### 🎯 Intelligent Task Execution

* Understand natural language instructions
* Select and use appropriate tools
* Execute multi-step workflows

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

```bash
git clone https://github.com/arpedocodes/EVO.git
cd EVO
pip install -r requirements.txt
```

Create a `.env` file:

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

* Python
* OpenAI API
* Ollama
* ChromaDB
* Tavily Search
* Google Calendar API
* NumPy
* SoundDevice
* PyDub

---

## 📌 Roadmap

* [ ] Improve long-term memory retrieval
* [ ] Expand system automation capabilities
* [ ] Add plugin architecture
* [ ] Improve reasoning and planning
* [ ] Cross-platform support

---

## 📄 License

This project is licensed under the [MIT LICENSE](LICENSE).
