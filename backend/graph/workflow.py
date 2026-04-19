from backend.agents.validation_agent import validate
from backend.agents.document_processor import process_document
from backend.agents.confidence_scorer import score_data
from backend.agents.summary_agent import summarize


def build_graph():

    def run(self, state):

        # Validation
        state = validate(state)

        # Document processing
        extracted = process_document(
            state["file_path"],
            state["old_name"],
            state["new_name"]
        )
        state["extracted_data"] = extracted

        # Scoring
        score = score_data(
            state["old_name"],
            state["new_name"],
            extracted
        )
        state["score"] = score

        # Summary
        state["summary"] = summarize(score)

        return state

    return type("Graph", (), {"invoke": run})()