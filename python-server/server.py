from flask import Flask, request, jsonify
import random
from threading import Lock
LOCK = Lock()

from translate import translate_lines
from align import align_sentence, replace_words

wordcount = 0
def replace_sentences(sentences, src_word_list=set(), tgt_word_list=set()):
    """
    Replace words in a list of sentences with their translations.
    src_word_list is the set of the words in the source language you want to have replaced,
    and tgt_word_list is the set of words in the target language you want to show up. 
    """
    print("Total sentences =", len(sentences))
    import time
    start = time.time()
    translations = translate_lines(sentences)
    print("time to translate:", time.time() - start)
    start = time.time()
    alignments = [align_sentence(sentence, translation) for sentence, translation in zip(sentences, translations)]
    print("time to align translation:", time.time() - start)

    # tgt_words = [word for sent_src, sent_tgt, align_words in alignments for word, _ in sent_tgt]
    # global wordcount
    # wordcount += len(tgt_words)
    # print("word count at", wordcount)
    # if wordcount >= 1000:
    #     tgt_words = set(tgt_words) - tgt_word_list
    #     new_word = random.choice(tuple(tgt_words))
    #     new_word = new_word.strip().lower()
    #     with open("../de_words.txt", 'a', encoding='utf-8') as f:
    #         f.write(new_word + "\n")
    #     tgt_word_list.add(new_word)
    #     wordcount = 0

    start = time.time()
    new_sentences = [replace_words(*a, src_word_list=src_word_list, tgt_word_list=tgt_word_list)
                        for a in alignments]
    print("time to reconstruct:", time.time() - start)
    start = time.time()
    new_sentences = [sent.strip() for sent in new_sentences]
    return new_sentences

with open("../en_words.txt", 'r', encoding="utf-8") as f:
    src_word_list = {word.strip() for word in f.readlines() if word.strip()}
with open("../de_words.txt", 'r', encoding="utf-8") as f:
    tgt_word_list = {word.strip() for word in f.readlines() if word.strip()}

#print(replace_sentences(["The most important thing was to stay on the premises."], src_word_list, tgt_word_list))
#exit()
app = Flask(__name__)
@app.route('/set_src_list', methods=['POST'])
def set_src_list():
    global src_word_list
    data = request.get_json()
    if isinstance(data, list) and all(isinstance(item, str) for item in data):
        src_word_list = {s.lower() for s in data}
        return 'List stored successfully!'
    else:
        return jsonify({'error': 'Invalid list format. Please provide a list of strings.'}), 400

@app.route('/set_tgt_list', methods=['POST'])
def set_tgt_list():
    global tgt_word_list
    data = request.get_json()
    if isinstance(data, list) and all(isinstance(item, str) for item in data):
        tgt_word_list = {s.lower() for s in data}
        return 'List stored successfully!'
    else:
        return jsonify({'error': 'Invalid list format. Please provide a list of strings.'}), 400

@app.route('/replace_sentences', methods=['POST'])
def replace_sentences_():
    try:
        LOCK.acquire()
        input_list = request.get_json()["sentences"]
        if isinstance(input_list, list) and all(isinstance(item, str) for item in input_list):
            sentences = [s.strip() for s in input_list]
            replaced = replace_sentences(sentences, src_word_list, tgt_word_list)
            LOCK.release()
            return jsonify({"replacements": replaced})
        else:
            LOCK.release()
            return jsonify({'error': 'Invalid list format. Please provide a dictionary of the format {"sentences": ["sentence 1", ..., "sentence N"]}'}), 400
    except Exception as e:
        print("Error occurred:", e)
        LOCK.release()
        return jsonify({'error': 'Internal server error'}), 500
app.run(port=5000, host='localhost')