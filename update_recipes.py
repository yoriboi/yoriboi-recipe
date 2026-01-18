import os, json, requests, re

def update_notion_recipes():
    token = os.environ.get('NOTION_TOKEN')
    database_id = os.environ.get('NOTION_DATABASE_ID')

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    print("🚀 데이터 가지러 갑니다...")
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    payload = { "page_size": 100 }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        results = []

        for page in data.get("results", []):
            try:
                props = page.get("properties", {})
                
                # 1. 제목 (이름)
                title = "제목 없음"
                for key in ["이름", "Name", "제목", "Title"]:
                    if key in props:
                        t = props[key].get("title", [])
                        if t: title = t[0]["text"]["content"]
                        break
                
                # 2. 링크 (URL) - 대소문자/한글 모두 대응
                link = "#"
                for key in ["URL", "url", "Url", "Link", "링크", "주소"]:
                    if key in props:
                        link = props[key].get("url", "#")
                        if link: break
                
                # 3. 이미지
                image = "https://ui-avatars.com/api/?name=No+Img"
                for key in ["이미지", "Image", "사진", "file"]:
                    if key in props:
                        files = props[key].get("files", [])
                        if files:
                            f = files[0]
                            image = f.get('file', {}).get('url') or f.get('external', {}).get('url')
                            break

                if link and link != "#":
                    results.append({"title": title, "link": link, "image": image})

            except Exception:
                continue

        # ⭐ [핵심 기능] #숫자 기준으로 내림차순 정렬 (최신 #30 -> 옛날 #1)
        # 숫자가 없으면 0으로 취급해서 맨 아래로 보냄
        def get_number(item):
            match = re.search(r'#(\d+)', item['title'])
            return int(match.group(1)) if match else 0
        
        # reverse=True : 큰 숫자가 위로 (30, 29, ... 1)
        results.sort(key=get_number, reverse=True)

        with open("links.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        
        print(f"🎉 정렬 완료! 총 {len(results)}개 저장됨.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    update_notion_recipes()
