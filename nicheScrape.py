import os
import requests
from dotenv import load_dotenv
import json
import re
from typing import List, Dict

class NichePromotionFinder:
    def __init__(self, niche: str):
        """
        Initialize the promotion finder with a specific niche
        
        :param niche: The specific niche or topic to find promotion channels for
        """
        load_dotenv()  # Load environment variables from .env file
        self.niche = niche
        self.results = {
            'subreddits': [],
            'reddit_communities': [],
            'github_topics': [],
            'twitter_hashtags': [],
            'dev_communities': [],
            'youtube_channels': [],
            'quora_topics': [],
            'medium_topics': []
        }
        
        # Free API keys (you'll need to set these up)
        self.reddit_client_id = 'REDDIT_CLIENT_ID'
        self.reddit_client_secret = 'REDDIT_CLIENT_SECRET'
        self.twitter_bearer_token = 'TWITTER_BEARER_TOKEN'
        
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text for searching
        
        :param text: Input text to clean
        :return: Cleaned text
        """
        return re.sub(r'[^a-zA-Z0-9\s]', '', text.lower()).strip()
    
    def find_reddit_opportunities(self) -> Dict[str, List[str]]:
        """
        Find relevant Reddit communities and subreddits
        
        :return: Dictionary of Reddit opportunities
        """
        try:
            # Reddit OAuth flow
            auth = requests.auth.HTTPBasicAuth(
                self.reddit_client_id, 
                self.reddit_client_secret
            )
            
            # Note: You'll need to replace these with your app's details
            data = {
                'grant_type': 'client_credentials',
                'device_id': 'DO_NOT_TRACK_THIS_DEVICE'
            }
            headers = {'User-Agent': 'NichePromotionTool/1.0'}
            
            # Get access token
            token_response = requests.post(
                'https://www.reddit.com/api/v1/access_token', 
                auth=auth, 
                data=data, 
                headers=headers
            )
            token = token_response.json()['access_token']
            
            # Search for subreddits
            search_headers = {
                **headers,
                'Authorization': f'bearer {token}'
            }
            
            search_response = requests.get(
                f'https://oauth.reddit.com/subreddits/search',
                params={'q': self.niche, 'limit': 20},
                headers=search_headers
            )
            
            subreddits = [
                sub['data']['display_name'] 
                for sub in search_response.json()['data']['children']
            ]
            
            self.results['subreddits'] = subreddits
            
            # Additional Reddit-related communities
            self.results['reddit_communities'] = [
                f"{self._clean_text(self.niche)}community",
                f"{self.niche}discussions",
                f"{self.niche}hub"
            ]
            
            return {
                'subreddits': subreddits,
                'communities': self.results['reddit_communities']
            }
        
        except Exception as e:
            print(f"Error finding Reddit opportunities: {e}")
            return {}
    
    def find_github_topics(self) -> List[str]:
        """
        Find GitHub topics related to the niche
        Uses GitHub's Search API (no authentication required)
        
        :return: List of GitHub topics
        """
        try:
            # GitHub Search API is free and doesn't require authentication
            search_url = 'https://api.github.com/search/repositories'
            
            topics = []
            page = 1
            while len(topics) < 20:
                response = requests.get(search_url, params={
                    'q': f'topic:{self._clean_text(self.niche)}',
                    'sort': 'stars',
                    'order': 'desc',
                    'page': page
                })
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                new_topics = [
                    repo['full_name'].split('/')[1] 
                    for repo in data.get('items', [])
                ]
                
                topics.extend(new_topics)
                page += 1
                
                if len(data.get('items', [])) == 0:
                    break
            
            self.results['github_topics'] = list(set(topics[:20]))
            return self.results['github_topics']
        
        except Exception as e:
            print(f"Error finding GitHub topics: {e}")
            return []
    
    def find_twitter_hashtags(self) -> List[str]:
        """
        Find Twitter hashtags related to the niche
        Uses Twitter API v2
        
        :return: List of Twitter hashtags
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.twitter_bearer_token}',
                'User-Agent': 'NichePromotionTool/1.0'
            }
            
            # Search for recent tweets with the niche
            response = requests.get(
                'https://api.twitter.com/2/tweets/search/recent',
                params={'query': self.niche, 'max_results': 100},
                headers=headers
            )
            
            # Extract hashtags from tweets
            data = response.json()
            hashtags = []
            
            # Extract unique hashtags from tweets
            for tweet in data.get('data', []):
                if 'entities' in tweet and 'hashtags' in tweet['entities']:
                    hashtags.extend([
                        f"#{tag['tag']}" 
                        for tag in tweet['entities']['hashtags']
                    ])
            
            # Generate additional hashtags
            generated_hashtags = [
                f"#{self._clean_text(self.niche)}community",
                f"#{self._clean_text(self.niche)}hub",
                f"#{self._clean_text(self.niche)}lovers"
            ]
            
            # Combine and deduplicate
            all_hashtags = list(set(hashtags + generated_hashtags))
            
            self.results['twitter_hashtags'] = all_hashtags[:20]
            return self.results['twitter_hashtags']
        
        except Exception as e:
            print(f"Error finding Twitter hashtags: {e}")
            return []
    
    def find_dev_communities(self) -> List[str]:
        """
        Find developer communities related to the niche
        
        :return: List of dev community platforms
        """
        dev_platforms = [
            f"dev.to/{self._clean_text(self.niche)}",
            f"{self._clean_text(self.niche)}developers",
            f"community.{self._clean_text(self.niche)}.org"
        ]
        
        self.results['dev_communities'] = dev_platforms
        return dev_platforms
    
    def find_online_communities(self) -> Dict[str, List[str]]:
        """
        Aggregate various online community platforms
        
        :return: Dictionary of online community platforms
        """
        communities = {
            'Quora Topics': [
                f"{self.niche} Community",
                f"{self.niche} Discussions",
                f"Experts in {self.niche}"
            ],
            'Medium Topics': [
                f"{self.niche} Insights",
                f"{self.niche} Community",
                f"All About {self.niche}"
            ]
        }
        
        self.results['quora_topics'] = communities['Quora Topics']
        self.results['medium_topics'] = communities['Medium Topics']
        
        return communities
    
    def aggregate_promotion_channels(self) -> Dict[str, List[str]]:
        """
        Aggregate all found promotion channels
        
        :return: Comprehensive dictionary of promotion channels
        """
        # Call methods to populate results
        self.find_reddit_opportunities()
        self.find_github_topics()
        self.find_twitter_hashtags()
        self.find_dev_communities()
        self.find_online_communities()
        
        return self.results
    
    def export_results(self, filename: str = 'promotion_channels.json'):
        """
        Export found promotion channels to a JSON file
        
        :param filename: Name of the file to export results to
        """
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=4)
            print(f"Results exported to {filename}")
        except Exception as e:
            print(f"Error exporting results: {e}")

def main():
    # Get user input for niche
    niche = input("Enter your niche/topic for promotion research: ").strip()
    
    # Create promotion finder instance
    promotion_finder = NichePromotionFinder(niche)
    
    # Find and aggregate promotion channels
    channels = promotion_finder.aggregate_promotion_channels()
    
    # Print results
    print("\n--- Promotion Channels Found ---")
    for channel_type, items in channels.items():
        if items:
            print(f"\n{channel_type.replace('_', ' ').title()}:")
            for item in items:
                print(f"  - {item}")
    
    # Export results
    promotion_finder.export_results()

if __name__ == "__main__":
    main()