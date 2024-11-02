import re


class Controller:
    def __init__(self):
        self.translit_table = {}

    def check_attributes(self, info, form, upostag, feats, correct_attributes, possible_attributes=None):
        if possible_attributes is None:
            possible_attributes = tuple()
        possible_attributes += ("Typo",)
        wrong_feats = [attribute for attribute in feats.keys() if attribute not in correct_attributes + possible_attributes]
        missing_feats = [attribute for attribute in correct_attributes if attribute not in feats.keys()]
        if wrong_feats:
            print(f"{info}: redundant features for {upostag} {form}: {wrong_feats}")
        if missing_feats:
            print(f"{info}: missing features for {upostag} {form}: {missing_feats}")

    def control_verb(self, info, form, lemma, upostag, feats):
        if lemma == "بۀ":
            if ("Tense" in feats and feats["Tense"] == "Fut") or ("Mood" in feats and feats["Mood"] == "Sub"):
                pass
            else:
                print(f"{info}: missing or incorrect Mood/Tense for {upostag} {form}")
            self.check_attributes(info, form, upostag, feats, tuple(), ("Mood", "Tense"))
            return
        elif lemma == "ونۀ":
            self.check_attributes(info, form, upostag, feats, ("Aspect", "Polarity"))
            if "Aspect" not in feats or feats["Aspect"] != "Perf":
                print(f"{info}: missing or incorrect Aspect for {upostag} {form}")
            if "Polarity" not in feats or feats["Polarity"] != "Neg":
                print(f"{info}: missing or incorrect Polarity for {upostag} {form}")
            return

        if "VerbForm" not in feats:
            print(f"{info}: missing VerbForm for {upostag} {form}")
            return
        if feats["VerbForm"] == "Fin":
            if lemma == "شته":
                self.check_attributes(info, form, upostag, feats, ("Person", "Tense", "VerbForm"))
                return
            if "Person" not in feats:
                if "Mood" in feats and feats["Mood"] != "Pot":
                    print(f"{info}: missing Person for {upostag} {form}")
            if "Number" not in feats:
                #if True:#"Person" not in feats or feats["Person"] != "3":
                if "Mood" in feats and feats["Mood"] != "Pot":
                    print(f"{info}: missing Number for {upostag} {form}")
            if "Mood" not in feats:
                print(f"{info}: missing Mood for {upostag} {form}")
            if "Tense" not in feats:
                if "Mood" not in feats or feats["Mood"] == "Ind":
                    print(f"{info}: missing Tense for {upostag} {form}")
            if "Aspect" not in feats:
                if lemma != "یم":
                    if "Mood" not in feats or feats["Mood"] != "Sub":  # !!! Sub may be removed
                        print(f"{info}: missing Aspect for {upostag} {form}")
            if "Tense" in feats and feats["Tense"] == "Past" and "Person" in feats and ["Person"] == "3":
                if "Gender" not in feats:
                    print(f"{info}: missing Gender for {upostag} {form}")

            if "Mood" in feats and feats["Mood"] == "Imp":
                if "Person" in feats and feats["Person"] != "2":
                    print(f"{info}: wrong Person for imperative {form}: {feats['Person']}")

        elif feats["VerbForm"] == "Inf":
            self.check_attributes(info, form, upostag, feats, ("Aspect", "Case", "VerbForm"))

        elif feats["VerbForm"] == "Part":
            self.check_attributes(info, form, upostag, feats, ("Aspect", "Case", "Gender", "Number", "Tense", "VerbForm"), ("Variant",)) # Tense?

    def control_nominal(self, info, form, _, upostag, feats):
        self.check_attributes(info, form, upostag, feats, ("Case", "Gender", "Number"))

    def control_pronoun(self, info, form, lemma, upostag, feats):
        return
        pronouns = {
            "Ind": {
                "ځینې": ["Case", "Number"],
                "كوم": ["Case"],
                "څو": []
            },
            "Tot": {
                "هر": ["Case", "Gender", "Number"],
                "ټول": ["Case", "Gender", "Number"],
            },
            "Int": {
                "څوک": ["Case"],
                "څۀ": [],
                "كوم": []
            },
            "Neg": {
                "هیڅوک": ["Case"],
                "": []
            },
            "Rel": {
                "څۀ": []
            },
            "Rcp": {
                "یوبل": []
            }
        }
        if "PronType" not in feats:
            print(f"{info}: missing PronType for {upostag} {form}")
            return
        if feats["PronType"] in pronouns:
            if lemma not in pronouns[feats["PronType"]]:
                print(f"{info}: wrong PronType for {lemma}: {feats['PronType']}")
            else:
                correct_attributes = tuple(pronouns[feats["PronType"]][lemma])
                check_attributes(info, form, upostag, feats, correct_attributes)
        elif feats["PronType"] == "Dem":
            if "Case" not in feats:
                print(f"{info}: missing Case for demonstrative {upostag} {form}")
            elif feats["Case"] != "Nom":
                check_attributes(info, form, upostag, feats, ("Case", "Deixis", "Gender", "Number", "PronType"))
            else:
                check_attributes(info, form, upostag, feats, ("Case", "Deixis", "PronType"))
        elif feats["PronType"] == "Prs":
            if not "Person" in feats:
                print(f"{info}: missing Person for personal {upostag} {form}")
                return
            if "Variant" in feats and "Person" in feats:
                if feats["Variant"] == "Dir":
                    check_attributes(info, form, upostag, feats, ("Person", "PronType", "Variant"))
                elif feats["Variant"] == "Weak":
                    check_attributes(info, form, upostag, feats, ("Person", "PronType", "Variant"), ("Poss"))
                else:
                    if feats["Person"] == "3" and "Poss" not in feats:
                        check_attributes(info, form, upostag, feats, ("Person", "Deixis", "PronType", "Variant"))
                    else:
                        check_attributes(info, form, upostag, feats, ("Person", "Deixis", "PronType", "Variant"))

    def control_numeral(self, info, form, lemma, upostag, feats):
        if "NumType" not in feats:
            print(f"{info}: missing NumType for NUM {form}")
            return
        if feats["NumType"] == "Card":
            if lemma in ["یو", "دوه"]:
                self.check_attributes(info, form, upostag, feats, ("Case", "Gender", "NumType"))
            else:
                self.check_attributes(info, form, upostag, feats, ("Case", "NumType"))



    # def control_adverb(self, info, form, lemma, upostag, feats):
    #     if

    def control_adposition(self, info, form, lemma, _, feats):
        locative_adpositions = ["پۀ", "کې", "پر"]
        oblique_adpositions = ["د", "ته", "څخه"]
        ablative_adpositions = ["له", "تر"]
        wrong_feats = [attribute for attribute in feats.keys() if attribute != "Case"]
        if wrong_feats:
            print(f"{info}: redundant features for ADP {form}: {wrong_feats}")
        if not "Case" in feats:
            print(f"{info}: missing Case for ADP {form}")
        else:
            if lemma in locative_adpositions and feats["Case"] != "Loc":
                print(f"{info}: incorrect Case for ADP {form}, expected Loc, got {feats['Case']}")
            if lemma in oblique_adpositions and feats["Case"] != "Acc":
                print(f"{info}: incorrect Case for ADP {form}, expected Acc, got {feats['Case']}")
            if lemma in ablative_adpositions and feats["Case"] not in ["Abl", "Acc"]:
                print(f"{info}: incorrect Case for ADP {form}, expected Abl, got {feats['Case']}")


    def control_particle(self, info, form, lemma, _, feats):
        if form == "نه" or form == "نۀ":
            if lemma != "نۀ":
                print(f"{info}: wrong lemma for {form}: {lemma}")
            if len(feats) == 1:
                if "Polarity" not in feats or feats["Polarity"] != "Neg":
                    print(f"{info}: incorrect feats for {lemma}, should be exctly Polarity=Neg")
            else:
                print(f"{info}: incorrect feats for {lemma}, should be exctly Polarity=Neg")

    def control_rest(self, info, form, _, upostag, feats):
        self.check_attributes(info, form, upostag, feats, tuple())
        # wrong_feats = [attribute for attribute in feats.keys() if attribute != "Case"]
        # if wrong_feats:
        #     print(f"{info}: redundant features for {upostag} {form}: {wrong_feats}")


    def control_annotation(self, sent_id, token_line):
        info = f"{sent_id}:{token_line.fields['ORD']}"
        form = token_line.fields["FORM"]
        lemma = token_line.fields["LEMMA"]
        upostag = token_line.fields["UPOSTAG"]

        # feats = {}
        # if token_line.fields["FEATS"]:
        #     feats_list = token_line.fields["FEATS"].split("|")
        #     for feat in feats_list:
        #         attribute, value = feat.split("=")
        #         feats[attribute] = value

        control_methods = {
            "VERB": self.control_verb,
            "AUX": self.control_verb,
            "NOUN": self.control_nominal,
            "PROPN": self.control_nominal,
            "ADJ": self.control_nominal,
            "PRON": self.control_pronoun,
            "DET": self.control_pronoun,
            "NUM": self.control_numeral,
            #"ADV": self.control_adverb,
            "ADP": self.control_adposition,
            "PART": self.control_particle
        }
        if upostag in control_methods:
            control_method = control_methods[upostag]
        else:
            control_method = self.control_rest

        control_method(info, form, lemma, upostag, token_line.feats)

    def check_correspondence(self, info, orig_char, trans_char):
        orig_trans_char_map = self.orig_trans_map[orig_char]
        trans_orig_char_map = self.trans_orig_map[orig_char]
        if orig_char in trans_orig_char_map and trans_char in orig_trans_char_map:
            return 1, 1
        if None in trans_orig_char_map:
            return 1, 0
        if None in orig_trans_char_map:
            return 0, 1
        print(f"{info}: incorrect transcription: {orig_char} <=> {trans_char}")
        return 1, 1

    def control_sigle_transcription(self, info, original, transcription):
        if transcription in ".,()[]{};:?!\"'-،؟" or transcription in [".‏", "!‏", "؟‏", ":‏"]:
            return

        transcription = re.sub("ë́", "@", transcription)
        vowel_num = len([char for char in transcription if char in "ieaëuoâíéá@óúấ"])
        stress_num = len([char for char in transcription if char in "íéá@óúấ"])
        if vowel_num == 0:
            print(f"{info}: missing vowel: {transcription}")
        elif vowel_num == 1 and stress_num > 0:
            print(f"{info}: redundant stress: {transcription}")
        elif vowel_num > 1 and stress_num == 0:
            print(f"{info}: missing stress: {transcription}")


    def control_transcription(self, sent_id, token_line):
        info = f"{sent_id}:{token_line.fields['ORD']}"
        form = token_line.fields["FORM"]
        transcription = token_line.trans["TRANSCRIPT"]
        self.control_sigle_transcription(info, form, transcription)
        lemma = token_line.fields["LEMMA"]
        lemma_transcription = token_line.trans["LEMMA_TRANSCRIPT"]
        if lemma != form or lemma_transcription != transcription:
            self.control_sigle_transcription(info, lemma, lemma_transcription)