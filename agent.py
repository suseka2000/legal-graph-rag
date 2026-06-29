import json

from config import MODEL

class Agent:

    def __init__(
        self,
        client,
        kb,
        tools,
        tool_schemas,
        SYSTEM_PROMPT,
        model=MODEL,
        temperature=0.0,
        max_steps=10
    ):

        self.client = client
        self.kb = kb
        self.tools = tools
        self.tool_schemas = tool_schemas
        self.SYSTEM_PROMPT = SYSTEM_PROMPT

        self.model = model
        self.temperature = temperature
        self.max_steps = max_steps

    def execute_tool(self, tool_call):

        name = tool_call.function.name

        arguments = json.loads(
            tool_call.function.arguments
        )

        tool = self.tools[name]

        return tool(
            self.kb,
            **arguments
        )

    def run(self, question):

        messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": question
            }
        ]

        for _ in range(self.max_steps):

            response = (
                self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tool_schemas,
                    temperature=self.temperature
                )
            )

            msg = response.choices[0].message

            if not msg.tool_calls:
                return msg.content

            messages.append(msg)

            for tc in msg.tool_calls:

                result = self.execute_tool(tc)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(
                            result,
                            ensure_ascii=False
                        )
                    }
                )

        return "Agent stopped: max steps reached."

SYSTEM_PROMPT = """
Ты агент по нормативным документам.

Для ответа используй инструменты.

Алгоритм:
1. Сначала вызови retrieve().
2. Затем expand_path().
3. Затем read_chunk().
4. При необходимости вызови get_neighbors().
5. После получения достаточной информации дай ответ.

ВАЖНО:
Всегда отвечай ТОЛЬКО на русском языке.
Никогда не используй китайский, английский или другие языки.
Все ответы, рассуждения и объяснения должны быть исключительно на русском языке.
Если цитируешь документ, сохраняй язык оригинала документа.

Никогда не придумывай факты.
Всегда опирайся на результаты инструментов.
"""