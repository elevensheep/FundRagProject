import requests
from bs4 import BeautifulSoup


class NewsData:
    def __init__(self, url):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.url = url

    def get_naver_finance_news(self) -> tuple:

        response = requests.get(self.url, headers=self.headers)
        response.encoding = 'euc-kr'

        soup = BeautifulSoup(response.text, 'html.parser')

        # 뉴스 리스트 영역 추출
        news_items = soup.select('dd.articleSubject')
        news_summaries = soup.select('dd.articleSummary')
        news_title = soup.select('h3.sub_tlt')
        news_title = news_title[0].get_text().strip()
        news_list = []

        print(f"--- {news_title} ({len(news_items)}건) ---")

        for idx, item in enumerate(news_items):
            title = item.a.get_text().strip()
            link = "https://finance.naver.com" + item.a['href']
            actual_link = link.split('§')[0]

            # 같은 인덱스의 요약 정보 가져오기
            if idx < len(news_summaries):
                summary_elem = news_summaries[idx]
                # 본문 (첫 번째 텍스트)
                summary_text = summary_elem.get_text(strip=True)
                summary = summary_text.split('서울경제')[0].split('|')[0].strip()

                # 시간
                time_elem = summary_elem.select_one('span.wdate')
                time = time_elem.get_text().strip() if time_elem else ""
            else:
                summary = ""
                time = ""

            news_list.append({
                "제목": title,
                "본문": summary,
                "시간": time,
                "링크": actual_link
            })

        return news_title, news_list

