from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
import operator
import os
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
import random

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
    problem = "Can you capture and write about the feeling of nostalgia in 200 words or less"

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
        state["answer_1"][0]["answer"],
        state["answer_2"][0]["answer"],
        state["answer_3"][0]["answer"],
    ]
    print(combined_responses)

    for m in selected_models:
            prompt = f"Can you rank these pieces of text {combined_responses} based on the {state['question']} out of a mark of 10"
            llm = ChatOpenAI(
            model=m,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"],
            )
            rankings = [] 
            response = llm.invoke(prompt)      
            rankings = rankings.append({"judge": m, "scores": response.content})

    return {"score": rankings}



from langgraph.graph import StateGraph, START, END

graph_builder = StateGraph(MarkerStates)

graph_builder.add_node("intial",intial)
graph_builder.add_node("node_1", nodes[0])
graph_builder.add_node("node_2",nodes[1])
graph_builder.add_node("node_3",nodes[2] )

graph_builder.add_edge(START, "intial")
graph_builder.add_edge("intial", "node_1")
graph_builder.add_edge("intial",  "node_2")
graph_builder.add_edge("intial",  "node_3")
graph_builder.add_edge("node_1", END)
graph_builder.add_edge("node_2", END)
graph_builder.add_edge("node_3", END)


graph = graph_builder.compile()