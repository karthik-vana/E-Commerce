# 🛍️ ShopMind AI — E-Commerce Chatbot

> **Production-grade AI shopping assistant powered by Groq LPU Inference**

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LPU_Inference-6366f1?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-10b981?style=for-the-badge)

</div>

# 🛒 ShopMind AI – E‑Commerce App

🔗 **Live Demo:** [https://e-commerce1.streamlit.app](https://e-commerce1.streamlit.app)

---

## ✨ Overview

**ShopMind AI** is an intelligent e-commerce chatbot that delivers smart product recommendations, order tracking, price comparisons, and policy guidance — all powered by state-of-the-art LLMs running on Groq's ultra-fast LPU inference engine.

### Key Highlights

- 🤖 **9 AI Models** — LLaMA 3.3 70B, Qwen 3 32B, Kimi K2, GPT OSS, Gemma 2, Mixtral, and more
- ⚡ **Sub-2-second responses** via Groq's LPU inference
- 🎭 **6 Personas** — Friendly, Professional, Expert, Concise, Luxury Concierge, Qwen Mode
- 🌐 **14 Languages** supported
- 🛡️ **Enterprise security** — input sanitisation, prompt injection defence, rate limiting
- 📊 **Real-time metrics** — response timer, session stats, word counter

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🔍 Product Discovery | Smart recommendations based on budget, preferences, and use case |
| 📦 Order Tracking | Step-by-step guidance for tracking orders |
| ⚖️ Price Comparison | Side-by-side product comparisons with pros/cons |
| ↩️ Returns & Refunds | Clear policy guidance and return process walkthrough |
| 🎁 Gift Suggestions | Curated gift ideas within any budget |
| 💳 Payment Info | Supported payment methods and EMI options |
| 🚚 Shipping Details | Delivery timelines and shipping policies |
| ⚡ Quick Presets | One-click Fast, Quality, Expert, Qwen, Creative, and Safe modes |

---

## 🤖 Available Models

| Model | Provider | Context | Best For |
|-------|----------|---------|----------|
| 🦙 LLaMA 3.3 70B Versatile | Meta | 128K | Best overall quality |
| ⚡ LLaMA 3.1 8B Instant | Meta | 131K | Ultra-fast responses |
| 🧠 Qwen 3 32B | Alibaba | 32K | Reasoning & multilingual |
| 🛡️ GPT OSS Safeguard 20B | OpenAI | 16K | Safety-focused |
| 🌙 Kimi K2 Instruct | Moonshot AI | 131K | Instruction following |
| 💎 Gemma 2 9B IT | Google | 8K | Balanced performance |
| 🔀 Mixtral 8x7B | Mistral | 32K | MoE architecture |
| 🦙 LLaMA 3 70B | Meta | 8K | Classic 70B power |
| 🏃 LLaMA 3 8B | Meta | 8K | Lightweight queries |

---

## 🏗️ Architecture

```
ShopMind AI
├── app.py                      # Streamlit entry point
├── config.py                   # Central configuration & model registry
├── src/
│   ├── api/
│   │   └── groq_client.py      # Groq REST client (retry, timeout, fallback)
│   ├── prompts/
│   │   └── ecommerce_prompts.py # Prompt engine, personas, few-shot examples
│   ├── services/
│   │   ├── chat_service.py     # Request pipeline & model orchestration
│   │   └── session_service.py  # Session state management
│   ├── ui/
│   │   └── components.py       # Premium dark UI with glassmorphism
│   └── utils/
│       ├── logger.py           # Rotating file + console logging
│       └── security.py         # Input sanitisation & rate limiting
├── .streamlit/
│   └── config.toml             # Streamlit theme configuration
├── requirements.txt
└── .env.example
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ecommerce-chatbot.git
cd ecommerce-chatbot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and add your Groq API key
```

### 4. Run locally

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 🌐 Deployment (Streamlit Cloud)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path**: `app.py`
5. In **Advanced Settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   GROQ_MODEL = "llama-3.3-70b-versatile"
   ```
6. Click **Deploy**

---

## 🛡️ Security

- **Input sanitisation** — HTML tags, JS injection, and prompt injection patterns are stripped
- **Domain guardrail** — Only e-commerce queries are processed; off-topic requests are politely declined
- **Rate limiting** — 30 requests per minute per session
- **No hardcoded secrets** — All API keys loaded from environment variables

---

## 📄 License

This project is open source under the [MIT License](LICENSE).

---

<div align="center">
  <strong>Built with ❤️ using Streamlit & Groq</strong>
</div>
