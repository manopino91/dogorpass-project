# UFC Podcast Analyzer

## Project Overview

The **UFC Podcast Analyzer** is a specialized Python script designed to analyze UFC podcasts, specifically the **"Dog or Pass UFC podcast"** on YouTube.

This project analyzes a YouTube podcast transcript, prompts AI Gemini to extract the winning picks and the event UFC name and saves them in a database, enabling statistical analysis
of the winning percentage once matched with historical UFC data.

With minor adjustments, it can be easily adapted to analyze other UFC-related podcasts by modifying the prompt in the **Gemini AI** settings. The script leverages
the **YouTube API** and **Gemini AI** to process content, and it automatically sets up an **SQLite database** (`ufc_analyzer.db`) to store the results for easy access and analysis.

### Key Features:

- **YouTube API Access**: Fetches podcast content from YouTube.
- **Gemini AI Analysis**: Analyzes podcast data for specific UFC-related insights.
- **Database Storage**: Stores results in an SQLite database (`ufc_analyzer.db`).
- **Environment Management**: Creates two virtual environments for dependency management:
  - One for the main script.
  - A secondary environment for data processing.



---

## Prerequisites


Before you begin, ensure you have the following:

1. **Python 3.x** installed on your machine.
2. **YouTube API** and **Gemini API** access keys.
3. Basic knowledge of working with **virtual environments** in Python.


---


## Getting Started

### Step 1: Clone the Repository

To get started, clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/ufc-podcast-analyzer.git
cd ufc-podcast-analyzer

## Step 2: Set Up Environment Variables

For security reasons, API keys and sensitive information are not included in this repository. To configure the keys, follow these steps:

1. Create a `.env` file in the `conf` directory with the following variables:

   ```env
   YOUTUBE_API_KEY=your_youtube_api_key
   GEMINI_API_KEY=your_gemini_api_key
   PLAYLIST_ID=your_youtube_playlist_id

## Step 3: Run the python script

python main_script.py


