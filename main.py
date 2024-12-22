from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import pandas as pd

app = FastAPI()

def fetch_air_quality_data():
    API_KEY = "ldsUnAd0IgYlk%2FQbU7ax9Sw9G3h0d3Cn2gTWiwnfwC2F8u6BplOoG2f%2FDLqvR7DM7QBVL%2B82rOS%2Fx%2B2u2EhOPA%3D%3D"
    SERVICE_URL = "http://apis.data.go.kr/B552584/UlfptcaAlarmInqireSvc/getCtprvnRltmMesureDnsty"
    
    params = {
        "serviceKey": API_KEY,
        "returnType": "json",
        "numOfRows": 10,  
        "pageNo": 1,
        "sidoName": "서울", 
        "ver": "1.0"
    }
    
    response = requests.get(SERVICE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if "response" in data and "body" in data["response"]:
            items = data["response"]["body"]["items"]
            return items
    return []

def interpret_khai_grade(grade):
    grade_dict = {
        "1": "좋음",
        "2": "보통",
        "3": "나쁨",
        "4": "매우 나쁨"
    }
    return grade_dict.get(str(grade), "N/A")

def process_air_quality_data():
    data = fetch_air_quality_data()
    if not data:
        return pd.DataFrame()
    
    processed_data = []
    for item in data:
        processed_data.append({
            "측정소": item.get("stationName", "알 수 없음"),
            "PM10 (미세먼지)": item.get("pm10Value", "N/A"),
            "PM2.5 (초미세먼지)": item.get("pm25Value", "N/A"),
            "상태": interpret_khai_grade(item.get("khaiGrade"))
        })
    
    return pd.DataFrame(processed_data)

@app.get("/", response_class=HTMLResponse)
async def show_air_quality():
    df = process_air_quality_data()
    if df.empty:
        return HTMLResponse(content="<h1>데이터를 가져올 수 없습니다.</h1>", status_code=200)

    table_html = df.to_html(index=False, escape=False, justify="center", border=1)

    html_content = f"""
    <html>
        <head>
            <title>지역별 미세먼지 정보</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; }}
                table {{ margin: 0 auto; border-collapse: collapse; width: 80%; }}
                th, td {{ padding: 10px; border: 1px solid #ddd; text-align: center; }}
                th {{ background-color: #f4f4f4; }}
            </style>
        </head>
        <body>
            <h1>지역별 미세먼지 정보</h1>
            {table_html}
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)