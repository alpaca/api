from __future__ import division
import queries2 as queries
from app.models import FacebookUser
from sqlalchemy import and_
import operator


FILTER_FUNS = {
    'age': lambda x: queries.age(age=[int(x.split('-')[0]),
                                      int(x.split('-')[-1])])
}


def like_breakdown(user_lst):
    cats = {}
    for idx, user in enumerate(user_lst):
        for page in user.pages:
            if page.type in cats:
                cats[page.type] += 1
            else:
                cats[page.type] = 1
        print "User %i" % idx
    return cats


def get_users(users, **kwargs):
    filters = []
    for key in kwargs:
        fn = FILTER_FUNS[key]
        filters.append(fn(kwargs[key]))
    return users.filter(
        and_(
            *filters
        )).all()


def dic_to_sorted(cats):
    sorted_cats = sorted(cats.iteritems(), key=operator.itemgetter(1),
                         reverse=True)
    total = sum([int(x[1]) for x in sorted_cats])
    out_str = ''
    for pair in sorted_cats:
        out_str += str(pair[0]) + ' : ' + str(pair[1]) + ' (' + \
            str(int(pair[1])*100/total) + '%)\n'
    return out_str


if __name__ == "__main__":
    users = FacebookUser.query
    filtered_users = get_users(users, age='20-30')

    categories = like_breakdown(filtered_users)

    print dic_to_sorted(categories)
