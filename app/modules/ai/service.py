# AI chat business logic — orchestrates OpenAI, messages, conversations.
# Will contain:
#   - ChatService.send_message() — full chat flow
#   - ChatService.stream_message() — async generator for SSE
#   - Save user message + assistant response to DB
#   - Build context from conversation history
#   - Handle token limits and truncation
