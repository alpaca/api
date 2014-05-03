"""empty message

Revision ID: 4fb51e2ca8ca
Revises: 2abaf2aa7bb9
Create Date: 2014-04-29 13:03:22.245892

"""

# revision identifiers, used by Alembic.
revision = '4fb51e2ca8ca'
down_revision = '2abaf2aa7bb9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('facebook_friends')
    op.drop_table('facebook_families')
    op.drop_table('facebook_statuses')
    op.drop_table('facebook_locations')
    op.add_column('facebook_pages', sa.Column('misc', sa.String(), nullable=True))
    op.add_column('facebook_users', sa.Column('misc', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('facebook_users', 'misc')
    op.drop_column('facebook_pages', 'misc')
    op.create_table('facebook_locations',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('city', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('loc_id', sa.BIGINT(), server_default="nextval('facebook_locations_loc_id_seq'::regclass)", nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('zip', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('country', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('longitude', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('state', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('street', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('address', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('latitude', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('gid', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('loc_id', name=u'facebook_locations_pkey')
    )
    op.create_table('facebook_statuses',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('like_count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('uid', sa.BIGINT(), autoincrement=False, nullable=True),
    sa.Column('status_id', sa.BIGINT(), server_default="nextval('facebook_statuses_status_id_seq'::regclass)", nullable=False),
    sa.Column('message', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('time', sa.DATE(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('status_id', name=u'facebook_statuses_pkey')
    )
    op.create_table('facebook_families',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('uid', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('relationship', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('profile_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['profile_id'], [u'facebook_users.uid'], name=u'facebook_families_profile_id_fkey'),
    sa.ForeignKeyConstraint(['uid'], [u'facebook_users.uid'], name=u'facebook_families_uid_fkey'),
    sa.PrimaryKeyConstraint('uid', 'profile_id', name=u'facebook_families_pkey')
    )
    op.create_table('facebook_friends',
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('uid2', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('uid1', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['uid1'], [u'facebook_users.uid'], name=u'facebook_friends_uid1_fkey'),
    sa.ForeignKeyConstraint(['uid2'], [u'facebook_users.uid'], name=u'facebook_friends_uid2_fkey'),
    sa.PrimaryKeyConstraint('uid2', 'uid1', name=u'facebook_friends_pkey')
    )
    ### end Alembic commands ###
