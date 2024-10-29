import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import time
from typing import List, Dict, Optional
import json

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
        self.model = genai.GenerativeModel('gemini-pro')
        self.playlist_id = playlist_id

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

        return videos  # Return the list of videos

    def get_transcript(self, video_id: str) -> Optional[str]:
        """Get the full transcript for a video."""
        try:
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = " ".join([entry['text'] for entry in transcript_data])
            return transcript  # Return the full transcript
        except Exception as e:
            print(f"Error fetching transcript for video {video_id}: {str(e)}")
            return None

    def analyze_transcript(self, transcript: str) -> Dict:
        """Analyze transcript using Gemini AI to extract fighter picks and event info."""
        prompt = """
        Analyze this UFC podcast transcript and extract the following information:
        1. Which fighters were picked to win the ufc event by Cody?
        2. What was the UFC event name mentioned?

        Format your response as JSON with the following structure:
        {
            "fighter_picks": ["Fighter1", "Fighter2"],
            "event_name": "UFC XXX"
        }

        If you can't find this information, return null values.
        """

        try:
            response = self.model.generate_content(transcript + "\n" + prompt)
            print("Response from Gemini AI:")
            print(response.text)

            return json.loads(response.text)
        except Exception as e:
            print(f"Error calling Gemini AI: {str(e)}")
            return {"fighter_picks": [], "event_name": None}

    def save_results(self, results: List[Dict], filename: str = "podcast_analysis.csv"):
        """Save analysis results to a CSV file."""
        df = pd.DataFrame(results)
        df.to_csv(filename, index=False)

    def run_analysis(self):
        """Main analysis pipeline with user confirmation and delay between analyses."""
        videos = self.get_playlist_videos()  # Fetch videos from the playlist
        analysis_results = []

        for video in videos:
            video_id = video['snippet']['resourceId']['videoId']
            transcript = self.get_transcript(video_id)

            if transcript:
                # Ask user if they want to proceed with the next analysis
                proceed = input(f"\nProceed with analyzing the transcript for video ID {video_id}? (y/n): ")
                if proceed.lower() != 'y':
                    print("Skipping this video.")
                    continue

                analysis_result = self.analyze_transcript(transcript)
                analysis_results.append(analysis_result)

                # Add delay to simulate processing time
                time.sleep(2)  # Adjust delay time as needed

        self.save_results(analysis_results)  # Save results to a CSV
        print("\nAll analyses are complete.")


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
