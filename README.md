# 🤖 AI Email Responder

<p align="center">
  <b>An intelligent, context-aware email assistant that actually feels human.</b><br>
  Reads emails • Understands intent • Replies smartly • Learns from conversations
</p>

---

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Gemini-AI-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Gmail-API-red?style=for-the-badge&logo=gmail" />
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" />
</p>

---

## ✨ What is this?

This is not just another automation script.
It’s a **stateful AI email agent** that:

* understands what emails mean
* decides what to do
* replies like a human
* remembers conversations

---

## 🚀 Core Capabilities

### 🧠 Intelligent Replies

* Context-aware responses (not generic templates)
* Controlled prompts → no hallucinations
* Clean, concise, human tone

---

### 🧵 Thread Memory

* Remembers last 1–2 messages per thread
* Maintains conversation flow
* Avoids repeating itself

---

### 🧹 Smart Filtering

* Detects newsletters, promos, digests
* Skips low-value emails automatically
* Saves API cost significantly

---

### 🏷️ Transparent Labeling

* `AI_REPLIED` → handled by agent
* `AI_SKIPPED` → ignored emails
* `AI_FAILED` → errors

---

### ⚡ Efficient by Design

* Cache system prevents duplicate processing
* Reduces unnecessary AI calls
* Keeps system fast and cheap

---

### 📊 Daily Summary

Every 24 hours you get:

* total emails processed
* replies sent
* skipped emails
* failures (if any)

---

## ⚙️ Configuration

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key
AUTO_REPLY=false
AUTO_DELETE_SPAM=false
```

| Variable         | Description              |
| ---------------- | ------------------------ |
| AUTO_REPLY       | Fully automate replies   |
| AUTO_DELETE_SPAM | Clean spam automatically |

---

## 🧠 How It Works

```text
Email arrives
   ↓
Smart filtering (newsletter / noreply)
   ↓
AI classification
   ↓
Decision engine
   ↓
Thread memory injected
   ↓
Reply generated
   ↓
Email sent (threaded)
   ↓
Label + cache + memory update
   ↓
Daily summary
```

---

## 🏗️ Project Structure

```bash
.
├── process_email.py        # Main pipeline
├── email_code.py           # Gmail integration
├── classify_and_reply.py   # AI logic
├── send_email.py           # Email sender
├── memory.py               # Thread memory
├── load_save_cache.py      # Cache logic
├── email_cache.json
├── thread_memory.json
├── summary_state.json
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1️⃣ Clone the repo

```bash
git clone <your-repo-url>
cd <repo>
```

---

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Setup Gmail API

* Enable Gmail API in Google Cloud
* Create OAuth client
* Download `credentials.json`

Generate token:

```bash
python auth_script.py
```

---

### 4️⃣ Run the agent

```bash
python process_email.py
```

---

## 🔁 Automation Options

* 🖥️ Local → Windows Task Scheduler
* ☁️ Cloud → Railway / Render / AWS

---

## 📌 Example

### ❌ Without memory

```text
Hi,
Thanks for reaching out...
```

### ✅ With memory

```text
Hi Labhesh,

Following up on your deployment issue, the "invalid_grant" error usually points to authentication problems.

Best regards,  
Labhesh
```

---

## 🧠 Design Philosophy

* Keep it **simple but powerful**
* Avoid unnecessary complexity (no vector DB yet)
* Optimize for **real-world usage**
* Build like a **product, not a demo**

---

## 🚀 Roadmap

* [ ] Tone learning (personal style)
* [ ] Priority inbox (AI ranking)
* [ ] Dashboard UI
* [ ] Multi-account support
* [ ] Retry system

---

## 📦 Version

**v1.0**

* Thread memory
* Smart filtering
* Logging
* Daily summary
* Gmail labeling
* Cache system

---

## 💡 Final Thought

> This started as automation…
> It’s slowly becoming a real AI assistant.

---

## ⭐ Support

If you found this useful:

⭐ Star the repo
🍴 Fork it
🚀 Build on top of it

---

<p align="center">
  Built with curiosity, debugging, and a lot of trial & error ⚡
</p>
