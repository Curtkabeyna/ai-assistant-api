# Message SQLAlchemy model.
# Will contain:
#   - Message model (id, conversation_id, role, content, token_count)
#   - Relationships: conversation
#   - ForeignKey to conversations table
#   - Index on conversation_id + created_at
