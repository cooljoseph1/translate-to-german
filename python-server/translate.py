import ctranslate2
import sentencepiece as spm

device = "cuda"  # or "cpu" for CPU

# [Modify] Set paths to the CTranslate2 and SentencePiece models
ct_model_path = "../models/m2m100_418m/"
sp_model_path = "../models/m2m100_418m/sentencepiece.model"
beam_size = 5 # Beam size for beam search in decoding

# Load the translation model
translator = ctranslate2.Translator(ct_model_path, device=device)

# Load the source SentecePiece model
sp = spm.SentencePieceProcessor()
sp.load(sp_model_path)

def translate_lines(lines, src_prefix="__en__", tgt_prefix="__de__"):
    source_sents = [line.strip() for line in lines]
    target_prefix = [[tgt_prefix]] * len(source_sents)

    # Subword the source sentences
    source_sents_subworded = sp.encode(source_sents, out_type=str)
    source_sents_subworded = [[src_prefix] + sent for sent in source_sents_subworded]

    # Translate the source sentences
    translations = translator.translate_batch(source_sents_subworded, batch_type="tokens", max_batch_size=4000, beam_size=beam_size, target_prefix=target_prefix)
    translations2 = [translation[0]['tokens'] for translation in translations]

    # Desubword the target sentences
    translations_desubword = sp.decode(translations2)
    translations_desubword = [sent[len(tgt_prefix):] for sent in translations_desubword]
    final_translations = [line.strip() for line in translations_desubword]
    return final_translations
