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
    # 최대 100개까지 가져옴
    payload = { "page_size": 100 }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        results = []

        for page in data.get("results", []):
            try:
                props = page.get("properties", {})
                
                # =====================================================
                # 🔒 [추가된 기능] 공개 여부 체크 (Checkbox)
                # "공개", "Published", "Public" 중 하나라도 컬럼이 있으면 확인
                # =====================================================
                is_published = True # 기본값: 컬럼 없으면 그냥 다 보여줌 (에러 방지)
                found_column = False

                for key in ["공개", "Published", "Public", "Status"]:
                    if key in props:
                        # 체크박스가 체크되어 있으면 True, 아니면 False
                        is_published = props[key].get("checkbox", False)
                        found_column = True
                        break
                
                # 컬럼이 존재하는데, 체크가 안 되어 있다? -> "건너뛰어!"
                if found_column and not is_published:
                    continue
                # =====================================================

                # 1. 제목 (이름)
                title = "제목 없음"
                for key in ["이름", "Name", "제목", "Title"]:
                    if key in props:
                        t = props[key].get("title", [])
                        if t: title = t[0]["text"]["content"]
                        break
                
                # 2. 링크 (URL)
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

                # 링크가 있는 것만 리스트에 추가
                if link and link != "#":
                    results.append({"title": title, "link": link, "image": image})

            except Exception:
                continue

        # ⭐ #숫자 기준으로 내림차순 정렬 (최신 #30 -> 옛날 #1)
        def get_number(item):
            match = re.search(r'#(\d+)', item['title'])
            return int(match.group(1)) if match else 0
        
        results.sort(key=get_number, reverse=True)

        with open("links.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        
        print(f"🎉 정렬 및 필터링 완료! 총 {len(results)}개 저장됨.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    update_notion_recipes()
