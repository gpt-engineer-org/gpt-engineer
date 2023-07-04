from __future__ import annotations

import json
import logging
import re

import openai


# from langchain.chat_models import ChatOpenAI
from langchain.llms.loading import load_llm
from langchain.schema import (  # serialization
    AIMessage,
    HumanMessage,
    SystemMessage,
    messages_from_dict,
    messages_to_dict,
)

logger = logging.getLogger(__name__)


class AI:
    def __init__(self, modelid="gpt-4", temperature=0.1):
        self.temperature = temperature
        self.modelid = fallback_model(modelid)
        self.llm = None

        # self.llm = load_llm("models/" + self.modelid + ".yaml")

        """
        # HUGGINGFACEHUB_API_TOKEN="hf_ASMyUUNgbhrqFnUbfKVixDiVlGDdQiCIKhbg"
        #repo_id = "facebook/mbart-large-50"
        # repo_id = "google/flan-t5-xl"
        # repo_id = "databricks/dolly-v2-3b"
        repo_id = "stabilityai/stablelm-tuned-alpha-3b"
        # repo_id = "Writer/camel-5b-hf"
        # repo_id = "tiiuae/falcon-40b-instruct"
        # repo_id = "TheBloke/Manticore-13B-Chat-Pyg-Guanaco-SuperHOT-8K-fp16"
        self.llm = HuggingFaceHub(repo_id=repo_id, model_kwargs={ "temperature": 0 }) #,
                           # huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN)
        """
        """
        # Run models locally
        self.llm = HuggingFacePipeline.from_model_id(model_id=repo_id,
                                                     task="text-generation",
                                                     model_kwargs={"temperature": 0 })
        """

        """
        # HF Text generation Endpoint
        llm = HuggingFaceTextGenInference(
            inference_server_url="http://localhost:8010/",
            #max_new_tokens=512,
            #top_k=10,
            #top_p=0.95,
            #typical_p=0.95,
            temperature=temperatu re,
            #repetition_penalty=1.03,
        )
        # llm("What did foo say about bar?")
        """

        """
        # Amazon Endpoint
        api_url = "https://<api_gateway_id>.execute-api.<region>.amazonaws.com/LATEST/HF"
        llm = AmazonAPIGateway(api_url=api_url)
        """

        # logging.info(self.llm)
        # self.llm.save("models/" + repo_id + ".yaml")

        # hf_embeddings = HuggingFaceEmbeddings(
        #                  model_name='sentence-transformers/all-MiniLM-L6-v2')
        try:
            # TODO: check for filename, if no yaml, try json
            llm_filename = "models/" + self.modelid + ".yaml"
            # cwd = os.getcwd()
            # logging.info("Working Dir: " + cwd)
            logging.info("LLM file name: " + llm_filename)
            self.llm = load_llm(llm_filename)  # load llm from file
        except Exception as e:
            logging.warning("Unable to load LLM", e)
        """
        try:
            self.chat = ChatOpenAI(model=self.modelid, temperature=temperature)
        except Exception as e:
            # ? try a different model
            logging.warning(e)
        """

    def start(self, system, user):
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=user),
        ]

        return self.next(messages)

    def fsystem(self, msg):
        return SystemMessage(content=msg)

    def fuser(self, msg):
        return HumanMessage(content=msg)

    def fassistant(self, msg):
        return AIMessage(content=msg)

    def combine_messages(self, messages: list[dict[str, str]]):
        msg_dict = messages_to_dict(messages)
        logging.info(msg_dict)
        # prompt = "\n".join(msg_dict =>
        prompt = "\n".join(
            "%s: %s" % (md["type"], md["data"]["content"]) for md in msg_dict
        )
        logging.info("Prompt: " + prompt)
        return prompt

    def next(self, messages: list[dict[str, str]], prompt=None):
        if prompt:
            messages += [self.fuser(prompt)]

        logger.debug(f"Creating a new chat completion: {messages}")

        # r = self.chat(messages)
        mp = self.combine_messages(messages)
        r = self.llm(mp)
        r = re.sub(
            "\\n", "\n", r
        )  # for some reason models sometimes return \n instead of newline?

        if isinstance(r, str):
            r = self.fassistant(r)
        messages += [r]  # AI Message

        logger.debug(f"Chat completion finished: {messages}")

        return messages

    def last_message_content(self, messages):
        m = messages[-1].content
        if m:
            m = m.strip()
        # logging.info(m)
        print(m)
        return m

    def serialize_messages(messages):
        r = "[]"
        if messages and isinstance(messages, list) and len(messages) > 0:
            r = json.dumps(messages_to_dict(messages))
        return r

    def deserialize_messages(jsondictstr):
        r = messages_from_dict(json.loads(jsondictstr))
        return r


def fallback_model(model: str) -> str:
    try:
        openai.Model.retrieve(model)
        return model
    except openai.InvalidRequestError:
        print(
            f"Model {model} not available for provided API key. Reverting "
            "to gpt-3.5-turbo. Sign up for the GPT-4 wait list here: "
            "https://openai.com/waitlist/gpt-4-api\n"
        )
        return "gpt-3.5-turbo"


def serialize_messages(messages):
    return AI.serialize_messages(messages)
