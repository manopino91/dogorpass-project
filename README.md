# UFC Podcast Analyzer

## Project Overview

The UFC Podcast Analyzer is a Python-based tool designed to extract and analyze predictions from UFC-related podcasts. Utilizing the YouTube Data API and Gemini AI, this project retrieves transcripts from a specified playlist, processes the content, and extracts fighter picks and event names mentioned in each episode. The results are saved for further analysis and comparison with historical UFC fight data.

## Features

- **YouTube Data Integration**: Fetches videos from a specific YouTube playlist.
- **Transcript Extraction**: Obtains full transcripts of each video using the YouTube Transcript API.
- **AI Analysis**: Analyzes the transcript content using Gemini AI to extract fighter picks and event information.
- **Data Storage**: Saves analysis results in a CSV format for easy access and further processing.

## Technologies Used

- Python
- Google API Client
- YouTube Transcript API
- Google Generative AI (Gemini)
- Pandas for data manipulation

## Installation

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/repositoryname.git
