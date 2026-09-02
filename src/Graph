from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
import operator


class MarkerStates(TypedDict):
    question : str  # the question which needs to be solved

    answers: Annotated[list, operator.add]

    score : Annotated[list, operator.add]  # the score each llm gets from eachother it should be a list of 9 

    rank :  list[str]  # the scores ranked to see the best response


import os
from langchain_openai import ChatOpenAI

def make_llm_node(model_id: str):
    async def llm_call(state: MarkerStates):
        question = state["question"]
        llm = ChatOpenAI(
            model=model_id,
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"],
        )
        response = await llm.ainvoke(question)
        return {"answers": [{"agent": model_id, "answer": response.content}]}
    return llm_call
    

node_1 = make_llm_node(MODEL_1)
node_2 = make_llm_node(MODEL_2)
node_3 = make_llm_node(MODEL_3)

from langgraph.graph import StateGraph, START, END

graph_builder = StateGraph(MarkerStates)

graph_builder.add_node("interface",input)
graph_builder.add_node("agent_1",node_1 )
graph_builder.add_node("agent_2",node_2 )
graph_builder.add_node("agent_3",node_3 )

graph_builder.add_edge(START, input)
graph_builder.add_edge(input, node_1)
graph_builder.add_edge(input, node_2)
graph_builder.add_edge(input, node_3)




graph = graph_builder.compile()