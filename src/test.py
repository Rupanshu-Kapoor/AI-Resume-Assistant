# Approach 1
# C4_200M based LLM

import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
model_name = 'deep-learning-analytics/GrammarCorrector'
torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name).to(torch_device)


def correct_grammar(input_text,num_return_sequences):
  num_beams=10
  batch = tokenizer([input_text],truncation=True,padding='max_length',max_length=64, return_tensors="pt").to(torch_device)
  translated = model.generate(**batch,max_length=64,num_beams=num_beams, num_return_sequences=num_return_sequences, temperature=1.5)
  tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
  return tgt_text


text = 'I have been working for 12 A.M'
print(correct_grammar(text, num_return_sequences=2))




# Approach 2
# API implementation for grammer check
import requests
import json
API_KEY = 'TKW44593kn5Eskwx'

text_to_check = 'I is an engeneer.'

params = {
    'text': text_to_check,
    'language': 'en-GB',
    'ai': 1,
    'key': API_KEY,
}

response = requests.get('https://api.textgears.com/grammar', params=params)

if response.status_code == 200:
    json_text = json.loads(response.text)
    for error in json_text["response"]["errors"]:
      print("wrong words:", error["bad"], end=" ")
      print(", correction:", error["better"])
else:
    print(f"Error: Unable to check grammar. Status code: {response.status_code}")
