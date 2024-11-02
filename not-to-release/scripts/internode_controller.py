
class InternodeController:

    def __init__(self):
        self.sent_id = 0
        self.tokens = []

    def new_tree(self, sent_id, tokens):
        self.sent_id = sent_id
        self.tokens = tokens
        for token in tokens:
            if "-" not in token.fields["ORD"] and token.fields["HEAD"] != "0":
                parents = [other_token for other_token in tokens if other_token.fields["ORD"] == token.fields["HEAD"]]
                assert len(parents) == 1
                parent = parents[0]
                parent.add_child(token)

    def control_tree(self, sent_id, tokens):
        self.sent_id = sent_id
        self.tokens = tokens
        for token in tokens:
            if "-" not in token.fields["ORD"] and token.fields["HEAD"] != "0":
                parents = [other_token for other_token in tokens if other_token.fields["ORD"] == token.fields["HEAD"]]
                assert len(parents) == 1
                parent = parents[0]
                parent.add_child(token)

        for token in self.tokens:
            children = token.children
            self.control_adp_case_agreement(token, children)
            self.control_nominal_agreement(token, children)

    def control_adp_case_agreement(self, token, children):
        adp_case_children = [child for child in children if child.fields["UPOSTAG"] == "ADP"
                             and child.fields["DEPREL"] == "case" and "Case" in token.feats]
        cases = set(child.feats["Case"] for child in adp_case_children)
        infos = [f"{self.sent_id}:{child.fields['ORD']}" for child in adp_case_children]
        if len(cases) > 1:
            print(f"ICN : {infos} do not have identical case: {cases}")
        elif len(cases) == 1:
            case = list(cases)[0]
            if "Case" in token.feats and token.feats["Case"] != case:
                print(f"ICN : {infos} case {case} does not agree with parent {token.feats['Case']}")

    def control_nominal_agreement(self, token, children):
        nominal_feats = ["Case", "Gender", "Number"]
        if token.fields["UPOSTAG"] in ["NOUN", "ADJ", "PROPN"]:
            nominal_children = [child for child in token.children if child.fields["DEPREL"] in ["amod", "det"] and
                                any(feat for feat in nominal_feats if feat in child.feats)]
            for feat in nominal_feats:
                if feat not in token.feats:
                    info = f"{self.sent_id}:{token.fields['ORD']}"
                    print(f"ICN : {info} nominal token lacks {feat}")
                    continue
                disagreeing = [child for child in nominal_children if feat in child.feats
                               and child.feats[feat] != token.feats[feat]]
                if disagreeing:
                    their_feats = set(child.feats[feat] for child in disagreeing)
                    infos = [f"{self.sent_id}:{child.fields['ORD']}" for child in disagreeing]
                    print(f"ICN : {infos} nominal children disagree {their_feats} with parent {token.feats[feat]}")


