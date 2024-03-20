from langchain_core.prompts import ChatPromptTemplate
import prompts
from CreateLLM import createLLM

def suggestDateFormat(data:str):
  prompt = ChatPromptTemplate.from_template(prompts.DATE_FORMAT_SUGGESTION)
  model = createLLM()
  chain = prompt | model

  return chain.invoke({"data": data}).content
