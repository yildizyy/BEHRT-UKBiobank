import sys
print(sys.executable)

import pandas as pd
df = pd.read_csv('./xxx.csv')
df['code'] = df['code'].str.replace(r"['\[\]]", '', regex=True)
df['age'] = df['age'].str.replace(r"['\[\]]", '', regex=True)

# Function to tokenize a string containing a list of words
def tokenize_list(cell_value):
    if isinstance(cell_value, str):
        return cell_value.strip('[]').replace(',', '').split()
    elif isinstance(cell_value, int):
        return str(cell_value).split()
    else:
        return []  # Handle other data types as needed

df = df.applymap(tokenize_list)

from typing import Dict
import json
import pandas as pd
from typing import List 

def get_all_codes(df: pd.DataFrame, codes_to_ignore: List[str]) -> List[str]:
    codes = []
    for df_list_codes in list(df['code']):
        codes.extend(df_list_codes)
    return list(set(codes) - set(codes_to_ignore))

def get_bert_tokens() -> Dict[str, int]:
    return {
      "PAD": 0,
      "UNK": 1,
      "SEP": 2,
      "CLS": 3,
      "MASK": 4,
    }
    
def build_token2index_dict(df: pd.DataFrame) -> Dict[str, int]:
    token2inx_dict = get_bert_tokens()
    next_index = max(token2inx_dict.values()) + 1
    
    codes = get_all_codes(df= df, codes_to_ignore=token2inx_dict.keys())
    for code in codes:
        token2inx_dict[str(code)] = next_index
        next_index += 1
    return token2inx_dict

def create_token2index_file(df: pd.DataFrame, output_file_path: str):
    token2inx_dict = build_token2index_dict(df= df)
    with open(output_file_path, 'w') as f:
        json.dump(token2inx_dict, f)
        print(f'token2inx_caliber was created, path={output_file_path}')

token2index_dict = build_token2index_dict(df)
create_token2index_file(df, './token2idx2_caliber.json')

import json
import pickle

BertVocab = {}

with open(r'./token2idx2_caliber.json') as f:
    token2idx = json.load(f)
    print(token2idx)
idx2token = {}
for x in token2idx:
    idx2token[token2idx[x]] = x
BertVocab['token2idx'] = token2idx
BertVocab['idx2token'] = idx2token

# save to pickle.

with open(r'./vocab0_caliber.pkl', 'wb') as handle:
    pickle.dump(BertVocab, handle, protocol=pickle.HIGHEST_PROTOCOL)


