import requests
import os
import streamlit as st
import json

class YouTubeAPI:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY', 'default_key')
        self.base_url = 'https://www.googleapis.com/youtube/v3'
    
    def search_workout_videos(self, exercise_name, max_results=5):
        """Search for workout videos on YouTube"""
        try:
            # If no API key, return fallback videos
            if self.api_key == 'default_key':
                return self._get_fallback_videos(exercise_name)
            
            search_url = f"{self.base_url}/search"
            
            params = {
                'part': 'snippet',
                'q': f"{exercise_name} exercise workout tutorial",
                'type': 'video',
                'maxResults': max_results,
                'key': self.api_key,
                'videoDuration': 'short',
                'videoDefinition': 'high',
                'order': 'relevance'
            }
            
            response = requests.get(search_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                videos = []
                
                for item in data.get('items', []):
                    video = {
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'][:200] + '...',
                        'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                        'channel': item['snippet']['channelTitle'],
                        'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                        'embed_url': f"https://www.youtube.com/embed/{item['id']['videoId']}"
                    }
                    videos.append(video)
                
                return videos
            else:
                st.warning(f"YouTube API error: {response.status_code}")
                return self._get_fallback_videos(exercise_name)
                
        except Exception as e:
            st.warning(f"Error fetching YouTube videos: {str(e)}")
            return self._get_fallback_videos(exercise_name)
    
    def _get_fallback_videos(self, exercise_name):
        """Fallback video recommendations when API is not available"""
        fallback_videos = {
            'push-ups': [
                {
                    'video_id': 'IODxDxX7oi4',
                    'title': 'Perfect Push-Up Form Tutorial',
                    'description': 'Learn proper push-up technique with this comprehensive guide...',
                    'thumbnail': 'https://img.youtube.com/vi/IODxDxX7oi4/mqdefault.jpg',
                    'channel': 'Athlean-X',
                    'url': 'https://www.youtube.com/watch?v=IODxDxX7oi4',
                    'embed_url': 'https://www.youtube.com/embed/IODxDxX7oi4'
                }
            ],
            'squats': [
                {
                    'video_id': 'YaXPRqUwItQ',
                    'title': 'How to Squat Properly - Squat Tutorial',
                    'description': 'Master the perfect squat form with this detailed tutorial...',
                    'thumbnail': 'https://img.youtube.com/vi/YaXPRqUwItQ/mqdefault.jpg',
                    'channel': 'Athlean-X',
                    'url': 'https://www.youtube.com/watch?v=YaXPRqUwItQ',
                    'embed_url': 'https://www.youtube.com/embed/YaXPRqUwItQ'
                }
            ],
            'plank': [
                {
                    'video_id': 'pvIjsG5Svck',
                    'title': 'How to Plank Correctly',
                    'description': 'Perfect your plank form with these essential tips...',
                    'thumbnail': 'https://img.youtube.com/vi/pvIjsG5Svck/mqdefault.jpg',
                    'channel': 'Calisthenic Movement',
                    'url': 'https://www.youtube.com/watch?v=pvIjsG5Svck',
                    'embed_url': 'https://www.youtube.com/embed/pvIjsG5Svck'
                }
            ],
            'burpees': [
                {
                    'video_id': 'TU8QYVW0gDU',
                    'title': 'How to do a Burpee - Proper Form',
                    'description': 'Learn the correct burpee technique for maximum effectiveness...',
                    'thumbnail': 'https://img.youtube.com/vi/TU8QYVW0gDU/mqdefault.jpg',
                    'channel': 'Howcast',
                    'url': 'https://www.youtube.com/watch?v=TU8QYVW0gDU',
                    'embed_url': 'https://www.youtube.com/embed/TU8QYVW0gDU'
                }
            ]
        }
        
        # Normalize exercise name for lookup
        exercise_key = exercise_name.lower().replace('-', '').replace(' ', '')
        
        # Find matching videos
        for key, videos in fallback_videos.items():
            if key in exercise_key or exercise_key in key:
                return videos
        
        # Default fallback
        return [{
            'video_id': 'placeholder',
            'title': f'{exercise_name} Workout Tutorial',
            'description': f'Search for "{exercise_name} exercise tutorial" on YouTube for instructional videos.',
            'thumbnail': 'https://img.youtube.com/vi/placeholder/mqdefault.jpg',
            'channel': 'Fitness Tutorial',
            'url': f'https://www.youtube.com/results?search_query={exercise_name}+exercise+tutorial',
            'embed_url': None
        }]
    
    def get_playlist_videos(self, playlist_id, max_results=10):
        """Get videos from a specific playlist"""
        try:
            if self.api_key == 'default_key':
                return []
            
            playlist_url = f"{self.base_url}/playlistItems"
            
            params = {
                'part': 'snippet',
                'playlistId': playlist_id,
                'maxResults': max_results,
                'key': self.api_key
            }
            
            response = requests.get(playlist_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                videos = []
                
                for item in data.get('items', []):
                    video = {
                        'video_id': item['snippet']['resourceId']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'][:200] + '...',
                        'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                        'channel': item['snippet']['channelTitle'],
                        'url': f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}",
                        'embed_url': f"https://www.youtube.com/embed/{item['snippet']['resourceId']['videoId']}"
                    }
                    videos.append(video)
                
                return videos
            else:
                return []
                
        except Exception as e:
            st.warning(f"Error fetching playlist videos: {str(e)}")
            return []
    
    def get_workout_playlists(self, workout_type):
        """Get curated workout playlists based on workout type"""
        curated_playlists = {
            'strength': 'PLyqKj7LwU2RulAjHczohbx5OyJQ8TaFM0',
            'cardio': 'PLyqKj7LwU2RuKXlJUsRwCGsXTqgGdE9S2',
            'yoga': 'PLyqKj7LwU2RvIpYhG8cAusqfs68JfcOX6',
            'hiit': 'PLyqKj7LwU2RuP5GCl57K4T7LVJ9hA9Ypj'
        }
        
        playlist_id = curated_playlists.get(workout_type.lower())
        if playlist_id:
            return self.get_playlist_videos(playlist_id)
        
        return []

# Global instance
youtube_api = YouTubeAPI()
