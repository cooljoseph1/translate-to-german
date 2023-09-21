from transformers import AutoModel, AutoTokenizer
import itertools
import torch
import random

import re

device = "cuda"  # or "cpu" for CPU

# load model
model = AutoModel.from_pretrained("../models/model_with_co").to(device)
tokenizer = AutoTokenizer.from_pretrained("../models/model_with_co")

# model parameters
align_layer = 8
threshold = 1e-3

def split_sentence(sentence):
    # Split the sentence into words and punctuation

    words_and_punctuation = re.findall(r"[\w\[\]'-]+\s|[\w\[\]'-]+|[^w]\s|[^w\s]", sentence, re.UNICODE)
    
    # Determine if each word/punctuation was separated by a space
    for i, item in enumerate(words_and_punctuation):
        if item.endswith(' '):
            yield item.rstrip(), True
        else:
            yield item, False

def join_words_and_punctuation(words_with_space):
    # Join the words and punctuation back into a sentence
    for i, (word, has_space) in enumerate(words_with_space):
        yield word.strip()
        if i < len(words_with_space) - 1:
            next_word = words_with_space[i + 1][0]
            if next_word in {".", ",", "!", "?", ";", ":"}:
                yield ''
            elif not any(s.isalpha() or s.isdigit() for s in word):
                yield ' ' if has_space else ''
            elif not any(s.isalpha() or s.isdigit() for s in next_word):
                yield ' ' if has_space else ''
            else:
                yield ' '

def align_sentence(src, tgt):
    """
    Return a mapping i-j mapping of words in src to words in tgt
    """
    # pre-processing
    src, tgt = src.strip(), tgt.strip()
    sent_src, sent_tgt = list(split_sentence(src)), list(split_sentence(tgt))
    token_src, token_tgt = [tokenizer.tokenize(word.lower()) for word, _ in sent_src], [tokenizer.tokenize(word.lower()) for word, _ in sent_tgt]
    wid_src, wid_tgt = [tokenizer.convert_tokens_to_ids(x) for x in token_src], [tokenizer.convert_tokens_to_ids(x) for x in token_tgt]
    ids_src, ids_tgt = tokenizer.prepare_for_model(list(itertools.chain(*wid_src)), return_tensors='pt', model_max_length=tokenizer.model_max_length, truncation=True)['input_ids'], tokenizer.prepare_for_model(list(itertools.chain(*wid_tgt)), return_tensors='pt', truncation=True, model_max_length=tokenizer.model_max_length)['input_ids']
    ids_src, ids_tgt = ids_src.to(device), ids_tgt.to(device)
    sub2word_map_src = []
    for i, word_list in enumerate(token_src):
        sub2word_map_src += [i for x in word_list]
    sub2word_map_tgt = []
    for i, word_list in enumerate(token_tgt):
        sub2word_map_tgt += [i for x in word_list]
    
    # alignment
    align_layer = 8
    threshold = 0.8
    model.eval()
    with torch.no_grad():
        out_src = model(ids_src.unsqueeze(0), output_hidden_states=True)[2][align_layer][0, 1:-1]
        out_tgt = model(ids_tgt.unsqueeze(0), output_hidden_states=True)[2][align_layer][0, 1:-1]

        dot_prod = torch.matmul(out_src, out_tgt.transpose(-1, -2))

        softmax_srctgt = torch.nn.Softmax(dim=-1)(dot_prod)
        softmax_tgtsrc = torch.nn.Softmax(dim=-2)(dot_prod)

        softmax_inter = (softmax_srctgt > threshold) | (softmax_tgtsrc > threshold)

    align_subwords = torch.nonzero(softmax_inter, as_tuple=False)
    align_words = set()
    for i, j in align_subwords:
        align_words.add( (sub2word_map_src[i], sub2word_map_tgt[j]) )

    align_words = sorted(align_words)
    
    return sent_src, sent_tgt, align_words

def replace_words(sent_src, sent_tgt, align_words, src_word_list=set(), tgt_word_list=set()):
    clumps = []
    clump_map = {}
    x = -2
    ii = {i for i, j in align_words if random.random() < 0.03}
    for i, j in sorted(align_words):
        if i not in ii:
            continue
        if i > x + 1:
            clumps.append(set())
        x = i
        clumps[-1].add(j)
        clump_map[x] = clumps[-1]

    new_sentence = []
    i = 0
    while i < len(sent_src):
        if i in clump_map:
            clump = clump_map[i]
            while i in clump_map:
                i += 1
            replacement = [sent_tgt[j] for j in sorted(clump)]
            replacement = [replacement[0]] + [b for a, b in zip(replacement[:-1], replacement[1:]) if a[0].lower() != b[0].lower()]
            new_sentence.extend(replacement)
        else:
            new_sentence.append(sent_src[i])
            i += 1
    return ''.join(join_words_and_punctuation(new_sentence))


def replace_words_old(sent_src, sent_tgt, align_words, src_word_list=set(), tgt_word_list=set()):
    clumps = []
    clump_map = {}
    x = -2
    ii = {i for i, j in align_words if sent_src[i][0].lower() in src_word_list or sent_tgt[j][0].lower() in tgt_word_list}
    for i, j in sorted(align_words):
        if i not in ii:
            continue
        if i > x + 1:
            clumps.append(set())
        x = i
        clumps[-1].add(j)
        clump_map[x] = clumps[-1]

    new_sentence = []
    i = 0
    while i < len(sent_src):
        if i in clump_map:
            clump = clump_map[i]
            while i in clump_map:
                i += 1
            replacement = [sent_tgt[j] for j in sorted(clump)]
            replacement = [replacement[0]] + [b for a, b in zip(replacement[:-1], replacement[1:]) if a[0].lower() != b[0].lower()]
            new_sentence.extend(replacement)
        else:
            new_sentence.append(sent_src[i])
            i += 1
    return ''.join(join_words_and_punctuation(new_sentence))