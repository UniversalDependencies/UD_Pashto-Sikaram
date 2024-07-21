import re

SENTENCE_ENDINGS = ".!؟"
TOKEN_ENDINGS = ":،!؟"

DOC_NAME = "pnt"


def load_transliteration_table():
    translit_table, transcrip_table = {}, {}
    with open( "not-to-release/transliteration_table.txt", encoding="utf-8") as table_file:
        for line in table_file:
            arabic_letter, translit_letter, transcrip_letter = line.rstrip("\n").split("\t")
            translit_table[ arabic_letter ] = translit_letter
            transcrip_table[ arabic_letter ] = transcrip_letter
    return translit_table, transcrip_table


def transliterate(text, table):
    char_list = list(text)
    for i, char in enumerate(char_list):
        if char in table:
            char_list[i] = table[char]
    return "".join(char_list)


transliteration_table, transcription_table = load_transliteration_table()
text_name = "pnt_plain_text.txt"
with open(f"not-to-release/{text_name}", "r", encoding="utf-8") as plain_text:
    text = "".join(plain_text.readlines())
    paragraphs = text.split("\n\n")
    paragraphs = [re.sub("\n", " ", paragraph.strip()) for paragraph in paragraphs]
    for paragraph_id, paragraph in enumerate(paragraphs):
        indices = [0] + [index+1 for index, char in enumerate(paragraph) if char in SENTENCE_ENDINGS]
        if len(paragraph) not in indices:
            indices.append(len(paragraph))
        sentences = [paragraph[indices[j-1]:indices[j]].strip() for j in range(1, len(indices))]
        for sentence_id, sentence in enumerate(sentences):
            sentence = sentence + "‏"
            sent_id_line = f"# sent_id = {DOC_NAME}-{paragraph_id+1}.{sentence_id+1}"
            text_line = f"# text = {sentence}"
            translit_sentence = transliterate(sentence, transliteration_table)
            transliteration_line = f"# transliter = {translit_sentence}"
            transcription_line = "# transcript = "
            text_en_line = "# text_en = "
            print("\n".join([sent_id_line, text_line, transliteration_line, transcription_line, text_en_line]))
            tokenized_sentence = sentence
            for ending_char in TOKEN_ENDINGS:
                tokenized_sentence = re.sub(ending_char, " "+ending_char, tokenized_sentence)
            tokenized_sentence = re.sub("..", " .", tokenized_sentence)
            tokenized_sentence = re.sub("\)", " ) ", tokenized_sentence)
            tokenized_sentence = re.sub("\(", " ( ", tokenized_sentence)
            tokens = tokenized_sentence.split()
            for token_id, token in enumerate(tokens):
                translit_token = transliterate(token, transliteration_table)
                transcrip_token = transliterate(token, transcription_table)
                token_line = f"{token_id+1}\t{token}\t{translit_token}\t{transcrip_token}"
                print(token_line)
            print("")
