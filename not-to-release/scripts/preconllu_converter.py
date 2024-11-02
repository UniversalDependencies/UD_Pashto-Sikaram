from itertools import zip_longest
from sys import stdout

from controller import Controller
from preconllu_loader import CairoLoader, PntLoader
from closed_dict import ClosedDict
from internode_controller import InternodeController

class TokenLine:
    def __init__(self, fields, trans):
        self.fields = fields
        self.trans = trans
        self.spaces_after = 1

        self.parent = None
        self.children = []
        split_feats = []
        if fields["FEATS"] not in ["", "_"]:
            split_feats = fields["FEATS"].split("|")
        self.feats = {feat.split("=")[0]: feat.split("=")[1] for feat in split_feats}

    def add_child(self, child):
        self.children.append(child)
        child.set_parent(self)

    def set_parent(self, parent):
        self.parent = parent

class Sentence:

    # LOADING

    def __init__(self, id_line, loader, controller, closed_dict, internode_controller):
        self.id = id_line.lstrip("# sent_id = ")
        self.intro_lines = {}
        self.token_lines = []
        self.loader = loader
        self.controller = controller
        self.closed_dict = closed_dict
        self.internode_controller = internode_controller

    def add_intro_line(self, line):
        if line.startswith("# text = "):
            _, _, intro_text = line.rstrip("\n").lstrip("# ").partition(" = ")
            self.intro_lines["orig"] = intro_text
        elif line.startswith("# text_en = "):
            _, _, intro_text = line.rstrip("\n").lstrip("# ").partition(" = ")
            self.intro_lines["gloss"] = intro_text


    def add_token_line(self, line):
        #print([a.fields["FORM"] for a in self.token_lines])
        fields = line.split("\t")
        conllu_fields, trans_fields = self.loader.parse(fields)
        token_line = TokenLine(conllu_fields, trans_fields)
        self.token_lines.append(token_line)

    # ===

    # CONTROL

    def build_sentence(self):
        built_text = ""
        mwt_end = ""
        for token_line in self.token_lines:
            if mwt_end:
                if mwt_end == token_line.fields["ORD"]:
                    mwt_end = ""
                continue
            if "-" in token_line.fields["ORD"]:
                mwt_end = token_line.fields["ORD"].split("-")[1]

            built_text += token_line.trans["TRANSCRIPT"].strip("‏")
            built_text += " " * token_line.spaces_after
        return built_text

    def control(self):
        original_tokens = []
        # transcript_text = ""
        mwt_end = None
        text = self.intro_lines["orig"]
        #print([a.fields["FORM"] for a in self.token_lines])

        for token_line in self.token_lines:
            if "-" in token_line.fields["ORD"]:
                mwt_end = token_line.fields["ORD"].split("-")[-1]
            elif mwt_end:
                if mwt_end == token_line.fields["ORD"]:
                    mwt_end = None
                continue
            original_tokens.append(token_line.fields["FORM"])
            # transcript_text += token_line.trans["TRANSCRIPT"]

            # handling spaces
            token_form = token_line.fields["FORM"]
            if not text.startswith(token_form):
                print(f"{self.id}:{token_line.fields['ORD']} form does not agree: {token_line.fields['FORM']}")
                return
            text = text.lstrip(token_form)
            if text:
                spaces_num = len(text) - len(text.lstrip(" "))
                token_line.spaces_after = spaces_num
                text = text.lstrip(" ")

            self.controller.control_transcription(self.id, token_line)
            self.controller.control_annotation(self.id, token_line)


    def convert(self, file):
        print(f"# sent_id = {self.id}", file=file)
        print(f"# text = {self.intro_lines['orig']}", file=file)
        #print(f"# translit_1 = {self.intro_lines[1]}", file=file)
        transcript_intro = self.build_sentence()
        print(f"# translit = {transcript_intro}", file=file)
        print(f"# text_en = {self.intro_lines['gloss']}", file=file)

        for token_line in self.token_lines:
            ord = token_line.fields["ORD"]
            form = token_line.fields["FORM"]
            lemma = form
            if token_line.fields["LEMMA"] not in ["_", form]:
                lemma = token_line.fields["LEMMA"]
            if "-" in ord:
                lemma = "_"
            upostag = token_line.fields["UPOSTAG"]
            xpostag = "_"
            feats = token_line.fields["FEATS"] if token_line.feats else "_"
            head = token_line.fields["HEAD"]
            deprel = token_line.fields["DEPREL"]
            deps = "_"

            translit = f"Translit={token_line.trans['TRANSCRIPT']}"
            ltranslit = f"LTranslit={token_line.trans['LEMMA_TRANSCRIPT']}"
            gloss = f"Gloss={token_line.trans['GLOSS']}"
            misc_items = [translit, ltranslit, gloss]
            if token_line.fields["MISC"] not in ["", "_"]:
                misc_items += token_line.fields["MISC"].split("|")
            if "-" in ord:
                misc_items = [f"Lemma={token_line.fields['LEMMA']}"] + misc_items
            if token_line.spaces_after == 0 and "SpaceAfter=No" not in misc_items:
                misc_items += ["SpaceAfter=No"]
            elif token_line.spaces_after > 1:
                spaces = "\\s" * token_line.spaces_after
                misc_items += [f"SpacesAfter={spaces}"]
            misc = "|".join(misc_items) if misc_items else "_"
            conllu_fields = [ord, form, lemma, upostag, xpostag,
                             feats, head, deprel, deps, misc]
            conllu_line = "\t".join(conllu_fields)
            print(conllu_line, file=file)
            # if [upostag for upostag in ["DET", "PRON", "ADV", "ADP", "NUM", "CONJ", "PART"] if upostag in conllu_line]:
            #     print(conllu_line)
            self.closed_dict.control_token_line(self.id, token_line)

        self.internode_controller.control_tree(self.id, self.token_lines)


class PreconlluConverter:
    def __init__(self, loader_class):
        self.sentences = []
        #self.loader = CairoLoader()
        self.loader = loader_class()
        self.controller = Controller()
        self.closed_dict = ClosedDict()
        self.internode_controller = InternodeController()

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
                elif line.startswith("# sent_id"):
                    current_sentence = Sentence(line, self.loader, self.controller, self.closed_dict, self.internode_controller)
                elif "\t" not in line:
                    current_sentence.add_intro_line(line)
                else:
                    current_sentence.add_token_line(line)
            if current_sentence:
                self.sentences.append(current_sentence)

    def control_sentences(self):
        for sentence in self.sentences:
            sentence.control()
        self.controller.final_dictionary_control()

    def convert_sentences(self, file=stdout):
        for sentence in self.sentences:
            sentence.convert(file)
            print("", file=file)



def main():
    conllu_file_name = "../../ps_sikaram-ud-test.conllu"
    with open(conllu_file_name, "w", encoding="utf-8") as conllu_file:
        converter = PreconlluConverter(CairoLoader)
        converter.load_preconllu("../data/cairo_sentences.preconllu")
        converter.control_sentences()
        converter.convert_sentences(file=conllu_file)

        converter = PreconlluConverter(PntLoader)
        converter.load_preconllu("../data/pnt_sentences.preconllu")
        converter.control_sentences()
        converter.convert_sentences(file=conllu_file)


if __name__ == "__main__":
    main()