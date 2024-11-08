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
import re

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
        try:
            self.connection = sqlite3.connect('ufc_analysis.db')
            self.cursor = self.connection.cursor()
            self._initialize_database()
        except sqlite3.Error as e:
            print(f"Database connection error: {str(e)}")
            raise

    def _initialize_database(self):
        """Initialize the database with required tables."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS podcast_analysis (
                    video_id TEXT PRIMARY KEY,
                    event_name TEXT,
                    fighters TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error initializing database: {str(e)}")
            raise

    def get_playlist_videos(self) -> List[Dict]:
        """Fetch all videos from the playlist."""
        videos = []
        try:
            request = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=self.playlist_id,
                maxResults=50
            )

            while request is not None:
                response = request.execute()
                videos += response['items']
                request = self.youtube.playlistItems().list_next(request, response)
        except Exception as e:
            print(f"Error fetching playlist videos: {str(e)}")
            return []

        return videos

    def get_video_title(self, video_id: str) -> str:
        """Retrieve the title of a video by its ID."""
        try:
            request = self.youtube.videos().list(part="snippet", id=video_id)
            response = request.execute()
            title = response["items"][0]["snippet"]["title"] if response["items"] else "Unknown Title"
            return title
        except Exception as e:
            print(f"Error fetching video title: {str(e)}")
            return "Error Fetching Title"

    def get_transcript(self, video_id: str) -> Optional[str]:
        """Get the full transcript for a video."""
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = " ".join([entry['text'] for entry in transcript_data])
            return transcript
        except Exception as e:
            print(f"Error fetching transcript for video {video_id}: {str(e)}")
            return None

    def format_fighters(self, fighter_list: List[str]) -> List[str]:
        """Format the list of fighters into the desired list structure."""
        return [fighter.strip() for fighter in fighter_list]

    def analyze_transcript(self, transcript: str, video_title: str) -> Dict:
        """Analyze transcript using Gemini AI to extract fighter picks and event info."""
        prompt = f"""
        Analyze this UFC podcast transcript titled '{video_title}' and extract the following information:
        1. Extract ONLY the fighters that Cody picked as WINNERS for each fight on the UFC card. Do not include both fighters from a matchup.
        2. Important rules for extraction:
              - For each fight matchup, only include the predicted WINNER
              - If Cody is unsure or doesn't make a clear pick, skip that fight completely
              - Do not list both fighters from the same matchup
              - Double-check the picks against the PRP (Picks Recap Portion) section at the end if available
        3. What was the UFC event name mentioned?

        Format your response as JSON with the following structure:
        {{
            "fighters": ["Fighter1", "Fighter2"],
            "event_name": "UFC XXX"
        }}
        Notes:
              - Use null if you can't find the event name
              - Only include clear, definitive picks
        """
        try:
            response = self.model.generate_content(transcript + "\n" + prompt)

            if response.text.strip() == "":
                print("Empty response received.")
                return {"fighters": [], "event_name": None}

            # Clean up the response text to ensure valid JSON
            cleaned_response = response.text.replace("```json", "").replace("```", "").strip()

            try:
                # First attempt to parse the JSON directly
                analysis_result = json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                print(f"Initial JSON parsing failed: {str(e)}")
                # If that fails, try to extract just the JSON object
                json_pattern = r'\{[\s\S]*\}'
                match = re.search(json_pattern, cleaned_response)
                if match:
                    try:
                        analysis_result = json.loads(match.group())
                    except json.JSONDecodeError:
                        print("Failed to parse extracted JSON pattern")
                        return {"fighters": [], "event_name": None}
                else:
                    print("No valid JSON pattern found in response")
                    return {"fighters": [], "event_name": None}

            # Handle case where fighter_picks might be in the response instead of fighters
            if "fighter_picks" in analysis_result and analysis_result["fighter_picks"]:
                formatted_fighters = self.format_fighters(analysis_result["fighter_picks"])
                analysis_result["fighters"] = formatted_fighters
            elif "fighters" not in analysis_result:
                analysis_result["fighters"] = []

            # Print the analysis result once
            print("Analysis Result:")
            print(json.dumps(analysis_result, indent=2))

            return analysis_result

        except Exception as e:
            print(f"Error processing response: {str(e)}")
            return {"fighters": [], "event_name": None}

    def save_to_database(self, analysis_result: Dict, video_id: str):
        """Insert analysis results into the database."""
        try:
            if analysis_result["event_name"]:
                fighters_data = ', '.join(analysis_result["fighters"])  # Store as comma-separated values
                self.cursor.execute("""
                    INSERT OR REPLACE INTO podcast_analysis (video_id, event_name, fighters)
                    VALUES (?, ?, ?)
                """, (video_id, analysis_result["event_name"], fighters_data))
                self.connection.commit()
                print("Successfully saved to database")
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
        except Exception as e:
            print(f"Error saving to database: {str(e)}")

    def save_results(self, results: List[Dict], filename: str = "podcast_analysis.csv"):
        """Save analysis results to a CSV file."""
        try:
            expanded_results = []
            for result in results:
                event_data = {"event_name": result["event_name"]}
                event_data["fighters"] = ", ".join(result["fighters"])  # Join list of fighters
                expanded_results.append(event_data)

            df = pd.DataFrame(expanded_results)
            df.to_csv(filename, index=False)
            print(f"Results successfully saved to {filename}")
        except Exception as e:
            print(f"Error saving results to CSV: {str(e)}")

    def run_analysis(self):
        """Main analysis pipeline."""
        videos = self.get_playlist_videos()
        if not videos:
            print("No videos found in playlist.")
            return

        analysis_results = []

        for video in videos:
            try:
                video_id = video['snippet']['resourceId']['videoId']
                video_title = self.get_video_title(video_id)
                print(f"\nProcessing video: {video_title}")

                transcript = self.get_transcript(video_id)
                if not transcript:
                    print("No transcript available, skipping...")
                    continue

                proceed = input(f"\nProceed with analyzing the transcript for video '{video_title}'? (y/n): ")
                if proceed.lower() != 'y':
                    continue

                analysis_result = self.analyze_transcript(transcript, video_title)
                self.save_to_database(analysis_result, video_id)

                analysis_results.append(analysis_result)

                time.sleep(2)  # Wait before processing the next video

            except Exception as e:
                print(f"Error processing video {video_id}: {str(e)}")

        self.save_results(analysis_results)

if __name__ == "__main__":
    analyzer = UFCPodcastAnalyzer(API_KEY, GEMINI_API_KEY, PLAYLIST_ID)
    analyzer.run_analysis()
