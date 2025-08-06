from ctransformers import AutoModelForCausalLM

# This script tests loading a pre-trained Mistral model using the ctransformers library.
MODEL_PATH = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

print("Loading model...")

# Load the model
# Set gpu_layers=0 to run on CPU.
# If you have a supported GPU, you can set this to a value > 0
llm = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    model_type="mistral",
    gpu_layers=1,
    temperature=0.1,
    max_new_tokens=256
)

print("Model loaded successfully!")

# --- Test the model ---
prompt = "What is the capital of France?"
print(f"\nPrompt: {prompt}")

response = llm(prompt)

print(f"Response: {response}")