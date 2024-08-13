from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
from flask_cors import CORS
import base64
import io
from PIL import Image

app = Flask(__name__, static_folder='static', static_url_path='/static')

CORS(app)

# GeminAI 설정
API_KEY = 'AIzaSyA0iOqll1uHZLLctgYyRDT10v8lbRS-DRY'
genai.configure(api_key=API_KEY)

@app.route('/')
def serve():
    return app.send_static_file('index.html')

@app.route('/generate-text', methods=['POST'])
def generate_text_story():
    data = request.json
    print(f"Received data: {data}") 
    keyword = data.get('keyword')
    mainCharacter = data.get('mainCharacter')
    genre = data.get('genre')

    if not keyword or not mainCharacter or not genre:
        return jsonify({"error": "Keyword, Main Character, and Genre are required"}), 400

    # 이야기 생성
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"제목을 '**제목:**'으로 시작하고, 이야기 본문은 '**이야기:**'로 시작하는 형식으로 {genre} 장르의 이야기를 작성해 주세요. 주인공은 {mainCharacter}, 키워드는 {keyword}입니다."
    response = model.generate_content([prompt])

    if response:
        story_parts = response.text.split('**이야기:**', 1)
        title = story_parts[0].replace('**제목:**', '').strip()
        story = story_parts[1].strip() if len(story_parts) > 1 else "No story content."
    else:
        title = "No title generated."
        story = "No story generated."
    
    return jsonify({"title": title, "story": story})


@app.route('/generate-image', methods=['POST'])
def generate_image_story():
    data = request.form

    # 이미지 처리
    image_data = data.get('image')
    if not image_data:
        return jsonify({"error": "Image file is required"}), 400
    
    # Base64 문자열에서 실제 이미지 데이터만 분리
    image_data = image_data.split(",")[1]
    
    # Base64 문자열을 바이너리로 변환
    image_bytes = base64.b64decode(image_data)
    
    # 이미지를 PIL 이미지로 변환
    image = Image.open(io.BytesIO(image_bytes))

    # 이야기 생성 로직
    mainCharacter = data.get('mainCharacter', '')
    genre = data.get('genre', '')

    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"제목을 '**제목:**'으로 시작하고, 이야기 본문은 '**이야기:**'로 시작하는 형식으로 {genre} 장르의 사진과 관련된 이야기를 작성해 주세요. 주인공은 {mainCharacter}입니다."
    response = model.generate_content([prompt, image])

    story = response.text if response else "No story generated."
    return jsonify({"story": story})

if __name__ == '__main__':
    app.run(debug=True)
