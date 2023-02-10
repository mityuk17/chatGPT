import openai
openai.api_key = ""

async def text(text):
    model_engine = "text-davinci-003"
    prompt = text

    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        temperature=0.5,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return completion
async def create_image(text, size):
    response = openai.Image.create(
        prompt=text,
        n=1,
        size=f"{size}*{size}"
    )
    image_url = response['data'][0]['url']
    return image_url