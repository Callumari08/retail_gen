from llm_interface import LLMInterface
from api_implementations.chatgpt import ChatGPTLLM
import gather_data
from product_data import ProductData
from api_implementations.google import VeoVideoGen

from sys import argv

llm = ChatGPTLLM()
api_key_path = argv[2]
video_gen = VeoVideoGen(api_key_path)

product_title = argv[1]
print("Your product is:", product_title)

products: list[ProductData] = gather_data.gather_data("/home/cal/Code/py/retail_gen/products_2026-06-17_13-57-10.tsv")
headphones: ProductData = gather_data.get_product_by_title(products, product_title)

print(headphones.print_data())

llm_response = llm.prompt_llm(headphones.print_data())

print("LLM response:", llm_response)

video_gen.prompt_video_gen(llm_response, product_title.strip().replace(" ", "").lower())
