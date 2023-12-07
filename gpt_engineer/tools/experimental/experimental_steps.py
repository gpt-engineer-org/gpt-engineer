import tempfile

from langchain.schema import SystemMessage, HumanMessage

from gpt_engineer.core.ai import AI
from gpt_engineer.core.chat_to_files import overwrite_code_with_edits
from gpt_engineer.core.files_dict import FilesDict
from gpt_engineer.core.default.disk_memory import DiskMemory
from gpt_engineer.core.default.paths import IMPROVE_LOG_FILE
from gpt_engineer.core.default.steps import setup_sys_prompt_existing_code, curr_fn
from gpt_engineer.core.preprompts_holder import PrepromptsHolder
from gpt_engineer.core.base_memory import BaseMemory
from gpt_engineer.tools.experimental.code_vector_repository import CodeVectorRepository


def improve_automatic_file_selection(
    ai: AI,
    prompt: str,
    code: FilesDict,
    memory: BaseMemory,
    preprompts_holder: PrepromptsHolder,
):
    code_vector_repository = CodeVectorRepository()
    # ToDo: Replace this hacky way to get the right langchain document format
    temp_dir = tempfile.mkdtemp()
    temp_saver = DiskMemory(temp_dir)
    for file, content in code.items():
        temp_saver[file] = content
    code_vector_repository.load_from_directory(temp_dir)
    relevant_documents = code_vector_repository.relevent_code_chunks(prompt)
    relevant_code = FilesDict()
    for doc in relevant_documents:
        file_path = os.path.relpath(doc.metadata["filename"], temp_dir)
        relevant_code[file_path] = code[file_path]
    print(
        "Relevant documents to be modified are: "
        + "\n".join(sorted(relevant_code.keys()))
    )
    preprompts = preprompts_holder.get_preprompts()
    messages = [
        SystemMessage(content=setup_sys_prompt_existing_code(preprompts)),
    ]
    # Add files as input
    messages.append(HumanMessage(content=f"{relevant_code.to_chat()}"))

    messages.append(HumanMessage(content=f"Request: {prompt}"))

    messages = ai.next(messages, step_name=curr_fn())
    chat = messages[-1].content.strip()
    overwrite_code_with_edits(chat, code)
    memory[IMPROVE_LOG_FILE] = chat
    return code
