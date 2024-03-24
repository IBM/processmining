import gradio as gr
from CreateLLM import createLLM
from ProjectDetailTool import ProjectDetailTool
from ProjectsTool import ProjectsTool
from CreateProjectTool import CreateProjectTool
from DeleteProjectTool import DeleteProjectTool
from MiningTool import MiningTool
from SetDataMappingTool import SetDataMappingTool
from SetDateFormatTool import SetDateFormatTool
from GetModelStatisticsTool import GetModelStatisticsTool


from LoadDataTool import LoadDataTool
from CustomParser import CustomParser
import prompts

from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferWindowMemory
from langchain.memory import ChatMessageHistory

from SuggestMapping import suggestMapping

import urllib3
urllib3.disable_warnings()

import os


def checkEnvironment():
    if not 'GENAI_KEY' in os.environ:
        print('Please set env variable GENAI_KEY to your IBM Generative AI key')
        exit()
    if not 'GENAI_API' in os.environ:
        print('Please set env variable GENAI_API to your IBM Generative AI  endpoint URL')
        exit()
    if not 'PM_API_URL' in os.environ:
        print('Please set env variable PM_API_URL to process mining API URL')
        exit()
    if not 'PM_API_USER' in os.environ:
        print('Please set env variable PM_API_USER to process mining API USER')
        exit()
    if not 'PM_API_KEY' in os.environ:
        print('Please set env variable PM_API_KEY to process mining API key')
        exit()
    if not 'COS_API_KEY_ID' in os.environ:
        print('Please set env variable COS_API_KEY_ID to Cloud Object Storage API Key')
        exit()
    if not 'COS_INSTANCE_CRN' in os.environ:
        print('Please set env variable COS_INSTANCE_CRN to Cloud Object Storage Intance CRN')
        exit()
        
        
def initializeLLMAgent():

   
    llm = createLLM()

    tools = [MiningTool(),CreateProjectTool(), GetModelStatisticsTool(), DeleteProjectTool(), 
            ProjectDetailTool(), 
             LoadDataTool(), SetDataMappingTool(), SetDateFormatTool()];
    
    memory = ConversationBufferWindowMemory(
       memory_key="chat_history", k=5, return_messages=True, output_key="output"
    )
    
    pm_agent = initialize_agent(tools, llm,
       agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True, 
       early_stopping_method="generate", 
       memory=memory,
       agent_kwargs = {
        'output_parser': CustomParser(),
        'prefix':prompts.PREFIX,
        'format_instructions': prompts.FORMAT_INSTRUCTIONS,
        'suffix': prompts.SUFFIX
        })
     
    return pm_agent;


checkEnvironment()
    
print("Creating the LLMAgent")

pm_agent = initializeLLMAgent()

def add_text(history, text):
    history = history + [(text, None)]
    return history, ""

def bot(history):
    response = infer(history[-1][0])
    history[-1][1] = response['result']
    return history

def infer(question):
    query = f'[INST] {question}[/INST]'
    response={}
    res =  pm_agent.invoke({'input' : query});
    response['result'] =res['output']
    return response
    

css="""
#col-container {max-width: 700px; margin-left: auto; margin-right: auto;}
"""

title = """
<div style="text-align: center;max-width: 700px;">
    <h1>Chat with IBM Process Mining</h1>
    <p style="text-align: center;">This sample allow to interact with IBM Process Mining projects:
    <li>how many events in project XX</li>
    <li>how many cases in project XX</li>
    <li>who is the owner of project XX</li>

    <li>can you create a project named YY</li>
    <li>can you delete the project named YY</li>
    <li>can you upload the file myfile.csv to the project named YY</li>
    <li>please do the mining of project A</li>

    </p>
 </div>
"""

with gr.Blocks(css=css, title='Chat with IBM Process Mining') as demo:
    with gr.Column(elem_id="col-container"):
        gr.HTML(title)
        
        chatbot = gr.Chatbot()
        question = gr.Textbox(label="Question", placeholder="Type your question and hit Enter ")
        submit_btn = gr.Button("Send message")
 
    question.submit(add_text, [chatbot, question], [chatbot, question]).then(
        bot, chatbot, chatbot
    )
    
    submit_btn.click(add_text, [chatbot, question], [chatbot, question]).then(
        bot, chatbot, chatbot
    )

demo.launch()
