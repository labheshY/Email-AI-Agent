# 🤖 AI Email Responder

An automated AI-powered email assistant that reads incoming emails, classifies intent, generates replies using Gemini, and responds in real-time — all while minimizing cost and avoiding duplicate processing.

---

## 🚀 Features

* 📥 **Reads Emails** using Gmail API
* 🧠 **Intent Classification** (Support, Personal, Sales, Spam, Urgent)
* ✍️ **AI Reply Generation** using Gemini
* 🧵 **Threaded Replies** (replies inside same conversation)
* 🏷️ **Smart Labeling**

  * `AI_REPLIED`
  * `AI_SKIPPED`
  * `AI_FAILED`
* ⚡ **Cost Optimization**

  * Rule-based filtering (skip newsletters)
  * Caching (avoid repeated AI calls)
* 🔁 **Duplicate Prevention**

  * Cache + Gmail labels
* 🛡️ **Error Handling**

  * Handles API failures gracefully

---

## 🧠 System Flow

```
Incoming Email
      ↓
Rule-based Filter (skip low-value)
      ↓
AI Classification (Gemini)
      ↓
Decision Engine
      ↓
Generate Reply
      ↓
Send Email (threaded)
      ↓
Apply Label + Save Cache
```

---

## 🏗️ Project Structure

```
.
├── process_email.py       # Main pipeline
├── email_code.py          # Gmail fetching + parsing
├── classify_and_reply.py  # AI classification + reply generation
├── send_email.py          # Gmail send (threaded)
├── email_cache.json       # Local cache
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd <repo>
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Setup Gmail API

* Create project in Google Cloud
* Enable Gmail API
* Create OAuth Client (Desktop App)
* Download:

  * `credentials.json`

Generate token:

```bash
python oauth_setup.py
```

This creates:

```
token.json
```

---

### 4. Setup Environment Variables

```bash
GEMINI_API_KEY=your_api_key
```

---

### 5. Run the Agent

```bash
python process_email.py
```

---

## 🔁 Continuous Execution

The system runs in a loop:

```python
while True:
    process_emails()
    time.sleep(60)
```

👉 Checks emails every 60 seconds

---

## 🏷️ Gmail Labels

Create these labels in Gmail:

```
AI_REPLIED
AI_SKIPPED
AI_FAILED
```

Used for:

* avoiding duplicate processing
* tracking system behavior

---

## 💾 Caching Strategy

* Stores processed emails in `email_cache.json`
* Prevents:

  * duplicate replies
  * repeated AI calls
* Handles:

  * success
  * skipped
  * failed states

---

## 🔐 Security

❗ NEVER commit:

```
token.json
credentials.json
.env
```

Use:

* `.gitignore`
* environment variables

---

## ⚠️ Safety Mode (Recommended)

Before full automation:

```python
confirm = input("Send? (y/n): ")
```

👉 Prevents accidental replies during testing

---

## 🚀 Deployment

Designed to run on:

* Railway (recommended)
* AWS
* Render

---

## 🧠 Future Improvements

* Memory-based replies (context awareness)
* Priority inbox (AI ranking)
* Web dashboard
* Multi-account support
* Retry system for failed emails

---

## 📌 Key Insight

> This is not just automation — it’s an AI decision system.

---

## 👨‍💻 Author

Built as an end-to-end AI agent system combining:

* Gmail API
* Gemini AI
* Smart filtering + caching
* Production-style design

---

## ⭐ If you like this project

Give it a star ⭐ and build on top of it 🚀
