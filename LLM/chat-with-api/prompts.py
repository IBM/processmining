from langchain.agents.structured_chat.prompt import FORMAT_INSTRUCTIONS

PREFIX = """<s><<SYS>>Assistant is a expert JSON builder designed to assist with a wide range of tasks.

 To answer the question of the user, the assistant can use tools. Tools available to Assistant are:

:<</SYS>>"""
FORMAT_INSTRUCTIONS = """RESPONSE FORMAT INSTRUCTIONS
----------------------------

When responding to me, please output a response in one of two formats:

**Option 1:**
Use this if you want the human to use a tool.
Markdown code snippet formatted in the following schema:

```json
{{{{
    "action": string, \\\\ The action to take. Must be one of {tool_names}
    "action_input": string \\\\ The input to the action
}}}}
```

**Option #2:**
Use this if you want to respond directly to the human. Markdown code snippet formatted in the following schema:

```json
{{{{
    "action": "Final Answer",
    "action_input": string \\\\ You should put what you want to return to use here in a human readable text.
}}}}
```"""

SUFFIX = """Begin! Remember, all actions must be formatted as markdown JSON strings.
  Question: {input}
  Thought:{agent_scratchpad}"""
  
DATE_FORMAT_SUGGESTION= """Provide a date format (java) for the data below, do not provide explanations and answer like : 'a suggested data format is': {data}"""

MAPPING_SUGGESTION = """with the columns of the csv file: {columns}, suggest the column index and column name of the column that best corresponds to 'activity name', the 'start time ' and the 'case id'. 
For every suggestion give the column name and index in the cvs, if you do not find a corespondent column do not make suggestion. You must answer starting with :'here is a suggestion for column binding:', do not add any other observation.'"""