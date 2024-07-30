from itertools import zip_longest
from sys import stdout

class PreconnluSentence:
    ORD = 0
    ORIGINAL = 1
    TRANSLITER = 2
    TRANSCRIPT = 3
    LEMMA_ORIGINAL = 4
    LEMMA_TRANSLITER = 5
    LEMMA_TRANSCRIPT = 6
    TRANSLATION = 7
    UPOSTAG = 8
    FEATS = 9
    HEAD = 10
    DEPREL = 11
    MISC = 12


    def __init__(self, id_line):
        self.id = id_line.lstrip("# sent_id = ")
        self.intro_lines = []
        self.token_lines = []

    def add_intro_line(self, line):
        self.intro_lines.append(line)

    def add_token_line(self, line):
        fields = line.split("\t")
        self.token_lines.append(fields)

    def control_layer(self, intro_text, line_tokens, version):
        for punct_mark in ".,;:?!\"'-،؟":
            intro_text = intro_text.replace(punct_mark, f" {punct_mark} ")
        text_tokens = intro_text.split()
        for text_token, line_token in zip_longest(text_tokens, line_tokens):
            if text_token != line_token:
                print(self.id, version, f"*{text_token}*", f"*{line_token}*")

    def control(self):
        text = self.intro_lines[0]
        original_tokens, transliteration_tokens = [], []
        transcription_tokens, translation_tokens = [], []

        mwt_end = None
        for token_line in self.token_lines:
            if "-" in token_line[self.ORD]:
                mwt_end = token_line[self.ORD].split("-")[-1]
            elif mwt_end:
                if mwt_end == token_line[self.ORD]:
                    mwt_end = None
                token_line += [""]
                continue
            original_tokens.append(token_line[self.ORIGINAL])
            transliteration_tokens.append(token_line[self.TRANSLITER])
            transcription_tokens.append(token_line[self.TRANSCRIPT])
            translation_tokens.append(token_line[self.TRANSLATION])

            # handling spaces
            token_form = token_line[self.ORIGINAL]
            assert text.startswith(token_form)
            text = text.lstrip(token_form)
            if text and text[0] != " ":
                token_line += ["SpaceAfter=No"]
                text = text.lstrip(" ")
                continue
            spaces_num = len(text) - len(text.lstrip(" "))
            if spaces_num > 1:
                token_line += ["\\s" * spaces_num]
            else:
                token_line += [""]
                text = text.lstrip(" ")

        self.control_layer(self.intro_lines[0], original_tokens, "orig")
        self.control_layer(self.intro_lines[1], transliteration_tokens, "tlit")
        self.control_layer(self.intro_lines[2], transcription_tokens, "tscr")
        #self.control_layer(self.intro_lines[3], translation_tokens, "tlat")

    def convert(self, file):
        print(f"# sent_id = {self.id}", file=file)
        print(f"# text = {self.intro_lines[0]}", file=file)
        print(f"# translit_1 = {self.intro_lines[1]}", file=file)
        print(f"# translit = {self.intro_lines[2]}", file=file)
        print(f"# text_en = {self.intro_lines[3]}", file=file)

        for token_line in self.token_lines:
            ord = token_line[self.ORD]
            form = token_line[self.ORIGINAL]
            lemma = token_line[self.ORIGINAL]
            upostag = token_line[self.UPOSTAG]
            xpostag = "_"
            feats = token_line[self.FEATS].strip('"')
            head = token_line[self.HEAD]
            deprel = token_line[self.DEPREL]
            deps = "_"

            translit, ltranslit, gloss = "", "", ""
            if token_line[self.TRANSLITER] not in ["_", token_line[self.ORIGINAL]]:
                translit = f"Translit={token_line[self.TRANSCRIPT]}"
            if token_line[self.LEMMA_ORIGINAL] != "-":
                lemma = token_line[self.LEMMA_ORIGINAL]
                ltranslit = f"LTranslit={token_line[self.LEMMA_TRANSCRIPT]}"
            if token_line[self.TRANSLATION] not in \
                    ["_", token_line[self.TRANSCRIPT], token_line[self.LEMMA_TRANSCRIPT]]:
                gloss = f"Gloss={token_line[self.TRANSLATION]}"
            misc_items = [item for item in [translit, ltranslit, gloss] if item]
            if token_line[self.MISC]:
                misc_items += token_line[self.MISC].split("|")
            misc = "|".join(misc_items) if misc_items else "_"

            conllu_fields = [ord, form, lemma, upostag, xpostag,
                             feats, head, deprel, deps, misc]
            conllu_line = "\t".join(conllu_fields)
            print(conllu_line, file=file)


class PreconlluConverter:
    def __init__(self):
        self.sentences = []

    def load_preconllu(self, preconllu_path):
        with open(preconllu_path, "r", encoding="utf-8") as preconllu_file:
            preconllu_content = preconllu_file.read()
            modified_content = preconllu_content.replace("|\n", "|")
            lines = modified_content.splitlines()
            current_sentence = None
            for line in lines:
                line = line.rstrip()
                if not line:
                    self.sentences.append(current_sentence)
                    current_sentence = None
                elif line.startswith("#"):
                    current_sentence = PreconnluSentence(line)
                elif "\t" not in line:
                    current_sentence.add_intro_line(line)
                else:
                    current_sentence.add_token_line(line)
            if current_sentence:
                self.sentences.append(current_sentence)

    def control_sentences(self):
        for sentence in self.sentences:
            sentence.control()

    def convert_sentences(self, file=stdout):
        for sentence in self.sentences:
            sentence.convert(file)
            print("", file=file)



def main():
    converter = PreconlluConverter()
    converter.load_preconllu("../data/cairo_sentences.preconllu")
    converter.control_sentences()
    conllu_file_name = "../../ps_sikaram-ud-test.conllu"
    with open(conllu_file_name, "w", encoding="utf-8") as conllu_file:
        converter.convert_sentences(file=conllu_file)

if __name__ == "__main__":
    main()