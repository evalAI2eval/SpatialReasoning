from ollama import chat
from ollama import ChatResponse
from dataclasses import dataclass


class ModelQuery:
    def __init__(self, model: str = 'gemma3', system_prompt: str = 'You are a helpful assistant.', role: str = 'user', prompt_content: list = None, think: bool = False):
        self.model: str = model
        self.system_prompt: str = system_prompt
        self.role: str = role
        self.prompt_content: list = prompt_content if prompt_content is not None else ['Why is the sky blue', 'What is the meaning of life?']
        self.responses: list = None
        self.think: bool = think

    def run_query(self):
        self.responses = []
        for content in self.prompt_content:
            response: ChatResponse = chat(model=self.model, messages=[
                {
                    'role': 'system',
                    'content': self.system_prompt,
                },
                {
                    'role': self.role,
                    'content': content,
                },
            ],
            stream=False, 
            think=self.think)
            self.responses.append(response)



if __name__ == "__main__":
    query = ModelQuery()
    query.run_query()
    for response in query.responses:
        print(f'{response.message.content}\n')