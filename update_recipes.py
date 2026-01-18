import os, json, requests

# 깃허브 금고(Secrets)에서 꺼내오는 정보
NOTION_TOKEN = os.environ['NOTION_TOKEN']
DATABASE_ID = os.environ['NOTION_DATABASE_ID']

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_recipes():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=headers)
    
    # 만약 에러가 나면 이유를 출력합니다
    if response.status_code != 200:
        print(f"노션 연결 실패: {response.json()}")
        return

    data = response.json()
    recipes = []

    for row in data.get("results", []):
        try:
            # 사용자님의 노션 칸 이름 '레시피명'을 정확히 읽어옵니다
            name = row["properties"]["레시피명"]["title"][0]["text"]["content"]
            # 노션 페이지 자체 주소를 링크로 사용
            link = row.get("url", "#")
            recipes.append({"name": name, "link": link})
        except Exception as e:
            print(f"항목 건너뜀: {e}")
            
    with open("recipes.json", "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    get_recipes()

