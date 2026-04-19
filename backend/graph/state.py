from typing import TypedDict, Dict

class WorkflowState(TypedDict):
    customer_id: str
    old_name: str
    new_name: str

    file_path: str

    extracted_data: Dict
    score: Dict
    summary: str

    status: str