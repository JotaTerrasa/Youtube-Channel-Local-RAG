from __future__ import annotations

from typing import Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph

from .config import Settings
from .utils import format_timestamp
from .vectorstore import ChromaKnowledgeBase, RetrievedChunk


class AgentState(TypedDict, total=False):
    question: str
    k: int
    contexts: list[RetrievedChunk]
    answer: str
    sources: list[dict[str, Any]]


class YoutubeRagAgent:
    def __init__(self, settings: Settings, knowledge_base: ChromaKnowledgeBase):
        self.settings = settings
        self.knowledge_base = knowledge_base
        self.llm = ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=0.1,
        )
        self.graph = self._build_graph()

    def ask(self, question: str, k: int | None = None) -> dict[str, Any]:
        return self.graph.invoke({"question": question, "k": k or self.settings.retrieve_k})

    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("retrieve", self._retrieve)
        graph.add_node("answer", self._answer)
        graph.set_entry_point("retrieve")
        graph.add_edge("retrieve", "answer")
        graph.add_edge("answer", END)
        return graph.compile()

    def _retrieve(self, state: AgentState) -> AgentState:
        contexts = self.knowledge_base.search(
            state["question"],
            k=int(state.get("k") or self.settings.retrieve_k),
        )
        return {"contexts": contexts}

    def _answer(self, state: AgentState) -> AgentState:
        contexts = state.get("contexts", [])
        if not contexts:
            return {
                "answer": "No he encontrado contenido relevante en la base de conocimiento local.",
                "sources": [],
            }

        context_text = self._format_context(contexts)
        messages = [
            SystemMessage(
                content=(
                    "Eres un agente RAG sobre una base de conocimiento creada a partir "
                    "de videos de YouTube. Responde en espanol, usa solo el contexto "
                    "proporcionado y cita las fuentes con marcadores como [1], [2]. "
                    "Si el contexto no contiene la respuesta, dilo claramente."
                )
            ),
            HumanMessage(
                content=f"Pregunta:\n{state['question']}\n\nContexto recuperado:\n{context_text}"
            ),
        ]
        response = self.llm.invoke(messages)
        answer = str(response.content).strip()
        sources = self._sources(contexts)

        return {
            "answer": f"{answer}\n\n{self._format_sources(sources)}",
            "sources": sources,
        }

    @staticmethod
    def _format_context(contexts: list[RetrievedChunk]) -> str:
        blocks = []
        for index, chunk in enumerate(contexts, start=1):
            metadata = chunk.metadata
            title = metadata.get("title", "Video")
            start = metadata.get("start_time") or format_timestamp(float(metadata.get("start", 0)))
            end = metadata.get("end_time") or format_timestamp(float(metadata.get("end", 0)))
            url = metadata.get("timestamp_url") or metadata.get("source_url", "")
            blocks.append(
                f"[{index}] {title} ({start}-{end})\nURL: {url}\nTexto: {chunk.text}"
            )
        return "\n\n".join(blocks)

    @staticmethod
    def _sources(contexts: list[RetrievedChunk]) -> list[dict[str, Any]]:
        sources = []
        seen = set()
        for index, chunk in enumerate(contexts, start=1):
            metadata = chunk.metadata
            key = (
                metadata.get("video_id"),
                metadata.get("start"),
                metadata.get("end"),
            )
            if key in seen:
                continue
            seen.add(key)
            sources.append(
                {
                    "index": index,
                    "title": metadata.get("title", "Video"),
                    "start_time": metadata.get("start_time", ""),
                    "end_time": metadata.get("end_time", ""),
                    "url": metadata.get("timestamp_url") or metadata.get("source_url", ""),
                    "distance": chunk.distance,
                }
            )
        return sources

    @staticmethod
    def _format_sources(sources: list[dict[str, Any]]) -> str:
        lines = ["Fuentes:"]
        for source in sources:
            when = f"{source['start_time']}-{source['end_time']}".strip("-")
            lines.append(f"[{source['index']}] {source['title']} ({when}) {source['url']}")
        return "\n".join(lines)

