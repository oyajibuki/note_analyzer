from flask import Flask, render_template, request, jsonify, send_file
import requests
import urllib.parse
import time
from datetime import datetime, timedelta
import csv
import io

app = Flask(__name__)

# JSONデータから記事情報を根こそぎ見つける関数
def find_notes_in_json(obj, found_notes, seen_keys):
    if isinstance(obj, dict):
        # 記事特有のデータ（スキ数、タイトル、キー）を持っているかチェック
        # Note API v3では likeCount ではなく like_count が返ってくる
        if "name" in obj and "key" in obj:
            # v3 APIのレスポンス構造に合わせる
            # contents配列の中身が直接対象になることが多い
            
            key = obj.get("key")
            if key not in seen_keys:
                seen_keys.add(key)
                
                author = "不明"
                urlname = ""
                # 作者情報の取得
                if "user" in obj and isinstance(obj["user"], dict):
                    author = obj["user"].get("name", "不明")
                    urlname = obj["user"].get("urlname", "")
                
                note_url = f"https://note.com/{urlname}/n/{key}" if urlname else f"https://note.com/n/{key}"
                
                # like_count または likeCount の両方を考慮（念のため）
                likes = obj.get("like_count", obj.get("likeCount", 0))
                
                # 公開日時を取得
                publish_at = obj.get("publish_at", "")

                found_notes.append({
                    "title": obj.get("name"),
                    "author": author,
                    "likes": likes,
                    "url": note_url,
                    "price": obj.get("price", 0),
                    "publish_at": publish_at
                })
        
        # さらに深い階層を探索
        for k, v in obj.items():
            find_notes_in_json(v, found_notes, seen_keys)
            
    elif isinstance(obj, list):
        for item in obj:
            find_notes_in_json(item, found_notes, seen_keys)

def get_note_ranking(keyword, duration="all"):
    encoded_word = urllib.parse.quote(keyword)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    results = []
    seen_keys = set()
    
    # ページネーション実装: 最大5ページ（250件）〜10ページ（500件）取得
    # 直近の人気記事を探すため、多めに取得する
    max_pages = 10 
    
    print(f"Searching for {keyword} with duration {duration}...")

    for page in range(max_pages):
        start = page * 50
        # sort=like でスキ数順
        url = f"https://note.com/api/v3/searches?context=note&q={encoded_word}&size=50&sort=like&start={start}"
        
        try:
            print(f"Fetching page {page+1}...")
            time.sleep(1) # サーバーへの配慮
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            json_data = response.json()
            
            initial_count = len(results)
            find_notes_in_json(json_data, results, seen_keys)
            
            # 新しい記事が見つからなければ終了
            if len(results) == initial_count:
                print("No new notes found, stopping.")
                break
                
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
    
    # 期間でフィルタリング
    filtered_results = []
    if duration == "all":
        filtered_results = results
    else:
        now = datetime.now()
        for note in results:
            if not note["publish_at"]:
                continue
                
            try:
                pub_date = datetime.fromisoformat(note["publish_at"])
                if pub_date.tzinfo is not None:
                        pub_date = pub_date.astimezone(None).replace(tzinfo=None)

                delta = now - pub_date
                
                if duration == "24h":
                    if delta <= timedelta(hours=24):
                        filtered_results.append(note)
                elif duration == "week":
                    if delta <= timedelta(days=7):
                        filtered_results.append(note)
                elif duration == "month":
                    if delta <= timedelta(days=30):
                        filtered_results.append(note)
                elif duration == "year":
                    if delta <= timedelta(days=365):
                        filtered_results.append(note)
                else:
                    filtered_results.append(note)
            except ValueError:
                pass
        
    # スキの数（likes）で降順に並び替え
    results_sorted = sorted(filtered_results, key=lambda x: x['likes'], reverse=True)
    return results_sorted

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    data = request.get_json()
    hashtag = data.get('hashtag', '')
    duration = data.get('duration', 'all')
    
    if not hashtag:
        return jsonify({"error": "キーワードが入力されていません"}), 400
        
    ranking_data = get_note_ranking(hashtag, duration)
    return jsonify({"results": ranking_data})

@app.route('/api/download_csv', methods=['POST'])
def download_csv():
    # フォームデータあるいはJSONから受け取る
    # window.location.hrefでのダウンロードパラメータ渡しはGETが無難だが、
    # 既存ロジックに合わせてPOSTで統一するか、あるいはGETクエリパラメータで実装するか。
    # ここではシンプルにフォームPOST（隠しフォーム）またはJSONボティを受け取る。
    # しかしHTML側で実装しやすいのはGETまたはフォームPOST。
    
    hashtag = request.form.get('hashtag')
    duration = request.form.get('duration', 'all')

    if not hashtag:
        # JSONリクエストの可能性も考慮（もしJSでBlob処理する場合）
        data = request.get_json(silent=True)
        if data:
            hashtag = data.get('hashtag')
            duration = data.get('duration', 'all')
            
    if not hashtag:
        return "Hashtag is required", 400

    results = get_note_ranking(hashtag, duration)
    
    # CSV生成
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['順位', 'スキ数', 'タイトル', '著者', '価格', 'URL', '公開日時'])
    
    for i, note in enumerate(results):
        cw.writerow([
            i + 1,
            note['likes'],
            note['title'],
            note['author'],
            note['price'],
            note['url'],
            note['publish_at']
        ])
        
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8-sig')) # Excelで文字化けしないようにBOM付きutf-8
    output.seek(0)
    
    filename = f"note_ranking_{duration}_{int(time.time())}.csv"
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)