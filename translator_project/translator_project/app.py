from flask import Flask, request, render_template, jsonify
from deep_translator import GoogleTranslator
from gtts import gTTS
import io
import base64

app = Flask(__name__)

languages = {
    'en': '🇬🇧 Английский',
    'ru': '🇷🇺 Русский',
    'fr': '🇫🇷 Французский',
    'de': '🇩🇪 Немецкий',
    'es': '🇪🇸 Испанский',
    'it': '🇮🇹 Итальянский',
    'ja': '🇯🇵 Японский',
    'ko': '🇰🇷 Корейский',
    'ar': '🇸🇦 Арабский'
}

@app.route('/', methods=['GET', 'POST'])
def index():
    original_text = ""
    translated_text = ""
    source_lang = "auto"
    target_lang = "en"
    
    if request.method == 'POST':
        original_text = request.form.get('text', '')
        source_lang = request.form.get('source_lang', 'auto')
        target_lang = request.form.get('target_lang', 'en')
        
        if original_text.strip():
            try:
                translator = GoogleTranslator(source=source_lang, target=target_lang)
                translated_text = translator.translate(original_text)
            except Exception as e:
                translated_text = f"Ошибка перевода: {str(e)}"
    
    return render_template('index.html', 
                         original_text=original_text,
                         translated_text=translated_text,
                         source_lang=source_lang,
                         target_lang=target_lang,
                         languages=languages)

@app.route('/auto_translate', methods=['POST'])
def auto_translate():
    data = request.json
    text = data.get('text', '')
    source_lang = data.get('source_lang', 'auto')
    target_lang = data.get('target_lang', 'en')
    
    if not text.strip():
        return jsonify({'success': True, 'translated': ''})
    
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        return jsonify({'success': True, 'translated': translated})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/swap_all', methods=['POST'])
def swap_all():
    data = request.json
    original_text = data.get('original_text', '')
    translated_text = data.get('translated_text', '')
    source_lang = data.get('source_lang', 'auto')
    target_lang = data.get('target_lang', 'en')
    
    return jsonify({
        'success': True,
        'new_original': translated_text,
        'new_translated': original_text,
        'new_source': target_lang,
        'new_target': source_lang
    })

@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    text = data.get('text', '')
    lang = data.get('lang', 'en')
    
    if not text:
        return jsonify({'error': 'Нет текста для озвучивания'}), 400
    
    try:
        if lang == 'auto':
            lang = 'en'
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        audio_base64 = base64.b64encode(audio_bytes.read()).decode()
        return jsonify({'success': True, 'audio': audio_base64})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)