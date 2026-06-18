from llm_interface import LLMInterface
from openai import OpenAI

class ChatGPTLLM(LLMInterface):

  def __init__(self):
    # OpenAI will automatically use OPENAI_API_KEY environemnt variable as api key,
    # but in future I can parse an api key string that will act as the API key instead.
    self.client = OpenAI()

  def prompt_llm(self, prompt: str) -> str:

    response = self.client.responses.create(
      model="gpt-5.4-mini",
      input=[
        {
          "role": "developer",
          "content": [
            {
              "type": "input_text",
              "text": "You are writing a prompt to a video generation tool. You must generate an appealing scene, based on the product that would help to advertise it. You must consider the target audience that the product might be for, and generate your prompt based off of what these target audiences would enjoy/appeal to (ie. a pricier product is more likely to attract people who have excess wealth etc). This video should last roughly 5-10 seconds (you decide). The video generation tool will have acess to the actual real life image of the product, so make sure the tool uses it. Make sure you write in such a way that a video image generation tool would understand it, while also considering the common limitations of video generation tools (ie. avoid hands, clocks (unless the product is a clock)). Your input from the user will define the product attributes. Do not try to implement markdown in your response. Consider VERY carefully about space; give instructions sequentially about how things are moving. Be aware that the video generation tool can block videos that may cover sensistive content, so be especially careful in these circumstances, including prompts referencing children (typically video generation tools block videos being generated of children, so avoid them where possible.)."
            }
          ]
        },
        {
          "role": "user",
          "content": [ 
            {
              "type": "input_text",
              "text": prompt
            }
          ]
        }
      ],
      text={
        "format": {
          "type": "text"
        },
        "verbosity": "medium"
      },
      reasoning={
        "effort": "medium",
        "summary": "auto"
      },
      tools=[],
      store=True,
      include=[
        "reasoning.encrypted_content",
        "web_search_call.action.sources"
      ]
    )

    return response.output_text
