UFC PODCAST ANALYZER

This project is a specialized Python script designed to analyze UFC podcasts, specifically targeting the Dog or Pass UFC podcast on YouTube. With minor adjustments, it can be adapted to analyze any other UFC-related podcast by modifying the prompt in the Gemini AI settings. The script utilizes the YouTube API and Gemini AI to process content, and it automatically sets up an SQLite database (ufc_analyzer.db) to store results.
Project Overview

The script performs the following tasks:

    YouTube API Access: Fetches podcast content from YouTube.
    Gemini AI Analysis: Analyzes podcast data using Gemini AI for specific UFC-related insights.
    Database Storage: Stores results in an SQLite database (ufc_analyzer.db) for easy access and analysis.
    Environment Management: Creates two virtual environments to manage dependencies and isolate configurations:
        One primary environment for running the script.
        A secondary environment in the data folder.

Prerequisites

    Python 3.x installed on your machine.
    YouTube API and Gemini API access keys.
    Basic knowledge of working with virtual environments in Python.

Getting Started
Step 1: Clone the Repository

git clone https://github.com/yourusername/ufc-podcast-analyzer.git
cd ufc-podcast-analyzer

Step 2: Set Up Environment Variables

For security reasons, API keys and sensitive information are not included in this repository. To configure these keys:

    Create a .env file in the conf directory with the following variables:

    YOUTUBE_API_KEY=your_youtube_api_key
    GEMINI_API_KEY=your_gemini_api_key
    PLAYLIST_ID=your_youtube_playlist_id

    Replace your_youtube_api_key, your_gemini_api_key, and your_youtube_playlist_id with your actual API keys and playlist ID.

The .env file is automatically ignored in the .gitignore file, so your sensitive information will not be included in the version control.
Step 3: Set Up Virtual Environments

The project uses two virtual environments for dependency isolation:

    A main virtual environment that runs the core script.
    An additional environment in the data folder.

Create and Activate the Main Virtual Environment

To set up the main environment:

python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt

Create the Additional Environment in the data Folder

cd data
python3 -m venv data_venv
source data_venv/bin/activate  # On Windows, use `data_venv\Scripts\activate`

This additional environment can be customized if needed.
Step 4: Run the Script

Once both virtual environments are set up and activated, run the script:

python main_script.py

The script will:

    Fetch podcast data from YouTube.
    Use Gemini AI to analyze the content.
    Store the analyzed data in the ufc_analyzer.db SQLite database, which will be automatically created in the main environment.

Configuration Tips

    Customizing for Other Podcasts: To adapt the script to another podcast, simply update the prompt sent to the Gemini AI service in the code.
    Database Storage: The ufc_analyzer.db database is automatically created within the main virtual environment. You can move it or change its path as needed.

Note on Database and Security

    The SQLite database (ufc_analyzer.db) is set to auto-generate in the main virtual environment, so there's no need to manually create it.
    Sensitive API keys and other information should remain in the .env file and out of public version control. Ensure .env is listed in .gitignore.
