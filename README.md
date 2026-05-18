# CineMind — AI-Powered Movie Recommendations

CineMind is a multimodal AI movie recommendation app built with Streamlit. Describe your mood in text, speak it aloud, or upload a movie poster / mood-board image — and CineMind returns three perfectly matched film recommendations, streamed in real time and optionally read back to you via text-to-speech.

---

## Features

- **Text input** — type a mood, situation, or genre preference
- **Voice input** — record audio; Azure Speech Service transcribes it automatically
- **Image input** — upload a movie poster, scene, or mood board; Azure Computer Vision extracts visual themes, brands (Marvel, DC, Disney…), colors, and OCR text to inform recommendations
- **Streaming recommendations** — three curated films streamed token-by-token from Groq's LLaMA 3.3 70B model, each with mood rationale, a watch-if-you-liked suggestion, and an underrated-gem guarantee
- **Read aloud** — convert the full recommendation text to speech (Azure TTS) and play it in-browser
- **Conversation history** — last five sessions kept in sidebar for reference

---

## Tech Stack

| Layer | Service / Library |
|---|---|
| UI | Streamlit |
| LLM (recommendations) | Groq — `llama-3.3-70b-versatile` |
| Image analysis | Azure Cognitive Services — Computer Vision |
| Speech-to-text | Azure Cognitive Services — Speech SDK |
| Text-to-speech | Azure Cognitive Services — Speech SDK |
| Image processing | Pillow |

---

## Project Structure

```
task8hd-main/
├── app.py                  # Streamlit entry point — UI, routing, session state
├── config.py               # Reads API keys from Streamlit secrets or env vars
├── requirements.txt        # Python dependencies
├── packages.txt            # System-level packages (GStreamer for audio on Linux)
└── utils/
    ├── __init__.py
    ├── recommender.py      # Groq LLM streaming call + system prompt
    ├── vision.py           # Azure Computer Vision — analyse_image()
    └── speech.py           # Azure Speech — speech_to_text(), text_to_speech()
```

---

## Prerequisites

- Python 3.9+
- A [Groq](https://console.groq.com/) account with an API key
- An [Azure](https://portal.azure.com/) subscription with:
  - **Computer Vision** resource (key + endpoint)
  - **Speech** resource (key + region)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/cinemind.git
cd cinemind
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. (Linux only) Install GStreamer system packages

The `packages.txt` file lists the required packages:

```bash
sudo apt-get install -y libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good
```

---

## Configuration

CineMind reads credentials from **Streamlit secrets** (recommended for deployment) or **environment variables** (for local development). You need five values:

| Key | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key |
| `VISION_KEY` | Azure Computer Vision key |
| `VISION_ENDPOINT` | Azure Computer Vision endpoint URL |
| `SPEECH_KEY` | Azure Speech Service key |
| `SPEECH_REGION` | Azure Speech Service region (e.g. `eastus`) |

### Option A — Streamlit secrets (`.streamlit/secrets.toml`)

Create the file `.streamlit/secrets.toml` in the project root:

```toml
GROQ_API_KEY     = "gsk_..."
VISION_KEY       = "abc123..."
VISION_ENDPOINT  = "https://<your-resource>.cognitiveservices.azure.com/"
SPEECH_KEY       = "xyz789..."
SPEECH_REGION    = "eastus"
```

> This file is listed in `.gitignore` — never commit it.

### Option B — Environment variables

```bash
export GROQ_API_KEY="gsk_..."
export VISION_KEY="abc123..."
export VISION_ENDPOINT="https://<your-resource>.cognitiveservices.azure.com/"
export SPEECH_KEY="xyz789..."
export SPEECH_REGION="eastus"
```

---

## Running Locally

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` by default.

---

## Usage Guide

### Text mode
1. Select **💬 Text** (default).
2. Type your mood or preference (e.g. *"something tense and psychological for a late night"*).
3. Click **Get Movie Recommendations**.

### Voice mode
1. Select **🎤 Voice**.
2. Click the microphone widget and record your preference.
3. Click **Transcribe** — Azure STT converts it to text.
4. The app auto-triggers the recommendation engine as soon as transcription succeeds.

### Image mode
1. Select **🖼️ Image**.
2. Upload a JPG or PNG — a movie poster, a screenshot, or any visual mood reference.
3. (Optional) add a short text message to guide the recommendation.
4. Azure Computer Vision analyses the image for:
   - OCR text (poster title, tagline)
   - Detected brands / franchises (Marvel, DC, Disney, Star Wars…)
   - Objects, tags, dominant colors, scene category
5. Click **Get Movie Recommendations**.

### Read aloud
After any recommendation appears, click **🔊 Read Recommendations Aloud** to hear Azure TTS play the full text back in the browser.

---

## How Recommendations Work

`utils/recommender.py` sends every request to Groq's `llama-3.3-70b-versatile` model with a strict system prompt that enforces:

- Exactly **3 recommendations** per response
- A structured card format — title, year, genre, two-sentence rationale, mood-match label, and a *"watch if you liked"* pointer
- At least **one underrated/lesser-known gem** per set
- Tone-matching — the model is instructed not to force comedy when the user is sad, or arthouse when they want fun
- Image-aware context — when an image is provided, the visual description is prepended to the user message with explicit instructions to honour detected franchises and color palette

Responses are **streamed** chunk-by-chunk (`stream=True`) so the UI updates as the model generates output.

---

## Deployment on Streamlit Community Cloud

1. Push the repository to GitHub (ensure `.streamlit/secrets.toml` is in `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app pointing to `app.py`.
3. Add all five secrets in the **Secrets** panel of the Streamlit Cloud dashboard.
4. For GStreamer (needed by the Azure Speech SDK on Linux), add the contents of `packages.txt` — Streamlit Cloud reads this file automatically and installs the listed APT packages before startup.

---

## Environment Variables Reference

```
GROQ_API_KEY       — Groq console → API Keys
VISION_KEY         — Azure Portal → Computer Vision resource → Keys and Endpoint
VISION_ENDPOINT    — Azure Portal → Computer Vision resource → Keys and Endpoint
SPEECH_KEY         — Azure Portal → Speech resource → Keys and Endpoint
SPEECH_REGION      — Azure Portal → Speech resource → Location/Region
```

---

## Dependencies

**Python (`requirements.txt`)**

```
groq
azure-cognitiveservices-vision-computervision
azure-cognitiveservices-speech
streamlit
msrest
pillow
requests
```

**System (`packages.txt`) — Linux only**

```
libgstreamer1.0-0
gstreamer1.0-plugins-base
gstreamer1.0-plugins-good
```

---

## License

MIT
