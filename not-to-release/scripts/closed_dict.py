class ClosedDict:
    FORM = 0
    TRANSLIT = 1
    LEMMA = 2
    LTRANSLIT = 3
    GLOSS = 4
    OTHER = 5
    UPOSTAG = 6
    DEPREL = 7
    ANIMACY = 8
    CASE = 9
    DEIXIS = 10
    GENDER = 11
    NUMBER = 12
    NUMBER_PSOR = 13
    NUM_TYPE = 14
    PERSON = 15
    POLARITY = 16
    POSS = 17
    PRON_TYPE = 18
    REFLEX = 19
    VARIANT = 20

    feats = {"Animacy": ANIMACY, "Case": CASE, "Deixis": DEIXIS,
             "Gender": GENDER, "Number": NUMBER, "Number[psor]": NUMBER_PSOR,
             "NumType": NUM_TYPE, "Person": PERSON, "Polarity": POLARITY,
             "Poss": POSS, "PronType": PRON_TYPE, "Reflex": REFLEX,
             "Variant": VARIANT}

    def __init__(self):
        self.records = {}
        with open("../data/closed_dict.txt", "r", encoding="utf-8") as closed_dict_file:
            for line in closed_dict_file:
                record_fields = line.rstrip().split("\t")

                for field_num in list(range(self.OTHER, self.VARIANT+1)):
                    if field_num == self.UPOSTAG:
                        continue
                    if field_num < len(record_fields):
                        field = record_fields[field_num]
                        if field:
                            subfields = field.split(";")
                            record_fields[field_num] = subfields
                        else:
                            record_fields[field_num] = []
                    else:
                        record_fields.append([])

                form = record_fields[self.FORM]
                if form not in self.records:
                    self.records[form] = [record_fields]
                else:
                    self.records[form].append(record_fields)

    @staticmethod
    def check_agreement(info, name, data_value, dict_value):
        if data_value != dict_value:
            return [f"CW {info}: Wrong {name}={data_value}, expected {dict_value}"]
        return []

    @staticmethod
    def check_inclusion(info, name, data_value, dict_values, general_values=None):
        possible_values = dict_values if general_values is None else dict_values + general_values
        if data_value not in possible_values:
            return [f"CW {info}: Wrong {name}={data_value}, expected {dict_values}"]
        return []

    def control_token_line(self, sent_id, token_line):
        info = f"{sent_id}:{token_line.fields['ORD']}"
        token_found = True
        if token_line.fields["FORM"] in self.records:
            records = self.records[token_line.fields["FORM"]]
            all_warnings = []
            for record in records:
                if token_line.fields["LEMMA"] != record[self.LEMMA]:
                    continue
                warnings = []
                warnings += self.check_agreement(info, "Translit", token_line.trans["TRANSCRIPT"], record[self.TRANSLIT])
                #warnings += self.check_agreement(info, "Lemma", token_line.fields["LEMMA"], record[self.LEMMA])
                warnings += self.check_agreement(info, "LTranslit", token_line.trans["LEMMA_TRANSCRIPT"], record[self.LTRANSLIT])
                warnings += self.check_agreement(info, "UPOSTAG", token_line.fields["UPOSTAG"], record[self.UPOSTAG])

                warnings += self.check_inclusion(info, "Gloss", token_line.trans["GLOSS"], [record[self.GLOSS]] + record[self.OTHER])
                warnings += self.check_inclusion(info, "DEPREL", token_line.fields["DEPREL"], record[self.DEPREL], ["fixed", "parataxis"])

                feats = token_line.feats
                dict_feats = [attribute for attribute in self.feats if record[self.feats[attribute]]]
                for attribute in feats:
                    if attribute not in dict_feats:
                        warnings += [f"CW {info}: Redundant feature {attribute}={feats[attribute]}"]
                for attribute in self.feats:
                    possible_values = record[self.feats[attribute]]
                    if possible_values:
                        if attribute not in feats:
                            warnings += [f"CW {info}: Missing feature {attribute}={possible_values}"]
                        elif possible_values != ["X"] and feats[attribute] not in possible_values:
                            warnings += [f"CW {info}: Wrong feature values {attribute}={feats[attribute]}, expected {possible_values}"]
                if not warnings:
                    break
                all_warnings.append(warnings)
            else:
                if all_warnings:
                    for warnings in all_warnings:
                        for warning in warnings:
                            print(warning)
                        print("---")
                    print("======")
        elif token_line.fields["UPOSTAG"] in ["DET", "PRON", "ADV", "ADP", "NUM", "CONJ", "PART"]:
            print(f"CW {info}: {token_line.fields['UPOSTAG']} {token_line.fields['FORM']} {token_line.trans['TRANSCRIPT']} not found in the dictionary")
