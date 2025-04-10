from flask import Flask, request, jsonify, render_template
import spacy
from jisho_api.word import Word
import pykakasi
import unicodedata
import httpx
import json

app = Flask(__name__)

# deeplx_api = "https://d8d0-136-142-159-111.ngrok-free.app/v2/translate"  # pro endpoint + hosted

deeplx_api = "http://127.0.0.1:1188/v2/translate" # pro endpoint + local


# deeplx_api = "http://127.0.0.1:1188/translate"  # mobile endpoint

# Load SpaCy Japanese model
nlp = spacy.load("ja_core_news_sm")

# Initialize pykakasi for kanji hiraganization
kks = pykakasi.kakasi()

# Define a mapping from UPOS tags to English POS tags
pos_mapping = {
    "NOUN": "Noun",
    "VERB": "Verb",
    "ADJ": "Adjective",
    "ADV": "Adverb",
    "PRON": "Pronoun",
    "DET": "Determiner",
    "ADP": "Adposition",
    "CONJ": "Conjunction",
    "CCONJ": "Coordinating Conjunction",
    "SCONJ": "Subordinating Conjunction",
    "NUM": "Numeral",
    "PART": "Particle",
    "AUX": "Auxiliary",
    "PUNCT": "Punctuation",
    "SYM": "Symbol",
    "INTJ": "Interjection",
    "X": "Other",
    "PROPN": "Proper Noun",
}

# Custom definitions for specific lemmas based on their grammatical role
custom_definitions = {
    "た": "past tense marker",
    "ます": "polite auxiliary verb",
    "です": "copula (to be)",
    "だ": "copula (to be)",
    "いる": "to exist (animate); to have",
    "ある": "to exist (inanimate); to have",
}



# Function to get English definition using Jisho API or custom definitions


# def get_english_definition(lemma, pos):
#     if lemma in custom_definitions:
#         return custom_definitions[lemma]
#     try:
#         result = Word.request(lemma)
#         if result and result.data:
#             return result.data[0].senses[0].english_definitions[0]
#     except Exception as e:
#         if pos != "PUNCT":
#             print(f"Error fetching definition for {lemma}: {e}")
#     return "No definition found"
def get_english_definition(lemma, pos):
    if lemma in custom_definitions:
        return custom_definitions[lemma]
    
    try:
        result = Word.request(lemma)
        if not result or not result.data:
            return "No definition found"
            
        # Build detailed output similar to terminal display
        definitions = []
        for entry in result.data:
            # Add word and reading
            word_info = f"{entry.slug} ({', '.join(entry.japanese[0].reading)})"
            if entry.jlpt:
                word_info += f" [JLPT: {entry.jlpt[0]}]"
            definitions.append(word_info)
            
            # Add all senses
            for i, sense in enumerate(entry.senses, 1):
                sense_def = f"{i}. {', '.join(sense.english_definitions)}"
                if sense.parts_of_speech:
                    sense_def += f" ({', '.join(sense.parts_of_speech)})"
                definitions.append(sense_def)
            
            definitions.append("─" * 80)  # Separator line
            
        return "\n".join(definitions)
        
    except Exception as e:
        if pos != "PUNCT":
            print(f"Error fetching definition for {lemma}: {e}")
        return "No definition found"

# Function to check if a character is hiragana
def is_hiragana(char):
    return "HIRAGANA" in unicodedata.name(char, "")


# Function to convert kanji to hiragana using pykakasi
def kanji_to_hiragana(text):
    if all(is_hiragana(char) for char in text):
        return None
    result = kks.convert(text)
    hiragana = "".join([item["hira"] for item in result])
    return hiragana

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')


# Route to handle translation and linguistic breakdown
@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    sentence = data.get('sentence', '')

    # Translate the sentence using DeepLX API PRO ENDPOINT
    translation_data = {
        "text": [sentence],
        "target_lang": "EN",
        "source_lang": "JA"
    }

    # Translate the sentence using DeepLX API MOBILE ENDPOINT
    # translation_data = {
# "text": "Hello World",
# "source_lang": "EN",
# "target_lang": "ZH"
    # }
    
    
    post_data = json.dumps(translation_data)
    
    try:
        response = httpx.post(url=deeplx_api, data=post_data)
        response_json = response.json()

        # Print the response for debugging
        print("DeepLX API Response:", response_json)

        # Check if the response contains the expected key
        if "translations" in response_json:
            translation_text = response_json["translations"][0]["text"]
        else:
            # Handle unexpected response structure
            print("Unexpected response structure:", response_json)
            translation_text = "Translation failed: Unexpected response from API."

    except Exception as e:
        # Handle any exceptions that occur during the API request
        print(f"Error during translation: {e}")
        translation_text = "Translation failed: Error contacting the API."

    # Process the sentence for linguistic breakdown
    doc = nlp(sentence)
    breakdown = []
    for token in doc:
        lemma = token.lemma_
        pos_english = pos_mapping.get(token.pos_, "UNKNOWN")
        token_hiragana = kanji_to_hiragana(token.text)
        lemma_hiragana = kanji_to_hiragana(lemma)
        if token.pos_ != "PUNCT":
            definition = get_english_definition(lemma, token.pos_)
            token_display = f"{token.text} ({token_hiragana})" if token_hiragana else token.text
            lemma_display = f"{lemma} ({lemma_hiragana})" if lemma_hiragana else lemma
            breakdown.append({
                "token": token_display,
                "lemma": lemma_display,
                "pos": pos_english,
                "definition": definition
            })

    return jsonify({
        "translation": translation_text,
        "breakdown": breakdown
    })


if __name__ == '__main__':
    app.run(debug=True)
