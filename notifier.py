import yfinance as yf
import requests
import os

def get_stock_info():
    # 대상 지수 설정
    indices = {
        "KOSPI": "^KS11",
        "KOSDAQ": "^KQ11",
        "S&P500": "^GSPC"
    }
    
    message = "📊 오늘의 주요 지수 (11:00)\n"
    for name, ticker in indices.items():
        data = yf.Ticker(ticker).history(period="2d")
        if len(data) >= 2:
            current_price = data['Close'].iloc[-1]
            prev_price = data['Close'].iloc[-2]
            change = current_price - prev_price
            change_percent = (change / prev_price) * 100
            
            emoji = "🔺" if change > 0 else "🔻"
            message += f"{name}: {current_price:,.2f} ({emoji}{change_percent:.2f}%)\n"
    
    return message

def send_fcm_notification(title, body):
    # GitHub Secrets에서 가져올 값들
    server_key = os.environ.get('FIREBASE_SERVER_KEY')
    token = os.environ.get('FCM_TOKEN')
    
    url = 'https://fcm.googleapis.com/fcm/send'
    headers = {
        'Authorization': f'key={server_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'to': token,
        'notification': {
            'title': title,
            'body': body,
            'sound': 'default'
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print(f"Notification Sent: {response.status_code}")

if __name__ == "__main__":
    content = get_stock_info()
    send_fcm_notification("📈 주식 지수 도착!", content)