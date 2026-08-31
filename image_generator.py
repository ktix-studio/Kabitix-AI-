import os
from huggingface_hub import InferenceClient


def generate_image(prompt):
    try:
        client = InferenceClient(
            api_key=os.getenv("HUGGINGFACE_API_KEY"),
            provider="auto"
        )

        image = client.text_to_image(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-schnell"
        )

        return image

    except Exception as e:
        print(f"Image generation error: {e}")
        return None
