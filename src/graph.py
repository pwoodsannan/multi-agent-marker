
from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
import operator
import os
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
import random
import json
import pandas as pd

class MarkerStates(TypedDict):
    question : str  # the question which needs to be solved

    answer_1 : dict # the place where the responce 1 for each llm are kept 
    answer_2 : dict # the place where the responce 2 for each llm are kept 
    answer_3 : dict # the place where the responce 3 for each llm are kept 

    score : Annotated[list, operator.add]  # the score each llm gets from eachother it should be a list of 9 

    rank :  list[str]  # the scores ranked to see the best response

load_dotenv()

model_list = [] # the list of models in the env
for i in range(1,11):  
    value = os.environ.get(f"MODEL_{i}")
    if value:
        model_list.append(value)

selected_models = random.sample(model_list, 3)  # pick 3 at random models from the 10 
print(selected_models) 

def intial(state: MarkerStates):
    problem = "Can you capture and write the feeling of nostalgia in 200 words or less"

    return {"question" : problem}

def node_builder(model, node_number):
    def node(state : MarkerStates):
        
        question = state["question"]
        llm = ChatOpenAI(
            model=model,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"],
        )
        response = llm.invoke(question)

        return {f"answer_{node_number}": [{"agent": model, "answer" : response.content}]}

    node.__name__ = f"node_{node_number}"
    return(node)
    

nodes =[] 

for number, model in enumerate(selected_models, start=1):
    nodes.append(node_builder(model, number))



def judge_node(state: MarkerStates):
    combined_responses = [
      f"{state['answer_1'][0]['agent']}: {state['answer_1'][0]['answer']}",
      f"{state['answer_2'][0]['agent']}: {state['answer_2'][0]['answer']}",
      f"{state['answer_3'][0]['agent']}: {state['answer_3'][0]['answer']}",
    ]

    print(combined_responses)
    rankings = []
    for m in selected_models:
        prompt = f"""Question: {state['question']}
        Here are 3 answers:
        {combined_responses}
        Score each model out of 10.
        Reply ONLY with JSON like: {{"<model name>": 7, "<model name>": 8, "<model name>": 6}}"""

        llm = ChatOpenAI(
            model=m,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"],
            )
        
        response = llm.invoke(prompt)      
        try:
            parsed = json.loads(response.content)
        except:
            parsed = {"error": response.content}
        rankings.append({"judge": m, "scores": parsed})

    return {"score": rankings}

def rank_node(state:MarkerStates):
    totals = {}
    for b in state["score"]:
        scores = b["scores"]          #
        
        if "error" in scores:           # skip broken
            continue

        for model, number in scores.items():
            totals[model] = totals.get(model, 0) + number   # accumulate

    ranked = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    return {"rank": ranked}


from langgraph.graph import StateGraph, START, END
# building the graph for the 
graph_builder = StateGraph(MarkerStates)

graph_builder.add_node("intial",intial)
graph_builder.add_node("node_1", nodes[0])
graph_builder.add_node("node_2",nodes[1])
graph_builder.add_node("node_3",nodes[2] )
graph_builder.add_node("judge_node",judge_node)
graph_builder.add_node("rank_node",rank_node)

graph_builder.add_edge(START, "intial")
graph_builder.add_edge("intial", "node_1")
graph_builder.add_edge("intial", "node_2")
graph_builder.add_edge("intial", "node_3")
graph_builder.add_edge("node_1", "judge_node")
graph_builder.add_edge("node_2", "judge_node")
graph_builder.add_edge("node_3", "judge_node")
graph_builder.add_edge("judge_node","rank_node")
graph_builder.add_edge("rank_node",END)

graph = graph_builder.compile()
print(graph.get_graph().draw_mermaid())

result = graph.invoke({})

matrix_data = {}
for entry in result["score"]:
    scores = entry["scores"]
    if "error" in scores:
        continue
    matrix_data[entry["judge"]] = scores

df = pd.DataFrame(matrix_data).T   # .T judges rows, models scored  columns
print(df)

print("\n--- SCOREBOARD ---")
for position, (model, total) in enumerate(result["rank"], start=1):
    print(f"{position}. {model}: {total}")