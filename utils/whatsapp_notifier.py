"""
WhatsApp Notification System for Nikkang KK EPL Competition
Supports both WhatsApp Web API and Twilio WhatsApp
"""

import requests
import json
from datetime import datetime
from typing import List, Optional

class WhatsAppNotifier:
    """
    WhatsApp notification system
    
    Supports multiple methods:
    1. WhatsApp Business API (official, requires approval)
    2. Twilio WhatsApp (easiest, $0.005 per message)
    3. WhatsApp Web URL (free, manual)
    """
    
    def __init__(self, method='url', api_key=None, account_sid=None, phone_from=None):
        """
        Initialize WhatsApp notifier
        
        Args:
            method: 'url', 'twilio', or 'business_api'
            api_key: API key for Twilio or Business API
            account_sid: Twilio account SID
            phone_from: Sending phone number (Twilio)
        """
        self.method = method
        self.api_key = api_key
        self.account_sid = account_sid
        self.phone_from = phone_from
    
    def send_whatsapp_url(self, phone: str, message: str) -> str:
        """
        Generate WhatsApp Web URL (FREE method)
        
        Args:
            phone: Recipient phone number (with country code, no +)
            message: Message text
        
        Returns:
            WhatsApp Web URL
        """
        # Format phone number (remove + and spaces)
        phone = phone.replace('+', '').replace(' ', '').replace('-', '')
        
        # URL encode message
        from urllib.parse import quote
        encoded_message = quote(message)
        
        # Generate WhatsApp Web URL
        url = f"https://wa.me/{phone}?text={encoded_message}"
        
        return url
    
    def send_via_twilio(self, phone: str, message: str) -> dict:
        """
        Send WhatsApp message via Twilio (PAID - $0.005/message)
        
        Requires:
        - Twilio account: https://www.twilio.com/console
        - WhatsApp enabled
        - Verified phone numbers
        
        Args:
            phone: Recipient phone number (format: +16505551234)
            message: Message text
        
        Returns:
            dict: Response with status
        """
        if not self.api_key or not self.account_sid or not self.phone_from:
            return {
                'success': False,
                'error': 'Twilio credentials not configured'
            }
        
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
            
            data = {
                'From': f'whatsapp:{self.phone_from}',
                'To': f'whatsapp:{phone}',
                'Body': message
            }
            
            response = requests.post(
                url,
                data=data,
                auth=(self.account_sid, self.api_key)
            )
            
            if response.status_code == 201:
                return {
                    'success': True,
                    'message_sid': response.json().get('sid'),
                    'status': 'sent'
                }
            else:
                return {
                    'success': False,
                    'error': response.json().get('message', 'Unknown error'),
                    'status_code': response.status_code
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_bulk_whatsapp_urls(self, contacts: List[dict], message: str) -> List[dict]:
        """
        Generate WhatsApp URLs for multiple contacts (FREE)
        
        Args:
            contacts: List of dicts with 'name' and 'phone'
            message: Message text
        
        Returns:
            List of dicts with 'name', 'phone', and 'url'
        """
        results = []
        
        for contact in contacts:
            url = self.send_whatsapp_url(contact['phone'], message)
            results.append({
                'name': contact.get('name', 'Unknown'),
                'phone': contact['phone'],
                'url': url
            })
        
        return results

# Message templates
class MessageTemplates:
    """Pre-defined message templates for common notifications"""
    
    @staticmethod
    def welcome_message(participant_name: str, registration_url: str) -> str:
        """Welcome message for new participants"""
        return f"""🎯 Welcome to Nikkang KK EPL Prediction Competition!

Hi {participant_name}!

You're now registered for Season 2025-26! ⚽

📱 Your Prediction Link:
{registration_url}

📋 How to Play:
• Predict 10 matches each week
• Choose your Game of the Week (double points!)
• Get 6 points for exact scores
• Get 3 points for correct results

🏆 Good luck and may the best predictor win!

- Nikkang KK Team"""
    
    @staticmethod
    def prediction_reminder(participant_name: str, week_number: int, deadline: str, url: str) -> str:
        """Reminder to submit predictions"""
        return f"""⏰ Prediction Reminder - Week {week_number}

Hi {participant_name}!

Don't forget to submit your predictions for Week {week_number}!

⏰ Deadline: {deadline}

📱 Submit Now:
{url}

🎯 Remember to choose your Game of the Week for double points!

- Nikkang KK Team"""
    
    @staticmethod
    def results_posted(participant_name: str, week_number: int, points: int, rank: int, url: str) -> str:
        """Notify when results are posted"""
        return f"""📊 Week {week_number} Results Posted!

Hi {participant_name}!

Your Week {week_number} results:
• Points: {points} 🎯
• Current Rank: #{rank} 📈

📊 View Full Leaderboard:
{url}

Keep up the great predictions! ⚽

- Nikkang KK Team"""
    
    @staticmethod
    def weekly_winner(participant_name: str, week_number: int, points: int, url: str) -> str:
        """Congratulate weekly winner"""
        return f"""🏆 Congratulations! Week {week_number} Winner!

Hi {participant_name}!

🎉 YOU WON WEEK {week_number}! 🎉

Your amazing performance:
• Points: {points} 🌟
• Top score of the week! 👑

📊 View Leaderboard:
{url}

Incredible predictions! Keep it up! ⚽

- Nikkang KK Team"""
    
    @staticmethod
    def season_summary(participant_name: str, total_points: int, final_rank: int, exact_scores: int, url: str) -> str:
        """End of season summary"""
        return f"""🏁 Season 2025-26 Complete!

Hi {participant_name}!

What a season! Here's your summary:

📊 Your Stats:
• Total Points: {total_points} 🎯
• Final Rank: #{final_rank} 📈
• Exact Scores: {exact_scores} 🎪

🏆 View Final Standings:
{url}

Thank you for participating!
See you next season! ⚽

- Nikkang KK Team"""
    
    @staticmethod
    def admin_new_registration(admin_name: str, participant_name: str, total_participants: int) -> str:
        """Notify admin of new registration"""
        return f"""👤 New Registration

Hi {admin_name},

New participant registered:
• Name: {participant_name}
• Total Participants: {total_participants}

- Nikkang KK Admin System"""
    
    @staticmethod
    def admin_all_predictions_submitted(admin_name: str, week_number: int, total_predictions: int) -> str:
        """Notify admin when all predictions are in"""
        return f"""✅ All Predictions Submitted

Hi {admin_name},

Week {week_number} - All predictions received!
• Total: {total_predictions} participants

Ready for results entry.

- Nikkang KK Admin System"""


# Integration helpers
def send_welcome_notifications(participants: List[dict], base_url: str, method='url') -> List[dict]:
    """
    Send welcome messages to new participants
    
    Args:
        participants: List of dicts with 'name', 'phone', 'id'
        base_url: Base URL of the app
        method: 'url' or 'twilio'
    
    Returns:
        List of notification results
    """
    notifier = WhatsAppNotifier(method=method)
    results = []
    
    for participant in participants:
        registration_url = f"{base_url}?user_id={participant['id']}"
        message = MessageTemplates.welcome_message(
            participant['name'],
            registration_url
        )
        
        if method == 'url':
            url = notifier.send_whatsapp_url(participant['phone'], message)
            results.append({
                'name': participant['name'],
                'phone': participant['phone'],
                'url': url,
                'method': 'url'
            })
        elif method == 'twilio':
            response = notifier.send_via_twilio(participant['phone'], message)
            results.append({
                'name': participant['name'],
                'phone': participant['phone'],
                'response': response,
                'method': 'twilio'
            })
    
    return results


def send_prediction_reminders(participants: List[dict], week_number: int, deadline: str, base_url: str, method='url') -> List[dict]:
    """
    Send prediction reminders to all participants
    
    Args:
        participants: List of dicts with 'name', 'phone', 'id'
        week_number: Current week number
        deadline: Deadline string (e.g., "Saturday 3:00 PM")
        base_url: Base URL of the app
        method: 'url' or 'twilio'
    
    Returns:
        List of notification results
    """
    notifier = WhatsAppNotifier(method=method)
    results = []
    
    for participant in participants:
        prediction_url = f"{base_url}?user_id={participant['id']}"
        message = MessageTemplates.prediction_reminder(
            participant['name'],
            week_number,
            deadline,
            prediction_url
        )
        
        if method == 'url':
            url = notifier.send_whatsapp_url(participant['phone'], message)
            results.append({
                'name': participant['name'],
                'phone': participant['phone'],
                'url': url,
                'method': 'url'
            })
        elif method == 'twilio':
            response = notifier.send_via_twilio(participant['phone'], message)
            results.append({
                'name': participant['name'],
                'phone': participant['phone'],
                'response': response,
                'method': 'twilio'
            })
    
    return results


# Example usage
if __name__ == "__main__":
    # Example 1: Generate WhatsApp URL (FREE)
    notifier = WhatsAppNotifier(method='url')
    
    url = notifier.send_whatsapp_url(
        phone='16505551234',  # Country code + number (no +)
        message='Hello! This is a test from Nikkang KK EPL Competition!'
    )
    print(f"WhatsApp URL: {url}")
    
    # Example 2: Bulk WhatsApp URLs
    contacts = [
        {'name': 'John Doe', 'phone': '16505551234'},
        {'name': 'Jane Smith', 'phone': '16505555678'},
    ]
    
    results = notifier.send_bulk_whatsapp_urls(
        contacts=contacts,
        message='Welcome to the competition!'
    )
    
    for result in results:
        print(f"{result['name']}: {result['url']}")
    
    # Example 3: Using Twilio (requires credentials)
    # notifier = WhatsAppNotifier(
    #     method='twilio',
    #     account_sid='YOUR_ACCOUNT_SID',
    #     api_key='YOUR_AUTH_TOKEN',
    #     phone_from='+14155238886'  # Your Twilio WhatsApp number
    # )
    # 
    # response = notifier.send_via_twilio(
    #     phone='+16505551234',
    #     message='Test message via Twilio'
    # )
    # print(response)
