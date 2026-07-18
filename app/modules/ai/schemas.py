# AI chat Pydantic schemas.
# Will contain:
#   - ChatRequest (message, conversation_id optional, stream optional)
#   - ChatResponse (message, conversation_id, usage tokens)
#   - ChatStreamChunk (delta content for SSE)
#   - OpenAIUsageResponse (prompt_tokens, completion_tokens, total_tokens)
