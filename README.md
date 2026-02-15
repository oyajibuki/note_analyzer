
# Note.com Hashtag Analyzer

A Flask web application that analyzes Note.com hashtags, sorting articles by "Likes" (スキ) and providing time-range filtering and CSV download capabilities.

## Features

-   **Sort by Likes**: Finds popular articles for a given hashtag.
-   **Deep Search**: Fetches up to 500 articles to find hidden gems.
-   **Time-Range Filtering**: Filter by Today (24h), Week, Month, Year, or All Time.
-   **CSV Download**: Export your search results for further analysis.
-   **Modern UI**: Clean and responsive interface.

## Local Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/note-analyzer.git
    cd note-analyzer
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python app.py
    ```

4.  **Access the app:**
    Open http://localhost:5000 in your browser.

## Deployment (Render)

This app is ready to be deployed on Render (free tier).

1.  Fork/Clone this repo to your GitHub.
2.  Create a new **Web Service** on Render.
3.  Connect your GitHub repo.
4.  Settings:
    -   **Runtime**: Python 3
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `gunicorn app:app`

See `deployment_guide.md` for more details.

## Disclaimer

This tool uses Note.com's unofficial API. Use responsibly and avoid sending too many requests in a short period.
