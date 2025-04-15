import torch
from transformers import XLMRobertaForSequenceClassification, XLMRobertaTokenizer

def load_bert():
    model_name = "vanguard-huggingface/biblo-model"
    model = XLMRobertaForSequenceClassification.from_pretrained(model_name)
    tokenizer = XLMRobertaTokenizer.from_pretrained(model_name)
    bert_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(bert_device)
    return model, tokenizer, bert_device

# BERT 모델 초기화
BERT, BERT_TOKENIZER, BERT_DEVICE = load_bert()

def classify_type(prompt: str) -> int:
    inputs = BERT_TOKENIZER(prompt, return_tensors="pt", truncation=True, padding=True)
    inputs = {key: value.to(BERT_DEVICE) for key, value in inputs.items()}
    with torch.no_grad():
        outputs = BERT(**inputs)
    predicted_class = torch.argmax(outputs.logits, dim=1).item()
    print(f"타입 분류 결과: {predicted_class}")
    return predicted_class