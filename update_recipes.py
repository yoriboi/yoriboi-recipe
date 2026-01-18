import os, json, requests

# 1. 깃허브 비밀금고에서 정보 꺼내기
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_data():
    # 2. 노션에 접속해서 데이터 달라고 요청
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = { "page_size": 100 } # 최대 100개까지 가져옴

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        
        # 연결 안 되면 에러 메시지 띄움
        if response.status_code != 200:
            print(f"❌ 노션 연결 실패: {data}")
            return

        items = []
        # 3. 받아온 데이터를 하나씩 포장하기
        for row in data.get("results", []):
            try:
                props = row.get("properties", {})
                
                # (1) 이름 가져오기
                title_list = props.get("이름", {}).get("title", [])
                title = title_list[0]["text"]["content"] if title_list else "제목 없음"
                
                # (2) URL 가져오기 (대소문자 URL 정확히 일치해야 함!)
                link = props.get("URL", {}).get("url", "#")
                
                # (3) 이미지 가져오기
                files = props.get("이미지", {}).get("files", [])
                image_url = "https://dummyimage.com/600x400/eee/aaa&text=No+Image" # 이미지 없으면 기본값
                
                if files:
                    file_obj = files[0]
                    # 노션에 직접 올린 파일인지, 외부 링크인지 확인
                    if 'file' in file_obj:
                        image_url = file_obj['file']['url']
                    elif 'external' in file_obj:
                        image_url = file_obj['external']['url']

                # 포장 완료된 상자
                items.append({ "title": title, "link": link, "image": image_url })
                
            except Exception:
                continue # 빈 칸이 있으면 건너뜀
        
        # 4. links.json 파일로 저장 (배달 준비 끝)
        with open("links.json", "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=4)
        print(f"✅ 총 {len(items)}개의 버튼을 성공적으로 가져왔습니다!")

    except Exception as e:
        print(f"❌ 시스템 에러: {e}")

if __name__ == "__main__":
    get_data()
