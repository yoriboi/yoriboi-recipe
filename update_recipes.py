import os, json, requests

# 깃허브 금고에서 열쇠 꺼내기
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
    data = response.json()
    
    recipes = []
    # 노션 창고의 각 줄을 하나씩 읽어옵니다
    for row in data.get("results", []):
        try:
            # ⚠️ 중요: 노션 열 이름이 '이름'과 'URL'이어야 합니다!
            name = row["properties"]["이름"]["title"][0]["text"]["content"]
            link = row["properties"].get("URL", {}).get("url", "#")
            recipes.append({"name": name, "link": link})
        except Exception as e:
            print(f"항목 건너뜀: {e}")
            
    # 읽어온 데이터를 recipes.json 파일로 저장합니다
    with open("recipes.json", "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    get_recipes()
