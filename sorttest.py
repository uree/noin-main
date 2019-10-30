from operator import itemgetter

list_to_be_sorted = {"participants": [{"192.168.0.118": {"noin_balance": 0.00318767823673822, "tmp_value": 0.0}}, {"192.168.0.107": {"noin_balance": 0.00118767823673822, "tmp_value": 0.0}}, {"192.168.0.113": {"noin_balance": 0.00218767823673822, "tmp_value": 0.0}}]}


newlist = sorted(list_to_be_sorted['participants'], key=lambda x: (
        x[]['noin_balance']))
