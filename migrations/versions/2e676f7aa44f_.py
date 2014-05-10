"""empty message

Revision ID: 2e676f7aa44f
Revises: 4bcffeac2672
Create Date: 2014-04-23 17:00:11.375647

"""

# revision identifiers, used by Alembic.
revision = '2e676f7aa44f'
down_revision = '4bcffeac2672'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contributors',
    sa.Column('cycle', sa.String(), nullable=True),
    sa.Column('transaction_namespace', sa.String(), nullable=True),
    sa.Column('transaction_id', sa.String(), nullable=False),
    sa.Column('transaction_type', sa.String(), nullable=True),
    sa.Column('transaction_type_description', sa.String(), nullable=True),
    sa.Column('filing_id', sa.String(), nullable=True),
    sa.Column('is_amendment', sa.String(), nullable=True),
    sa.Column('amount', sa.String(), nullable=True),
    sa.Column('date', sa.String(), nullable=True),
    sa.Column('contributor_name', sa.String(), nullable=True),
    sa.Column('contributor_ext_id', sa.String(), nullable=True),
    sa.Column('contributor_type', sa.String(), nullable=True),
    sa.Column('contributor_occupation', sa.String(), nullable=True),
    sa.Column('contributor_employer', sa.String(), nullable=True),
    sa.Column('contributor_gender', sa.String(), nullable=True),
    sa.Column('contributor_address', sa.String(), nullable=True),
    sa.Column('contributor_city', sa.String(), nullable=True),
    sa.Column('contributor_state', sa.String(), nullable=True),
    sa.Column('contributor_zipcode', sa.String(), nullable=True),
    sa.Column('contributor_category', sa.String(), nullable=True),
    sa.Column('organization_name', sa.String(), nullable=True),
    sa.Column('organization_ext_id', sa.String(), nullable=True),
    sa.Column('parent_organization_name', sa.String(), nullable=True),
    sa.Column('parent_organization_ext_id', sa.String(), nullable=True),
    sa.Column('recipient_name', sa.String(), nullable=True),
    sa.Column('recipient_ext_id', sa.String(), nullable=True),
    sa.Column('recipient_party', sa.String(), nullable=True),
    sa.Column('recipient_type', sa.String(), nullable=True),
    sa.Column('recipient_state', sa.String(), nullable=True),
    sa.Column('recipient_state_held', sa.String(), nullable=True),
    sa.Column('recipient_category', sa.String(), nullable=True),
    sa.Column('committee_name', sa.String(), nullable=True),
    sa.Column('committee_ext_id', sa.String(), nullable=True),
    sa.Column('committee_party', sa.String(), nullable=True),
    sa.Column('candidacy_status', sa.String(), nullable=True),
    sa.Column('district', sa.String(), nullable=True),
    sa.Column('district_held', sa.String(), nullable=True),
    sa.Column('seat', sa.String(), nullable=True),
    sa.Column('seat_held', sa.String(), nullable=True),
    sa.Column('seat_status', sa.String(), nullable=True),
    sa.Column('seat_result', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('transaction_id')
    )
    op.create_unique_constraint(None, 'facebook_locations', ['loc_id'])
    op.create_unique_constraint(None, 'facebook_pages', ['page_id'])
    op.create_unique_constraint(None, 'facebook_statuses', ['status_id'])
    op.create_unique_constraint(None, 'facebook_users', ['uid'])
    op.create_unique_constraint(None, 'twitter_tweets', ['id'])
    op.create_unique_constraint(None, 'twitter_users', ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'twitter_users')
    op.drop_constraint(None, 'twitter_tweets')
    op.drop_constraint(None, 'facebook_users')
    op.drop_constraint(None, 'facebook_statuses')
    op.drop_constraint(None, 'facebook_pages')
    op.drop_constraint(None, 'facebook_locations')
    op.drop_table('contributors')
    ### end Alembic commands ###