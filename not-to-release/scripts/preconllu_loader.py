from collections import defaultdict

class Loader:
    field_nums = {}

    def __init__(self):
        self.fields = defaultdict(str)
        self.conllu_fields, self.trans = {}, {}
    
    def parse(self, fields):
        for field_name, field_num in self.field_nums.items():
            try:
                self.fields[field_name] = fields[field_num]
            except IndexError:
                self.fields[field_name] = ""
        self.conllu_fields, self.trans = {}, {}
        self.fill_conllu_fields()
        return self.conllu_fields, self.trans

    def fill_conllu_fields(self):
        self.conllu_fields["ORD"] = self.fields["ORD"]
        self.conllu_fields["FORM"] = self.fields["ORIGINAL"]
        if self.fields["LEMMA_ORIGINAL"] in ["-", "_"]:
            self.conllu_fields["LEMMA"] = self.conllu_fields["FORM"]
        else:
            self.conllu_fields["LEMMA"] = self.fields["LEMMA_ORIGINAL"]
        self.conllu_fields["UPOSTAG"] = self.fields["UPOSTAG"]
        self.process_feats()
        self.conllu_fields["XPOSTAG"] = "_"
        self.conllu_fields["HEAD"] = self.fields["HEAD"]
        self.conllu_fields["DEPREL"] = self.fields["DEPREL"]
        self.conllu_fields["DEPS"] = "_"
        self.process_misc()
        self.process_trans()

    def process_feats(self):
        pass

    def process_misc(self):
        self.conllu_fields["MISC"] = "_"

    def process_trans(self):
        self.trans = {
            "TRANSCRIPT": self.fields["TRANSCRIPT"],
            "LEMMA_TRANSCRIPT": self.fields["LEMMA_TRANSCRIPT"],
            "GLOSS": self.fields["GLOSS"],
        }
        if self.fields["LEMMA_ORIGINAL"] in ["-", "_"]:
            self.trans["LEMMA_TRANSCRIPT"] = self.trans["TRANSCRIPT"]

class CairoLoader(Loader):
    field_nums = {
        "ORD": 0,
        "ORIGINAL": 1,
        # "TRANSLITER": 2,
        "TRANSCRIPT": 3,
        "LEMMA_ORIGINAL": 4,
        # "LEMMA_TRANSLITER": 5,
        "LEMMA_TRANSCRIPT": 6,
        "GLOSS": 7,
        "UPOSTAG": 8,
        "FEATS": 9,
        "HEAD": 10,
        "DEPREL": 11
    }

    def process_feats(self):
        self.conllu_fields["FEATS"] = self.fields["FEATS"].strip('"')
        if self.conllu_fields["FEATS"] == "_":
            self.conllu_fields["FEATS"] = ""

    def fill_conllu_fields(self):
        super().fill_conllu_fields()
        if self.conllu_fields["LEMMA"] == "-":
            self.conllu_fields["LEMMA"] = self.conllu_fields["FORM"]
            self.trans["LEMMA_TRANSCRIPT"] = self.trans["TRANSCRIPT"]




class PntLoader(Loader):
    field_nums = {
        "ORD": 0,
        "ORIGINAL": 1,
        "TRANSCRIPT": 2,
        "LEMMA_ORIGINAL": 3,
        "LEMMA_TRANSCRIPT": 4,
        "GLOSS": 5,
        "UPOSTAG": 6,
        "DEPREL": 7,
        "HEAD": 8,
        "ASPECT_FEAT": 9,
        "CASE_FEAT": 10,
        "GENDER_FEAT": 11,
        "MOOD_FEAT": 12,
        "NUMBER_FEAT": 13,
        "PERSON_FEAT": 14,
        "TENSE_FEAT": 15,
        "VERB_FORM_FEAT": 16,
        "OTHER_FEATS": 17,
        "MISC": 18
    }
    feats_names = {
        "ASPECT_FEAT": "Aspect",
        "CASE_FEAT": "Case",
        "GENDER_FEAT": "Gender",
        "MOOD_FEAT": "Mood",
        "NUMBER_FEAT": "Number",
        "PERSON_FEAT": "Person",
        "TENSE_FEAT": "Tense",
        "VERB_FORM_FEAT": "VerbForm",
    }

    def process_feats(self):
        feats_attributes = [attribute for attribute in self.field_nums if attribute.endswith("_FEAT")]
        feats_list = [f"{self.feats_names[attribute]}={self.fields[attribute]}"
                      for attribute in feats_attributes if self.fields[attribute]]
        if self.fields["OTHER_FEATS"]:
            feats_list += self.fields["OTHER_FEATS"].split("|")
        feats_list.sort()
        self.conllu_fields["FEATS"] = "|".join(feats_list)

    def process_misc(self):
        self.conllu_fields["MISC"] = self.fields["MISC"]

    def fill_conllu_fields(self):
        super().fill_conllu_fields()
        if self.conllu_fields["LEMMA"] == "_":
            self.conllu_fields["LEMMA"] = self.conllu_fields["FORM"]
            self.trans["LEMMA_TRANSCRIPT"] = self.trans["TRANSCRIPT"]
