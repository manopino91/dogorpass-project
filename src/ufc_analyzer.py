import os
import sqlite3
from dotenv import load_dotenv
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import time
from typing import List, Dict, Optional
import json
import pandas as pd

# Load environment variables from .env file
load_dotenv('../config/keys.env')

API_KEY = os.getenv('API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
PLAYLIST_ID = os.getenv('PLAYLIST_ID')  # Load Playlist ID from the .env file

class UFCPodcastAnalyzer:
    def __init__(self, youtube_api_key: str, gemini_api_key: str, playlist_id: str):
        """Initialize the analyzer with necessary API keys."""
        self.youtube = build('youtube', 'v3', developerKey=youtube_api_key)
        genai.configure(api_key=gemini_api_key)

        # Configure generation parameters
        generation_config = genai.GenerationConfig(
            temperature=0.2,
            top_p=0.8,
            top_k=40
        )
        # Initialize the model with generation config
        self.model = genai.GenerativeModel('gemini-pro', generation_config=generation_config)
        self.playlist_id = playlist_id

        # Connect to the SQLite database
        self.connection = sqlite3.connect('ufc_analysis.db')
        self.cursor = self.connection.cursor()

    def get_playlist_videos(self) -> List[Dict]:
        """Fetch all videos from the playlist."""
        videos = []
        request = self.youtube.playlistItems().list(
            part='snippet',
            playlistId=self.playlist_id,
            maxResults=50  # You can adjust the number as needed
        )

        while request is not None:
            response = request.execute()
            videos += response['items']
            request = self.youtube.playlistItems().list_next(request, response)

        return videos

    def get_transcript(self, video_id: str) -> Optional[str]:
        """Get the full transcript for a video."""
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = " ".join([entry['text'] for entry in transcript_data])
            return transcript
        except Exception as e:
            print(f"Error fetching transcript for video {video_id}: {str(e)}")
            return None

    def format_fighters(self, fighter_list: List[str]) -> Dict:
        """Format the list of fighters into the desired columnar structure."""
        fighters_dict = {}
        for index, fighter in enumerate(fighter_list, start=1):
            fighters_dict[f"fighter_{index}"] = fighter
        return fighters_dict

    def analyze_transcript(self, transcript: str) -> Dict:
        """Analyze transcript using Gemini AI to extract fighter picks and event info."""
        prompt = """
        Analyze this UFC podcast transcript and extract the following information:
        1. Which fighters were picked to win the UFC event by the guy that is being interview and asked opinions.
        2. At the end of the podcast there is a PRP section where they repeat all the winners, you can double check the results there as well.
        3. What was the UFC event name mentioned?

        Format your response as JSON with the following structure:
        {
            "fighters": {
                "fighter_1": "Fighter1",
                "fighter_2": "Fighter2",
                "fighter_3": "Fighter3",
                "fighter_4": "Fighter4",
                ...
            },
            "event_name": "UFC XXX"
        }
        If you can't find this information, return null values.
        """
        try:
            response = self.model.generate_content(transcript + "\n" + prompt)
            print("Response from Gemini AI:")
            print(response.text)

            if response.text.strip() == "":
                print("Empty response received.")
                return {"fighters": {}, "event_name": None}

            analysis_result = json.loads(response.text)

            # Handle case where fighter_picks might be in the response instead of fighters
            if "fighter_picks" in analysis_result and analysis_result["fighter_picks"]:
                formatted_fighters = self.format_fighters(analysis_result["fighter_picks"])
                analysis_result["fighters"] = formatted_fighters
            elif "fighters" not in analysis_result:
                analysis_result["fighters"] = {}

            return analysis_result

        except json.JSONDecodeError:
            print("Error decoding JSON.")
            return {"fighters": {}, "event_name": None}
        except Exception as e:
            print(f"Error calling Gemini AI: {str(e)}")
            return {"fighters": {}, "event_name": None}

    def save_to_database(self, analysis_result: Dict, video_id: str):
        """Insert analysis results into the database."""
        if analysis_result["event_name"]:
            fighters_data = ', '.join([f"{k}: {v}" for k, v in analysis_result["fighters"].items()])
            self.cursor.execute("""
                INSERT INTO podcast_analysis (video_id, event_name, fighters)
                VALUES (?, ?, ?)
            """, (video_id, analysis_result["event_name"], fighters_data))
            self.connection.commit()

    def save_results(self, results: List[Dict], filename: str = "podcast_analysis.csv"):
        """Save analysis results to a CSV file."""
        expanded_results = []
        for result in results:
            event_data = {"event_name": result["event_name"]}
            event_data.update(result["fighters"])
            expanded_results.append(event_data)

        df = pd.DataFrame(expanded_results)
        df.to_csv(filename, index=False)

    def run_analysis(self):
        """Main analysis pipeline."""
        videos = self.get_playlist_videos()
        analysis_results = []

        for video in videos:
            video_id = video['snippet']['resourceId']['videoId']
            transcript = self.get_transcript(video_id)

            if transcript:
                proceed = input(f"\nProceed with analyzing the transcript for video ID {video_id}? (y/n): ")
                if proceed.lower() != 'y':
                    print("Skipping this video.")
                    continue

                while True:
                    analysis_result = self.analyze_transcript(transcript)
                    print("AI Result:")
                    print(analysis_result)

                    like_result = input("Do you like this result? (y/n): ")
                    if like_result.lower() == 'y':
                        self.save_to_database(analysis_result, video_id)
                        analysis_results.append(analysis_result)
                        break
                    else:
                        print("Rerunning the analysis...")
                        continue

                time.sleep(2)

        self.save_results(analysis_results)
        print("\nAll analyses are complete.")

    def __del__(self):
        """Close the database connection when the instance is deleted."""
        self.connection.close()


def main():
    # Load environment variables from .env file
    load_dotenv('../config/keys.env')

    # Initialize analyzer
    analyzer = UFCPodcastAnalyzer(
        youtube_api_key=os.getenv('API_KEY'),
        gemini_api_key=os.getenv('GEMINI_API_KEY'),
        playlist_id=os.getenv('PLAYLIST_ID')
    )

    # Run analysis
    analyzer.run_analysis()


if __name__ == "__main__":
    main()

