
# Note Analyzer - Deployment Guide (Render)

This guide explains how to publish your Note Analyzer tool to the web using **Render** (a free cloud hosting service).

> [!WARNING]
> **Important**: This tool uses Note.com's *unofficial* API.
> -   Running it publicly (on the web) makes it easier for Note.com to detect and block the traffic if many people use it.
> -   Use it for personal use or share with a small group of friends.

## Prerequisites

1.  **GitHub Account**: You need a GitHub account to host your code.
2.  **Render Account**: Sign up at [render.com](https://render.com/).

## Step 1: Push Code to GitHub

1.  Create a new repository on GitHub (e.g., `note-analyzer`).
2.  Upload all files from your `note_analyzer` folder to this repository.
    -   Ensure `app.py`, `Procfile`, `requirements.txt`, and the `templates` folder are included.

## Step 2: Create a Web Service on Render

1.  Log in to your Render dashboard.
2.  Click **"New +"** and select **"Web Service"**.
3.  Connect your GitHub account and select the `note-analyzer` repository you created.
4.  Configure the service:
    -   **Name**: Choose a unique name (e.g., `my-note-analyzer`).
    -   **Region**: Singapore or Oregon (pick the closest).
    -   **Branch**: `main` (or `master`).
    -   **Root Directory**: Leave blank (default).
    -   **Runtime**: **Python 3**.
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `gunicorn app:app`
5.  Select the **"Free"** plan.
6.  Click **"Create Web Service"**.

## Step 3: Wait for Deployment

1.  Render will start building your app. You can watch the logs.
2.  It may take a few minutes.
3.  Once finished, you will see "Your service is live" and a URL (e.g., `https://my-note-analyzer.onrender.com`).

## Step 4: Access Your App

Click the URL provided by Render. Your Note Analyzer is now on the web!

## Troubleshooting

-   **502 Bad Gateway**: Check the "Logs" tab in Render. It usually means the app failed to start. Ensure `Procfile` exists and contains `web: gunicorn app:app`.
-   **No Results**: Note.com might be blocking requests from Render's IP addresses. If this happens, the tool might only work locally on your PC.
