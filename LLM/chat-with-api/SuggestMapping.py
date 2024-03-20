from langchain_core.prompts import ChatPromptTemplate
import prompts
from CreateLLM import createLLM

def suggestMapping(columns:str):
  print(columns, type(columns))
  prompt = ChatPromptTemplate.from_template(prompts.MAPPING_SUGGESTION)
  model = createLLM()
  chain = prompt | model

  return chain.invoke({"columns": columns}).content
