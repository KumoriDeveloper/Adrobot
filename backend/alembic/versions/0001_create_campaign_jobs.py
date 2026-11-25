from alembic import op
import sqlalchemy as sa

revision = "0001_campaign_jobs"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "campaign_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campaign_name", sa.String(length=255), nullable=False),
        sa.Column("geo", sa.String(length=2), nullable=False),
        sa.Column("offer_id", sa.Integer(), nullable=False),
        sa.Column("keitaro_campaign_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

def downgrade():
    op.drop_table("campaign_jobs")
