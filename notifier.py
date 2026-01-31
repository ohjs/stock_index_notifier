import yfinance as yf
import requests
import os
import json
from google.oauth2 import service_account
import google.auth.transport.requests

def get_stock_info():
    indices = {"KOSPI": "^KS11", "KOSDAQ": "^KQ11", "S&P500": "^GSPC"}
    message = "📊 오늘의 주요 지수 (11:00)\n"
    for name, ticker in indices.items():
        data = yf.Ticker(ticker).history(period="2d")
        if len(data) >= 2:
            curr = data['Close'].iloc[-1]
            prev = data['Close'].iloc[-2]
            diff = curr - prev
            per = (diff / prev) * 100
            emoji = "🔺" if diff > 0 else "🔻"
            message += f"{name}: {curr:,.2f} ({emoji}{per:.2f}%)\n"
    return message

def send_fcm_v1(title, body):
    # 1. 서비스 계정 키 설정 (GitHub Secrets에서 가져올 예정)
    service_account_info = json.loads(os.environ.get('FIREBASE_SERVICE_ACCOUNT'))
    fcm_token = os.environ.get('FCM_TOKEN')
    project_id = service_account_info['project_id']

    # 2. 구글 인증 토큰 생성
    scopes = ['https://www.googleapis.com/auth/cloud-platform']
    creds = service_account.Credentials.from_service_account_info(service_account_info, scopes=scopes)
    auth_request = google.auth.transport.requests.Request()
    creds.refresh(auth_request)
    access_token = creds.token

    # 3. 알림 전송
    url = f'https://fcm.googleapis.com/v1/projects/{project_id}/messages:send'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        "message": {
            "token": fcm_token,
            "notification": {"title": title, "body": body}
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    content = get_stock_info()
    send_fcm_v1("📈 주식 지수 도착!", content)