import json
from datetime import datetime
from stock_data import NewsData

if __name__ == "__main__":
    url = [
        "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258",  # 네이버금융 실시간 속보
        "https://finance.naver.com/news/mainnews.naver",  # 주요뉴스
        "https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=401",  # 시황, 전망
        "https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=402",  # 기업, 종목분석
        "https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=403",  # 해외증시
        "https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=404",  # 채권, 선물
        "https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=406",  # 공시, 메모
        "https://finance.naver.com/news/news_list.naver?mode=LSS3D&section_id=101&section_id2=258&section_id3=429",  # 환율
    ]

    all_news = {}
    for url in url:
        newsData = NewsData(url)
        news_title, newsList = newsData.get_naver_finance_news()

        all_news[news_title] = newsList

    # JSON 파일로 저장 (현재 시간 포함)
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'news_data_{current_time}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
