import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
from urllib.parse import urljoin, urlparse

# 今天
#明天
class WebContentAnalyzer:
    """網頁內容分析器"""
    
    def __init__(self, url):
        self.url = url
        self.soup = None
        self.text = ""
        
    def fetch_content(self):
        """抓取網頁內容"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            self.soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除 script 和 style 標籤
            for script in self.soup(['script', 'style']):
                script.decompose()
            
            self.text = self.soup.get_text()
            return True
        except requests.RequestException as e:
            print(f"❌ 無法抓取網頁: {e}")
            return False
    
    def get_title(self):
        """取得網頁標題"""
        if self.soup:
            title = self.soup.find('title')
            return title.string.strip() if title else "無標題"
        return None
    
    def count_words(self):
        """統計字數"""
        # 清理文本
        cleaned_text = ' '.join(self.text.split())
        # 分別統計中文字符和英文單詞
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', cleaned_text))
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', cleaned_text))
        
        return {
            'chinese_chars': chinese_chars,
            'english_words': english_words,
            'total_chars': len(cleaned_text)
        }
    
    def extract_keywords(self, top_n=10):
        """提取關鍵字（英文 + 中文，簡易詞頻統計）"""
        # 提取英文單詞
        words = re.findall(r'\b[a-zA-Z]{3,}\b', self.text.lower())
        
        # 常見英文停用詞
        en_stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 
            'can', 'her', 'was', 'one', 'our', 'out', 'this', 'that',
            'with', 'from', 'have', 'has', 'had', 'will', 'more'
        }
        # 過濾英文停用詞
        filtered_en_words = [w for w in words if w not in en_stop_words]

        # 中文斷詞，使用 jieba
        try:
            import jieba
            zh_words = list(jieba.cut(self.text))
        except ImportError:
            zh_words = []

        # 常見中文停用詞，可根據需求擴充
        zh_stop_words = set([
            "的", "了", "和", "是", "在", "也", "有", "與", "將","及", "或", "就", "都",
            "而", "及", "著", "以", "對", "由", "及其", "等", "中", "之一", "並"
        ])
        filtered_zh_words = [w for w in zh_words if w.strip() and w not in zh_stop_words and re.match(r'[\u4e00-\u9fff]+', w)]

        # 合併中英文詞彙
        all_words = filtered_en_words + filtered_zh_words

        # 統計詞頻
        word_freq = Counter(all_words)
        return word_freq.most_common(top_n)
    
    def count_links(self):
        """統計連結數量"""
        if self.soup:
            all_links = self.soup.find_all('a', href=True)
            external_links = []
            internal_links = []
            
            base_domain = urlparse(self.url).netloc
            
            for link in all_links:
                href = link.get('href')
                full_url = urljoin(self.url, href)
                link_domain = urlparse(full_url).netloc
                
                if link_domain == base_domain:
                    internal_links.append(full_url)
                elif link_domain:
                    external_links.append(full_url)
            
            return {
                'total': len(all_links),
                'internal': len(internal_links),
                'external': len(external_links)
            }
        return None
    
    def count_images(self):
        """統計圖片數量"""
        if self.soup:
            images = self.soup.find_all('img')
            return len(images)
        return 0
    
    def analyze(self):
        """執行完整分析"""
        print(f"\n🔍 正在分析: {self.url}\n")
        
        if not self.fetch_content():
            return
        
        # 標題
        title = self.get_title()
        print(f"📄 標題: {title}")
        print("=" * 60)
        
        # 字數統計
        word_count = self.count_words()
        print(f"\n📊 字數統計:")
        print(f"  • 中文字符: {word_count['chinese_chars']:,}")
        print(f"  • 英文單詞: {word_count['english_words']:,}")
        print(f"  • 總字符數: {word_count['total_chars']:,}")
        
        # 關鍵字
        keywords = self.extract_keywords()
        print(f"\n🔑 Top 10 關鍵字:")
        for i, (word, count) in enumerate(keywords, 1):
            print(f"  {i:2d}. {word:15s} ({count} 次)")
        
        # 連結統計
        links = self.count_links()
        if links:
            print(f"\n🔗 連結統計:")
            print(f"  • 總連結數: {links['total']}")
            print(f"  • 內部連結: {links['internal']}")
            print(f"  • 外部連結: {links['external']}")
        
        # 圖片統計
        image_count = self.count_images()
        print(f"\n🖼️  圖片數量: {image_count}")
        
        print("\n" + "=" * 60)
        print("✅ 分析完成！\n")


def main():
    """主程式"""
    import sys
    import os
    
    print("=" * 60)
    print("  網頁內容分析器 - Web Content Analyzer")
    print("=" * 60)
    
    # 測試用網址
    default_url = "https://www.python.org"
    
    # 優先順序：命令行參數 > 環境變數 > 互動輸入 > 預設值
    url = None
    
    # 1. 檢查命令行參數
    if len(sys.argv) > 1:
        url = sys.argv[1]
    # 2. 檢查環境變數
    elif os.getenv('TARGET_URL'):
        url = os.getenv('TARGET_URL')
    # 3. 互動輸入
    else:
        try:
            url = input(f"\n輸入要分析的網址 (直接按 Enter 使用預設: {default_url}): ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n使用預設網址: {default_url}")
            url = ""
    
    if not url:
        url = default_url
    
    # 確保網址包含協議
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # 開始分析
    analyzer = WebContentAnalyzer(url)
    analyzer.analyze()


if __name__ == "__main__":
    main()
