import os, json, requests

def update_notion_recipes():
    token = os.environ.get('NOTION_TOKEN')
    database_id = os.environ.get('NOTION_DATABASE_ID')

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    print("🚀 노션 데이터 가져오기 시작...")
    
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    payload = { "page_size": 100 }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        if response.status_code != 200:
            print(f"❌ 노션 연결 실패! (ID/토큰 확인 필요): {data}")
            return

        results = []
        rows = data.get("results", [])
        print(f"🧐 노션에서 총 {len(rows)}개의 데이터를 발견했습니다.")

        for i, page in enumerate(rows):
            try:
                props = page.get("properties", {})
                
                # 1. 이름 가져오기
                title = "제목 없음"
                for key in ["이름", "Name", "제목", "Title", "Page"]:
                    if key in props:
                        t_list = props[key].get("title", [])
                        if t_list:
                            title = t_list[0]["text"]["content"]
                            break
                
                # 2. 링크 가져오기 (가장 중요! 유형 상관없이 다 뒤짐)
                link = "#"
                # 확인해볼 칸 이름들
                url_candidates = ["URL", "url", "Url", "LINK", "Link", "link", "링크", "주소"]
                
                for key in url_candidates:
                    if key in props:
                        # (1) 진짜 링크(url) 속성인 경우
                        if "url" in props[key]:
                            link = props[key]["url"]
                        # (2) 글자(rich_text) 속성인 경우 (여기서 많이 걸림!)
                        elif "rich_text" in props[key]:
                            txt_list = props[key]["rich_text"]
                            if txt_list:
                                link = txt_list[0]["text"]["content"]
                        
                        if link: break # 찾았으면 스톱

                # 3. 이미지 가져오기
                image = "https://ui-avatars.com/api/?name=No+Img"
                for key in ["이미지", "Image", "image", "사진", "File"]:
                    if key in props:
                        files = props[key].get("files", [])
                        if files:
                            f = files[0]
                            image = f.get('file', {}).get('url') or f.get('external', {}).get('url')
                            break

                # 저장 조건: 링크가 존재하면 저장
                if link and link != "#":
                    print(f"  ✅ [{i+1}] 저장 성공: {title}")
                    results.append({"title": title, "link": link, "image": image})
                else:
                    print(f"  ⚠️ [{i+1}] 건너뜀 (링크 없음): {title}")

            except Exception as e:
                print(f"❌ 에러 발생: {e}")
                continue

        # 파일 저장
        with open("links.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        
        print(f"🎉 크롤링 완료! 총 {len(results)}개 저장됨.")

    except Exception as e:
        print(f"❌ 시스템 에러: {e}")

if __name__ == "__main__":
    update_notion_recipes()
