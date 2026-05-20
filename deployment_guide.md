 Deployment Guide: STRATA Market Engine

Follow this step-by-step guide to deploy your multi-agent market intelligence application for free on Streamlit Community Cloud.

Prerequisites

Before starting, ensure your local project folder has the following structure:

your-project-folder/
├── app.py                 # The core Streamlit interface
├── fetcher.py             # Data & news ingestion
├── engine.py              # Mathematical state classification
├── main.py                # Payload aggregation logic
├── llm_handler.py         # Gemini prompt & model runner
└── requirements.txt       # Cloud dependency sheet


Note: Do not upload your local .env file to GitHub! We will configure your API keys securely using the Streamlit Cloud Dashboard.

📂 Step 1: Push Code to GitHub

Log in to GitHub and create a new Public repository named strata-market-engine.

Open your terminal in your local project folder and initialize git:

git init
git add .
git commit -m "Initial commit: STRATA Market Engine build v2.5"


Link your local project to your GitHub repository and push your code:

git branch -M main
git remote add origin [https://github.com/YOUR_GITHUB_USERNAME/strata-market-engine.git](https://github.com/YOUR_GITHUB_USERNAME/strata-market-engine.git)
git push -u origin main


☁️ Step 2: Deploy on Streamlit Community Cloud

Go to share.streamlit.io and click "Sign in with GitHub".

Once logged in, click the "Create app" or "New app" button.

Configure the deployment settings:

Repository: Select your YOUR_GITHUB_USERNAME/strata-market-engine repository.

Branch: Select main.

Main file path: Set this to app.py.

Click "Deploy!" Your app will begin building. Streamlit will read your requirements.txt file and install the necessary dependencies (this typically takes 1–2 minutes on the first run).

🔑 Step 3: Configure Environment Secrets

Your application will initially show an API key error because it cannot read a local .env file. We must provide your keys securely to Streamlit:

In the bottom-right corner of your running Streamlit Cloud app page, click on "Manage app" and then select "Settings" (the gear icon).

Go to the "Secrets" tab in the settings menu.

Copy and paste your API keys and configuration values in the TOML format exactly like this:

GEMINI_API_KEY = "your-actual-api-key-here"
GEMINI_MODEL = "gemini-2.5-flash"


Click "Save".

Streamlit will automatically restart your app with the loaded credentials, and your STRATA engine will be fully live and operational!