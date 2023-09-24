import gradio as gr
from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch

# Set up the transformer model
model = "tiiuae/falcon-7b"
tokenizer = AutoTokenizer.from_pretrained(model)
pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    device_map="auto",
)

def generate_headlines(topic):
    prompt = f"Create at most 5 headlines that highlight {topic}. The headlines should be concise, attention-grabbing, and suitable for use in a news video."
    sequences = pipeline(
        prompt,
        max_length=200,
        do_sample=True,
        top_k=10,
        num_return_sequences=5,
        eos_token_id=tokenizer.eos_token_id,
    )
    headlines = [seq['generated_text'].split('\n')[1] for seq in sequences if seq['generated_text'].split('\n')[1]]  # Extract headlines from generated sequences
    return "\n".join(headlines)

iface = gr.Interface(
    fn=generate_headlines,
    inputs=gr.inputs.Textbox(placeholder="Enter the topic"),
    outputs="text"
)

iface.launch()
