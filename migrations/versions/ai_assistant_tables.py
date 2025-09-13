"""AI Assistant Tables and Vector Support

Revision ID: ai_assistant_v1
Revises: e780388b4935
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = 'ai_assistant_v1'
down_revision = 'e780388b4935'
branch_labels = None
depends_on = None


def upgrade():
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Add vector columns to existing tables
    op.add_column('recipe', sa.Column('embedding', Vector(1536), nullable=True))
    op.add_column('ingredient', sa.Column('embedding', Vector(1536), nullable=True))
    op.add_column('instruction', sa.Column('embedding', Vector(1536), nullable=True))
    op.add_column('instruction', sa.Column('step_number', sa.Integer(), nullable=True))
    
    # Create user_session table
    op.create_table('user_session',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('recipe_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('current_step', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_session_session_id'), 'user_session', ['session_id'], unique=True)
    
    # Create user_conversation table
    op.create_table('user_conversation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('query_type', sa.String(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['user_session.session_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for vector similarity search
    op.execute('CREATE INDEX IF NOT EXISTS recipe_embedding_idx ON recipe USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')
    op.execute('CREATE INDEX IF NOT EXISTS ingredient_embedding_idx ON ingredient USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')
    op.execute('CREATE INDEX IF NOT EXISTS instruction_embedding_idx ON instruction USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')


def downgrade():
    # Drop indexes
    op.execute('DROP INDEX IF EXISTS recipe_embedding_idx')
    op.execute('DROP INDEX IF EXISTS ingredient_embedding_idx')
    op.execute('DROP INDEX IF EXISTS instruction_embedding_idx')
    
    # Drop tables
    op.drop_table('user_conversation')
    op.drop_index(op.f('ix_user_session_session_id'), table_name='user_session')
    op.drop_table('user_session')
    
    # Drop columns
    op.drop_column('instruction', 'step_number')
    op.drop_column('instruction', 'embedding')
    op.drop_column('ingredient', 'embedding')
    op.drop_column('recipe', 'embedding')
    
    # Note: We don't drop the vector extension as it might be used by other parts of the system
