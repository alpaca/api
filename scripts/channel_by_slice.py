from __future__ import division
import queries2 as queries
from app.models import FacebookUser
from sqlalchemy import and_
import operator
import itertools


FILTER_FUNS_K = {
    'age': lambda x: queries.age(age=[int(x.split('-')[0]),
                                      int(x.split('-')[-1])]),
    'sex': lambda x: queries.sex(sex=x),
    # 'employer': lambda _x: queries.employerInList(reduce(lambda x, y: x + y,
    #             map(lambda cat: cat[1:], queries.readEmploy(_x.split('NOT::')[-1])), []),
    #                                              opposite=("NOT::" in _x)),
    'currentcity': lambda _x: queries.currentCityInList(readFile(_x.split('NOT::')[-1], int),
                                                 opposite=("NOT::" in _x)),
    'employer': lambda _x: queries.employerInList(readFile(_x.split('NOT::')[-1], str),
                                                 opposite=("NOT::" in _x))

}

def readFile(fname,_type):
    arr = []
    with open(fname,'r') as f:
        for line in f:
            arr.append(_type(line.rstrip(',\t\n').lower()))
    return arr

CATEGORIES_K = {
    'musical': ["album", "concert tour", "concert venue", "music",
                "music award", "music chart", "music video",
                "musical genre", "musical instrument", "musician/band",
                "song"],
    'art': ["art", "artist", "arts/entertainment/nightlife",
            "arts/humanities website", "dancer",
            "museum/art gallery"],
    'book': ["author", "book", "book genre", "book series", "book store",
             "library", "literary editor"],
    'sports': ["amateur sports team", "athlete", "professional sports team",
               "recreation/sports website", "school sports team", "sport",
               "sports event", "sports league", "sports venue",
               "sports/recreation/activities"],
    'science': ["biotechnology", "chemicals"],
    'finance': ["bank/financial institution", "bank/financial services"],
    'business': ["business person", "business services",
                 "business/economy website", "consulting/business services"],
    'family': ["baby goods/kids goods", "neighborhood"],
    'food': ["food", "food/beverages", "food/grocery"],
    'home_living': ["appliances", "bags/luggage", "furniture", "home decor",
                    "home improvement", "home/garden website",
                    "home/garden website", "household supplies",
                    "neighborhood"],
    'health': ["diseases", "health/beauty", "health/medical/pharmaceuticals",
               "health/medical/pharmacy", "health/wellness website",
               "hospital/clinic"],
    'medical': ["doctor", "health/medical/pharmaceuticals",
                "health/medical/pharmacy", "hospital/clinic"],
    'government': ["community/government", "government official",
                   "government organization", "government website"],
    'community': ["community", "community organization",
                  "community/government"],
    'tech': ["aerospace/defense", "computers", "computers/internet website",
             "computers/technology", "internet/software", "phone/tablet",
             "software"],
    'education': ["concentration or major", "course", "education",
                  "education website", "education/work status", "school",
                  "teacher", "university"],
    'tv': ["tv", "tv channel", "tv genre", "tv network", "tv show",
           "tv/movie award"],
    'leisure': ["bar", "club", "drink", "drugs"],
    'religious': ["church/religious organization", "religion"],
    'movie': ["movie", "movie character", "movie genre", "movie theater"],
    'politics': ["political ideology", "political organization",
                 "political party", "politician"]
}


def like_breakdown(user_lst):
    cats = {}
    for idx, user in enumerate(user_lst):
        for page in user.pages:
            cat = page.type
            if not page.type:
                print "Caught a page without a type."
                continue
            for group in CATEGORIES_K:
                if page.type.lower() in CATEGORIES_K[group]:
                    cat = group
                    break

            if cat in cats:
                cats[cat] += 1
            else:
                cats[cat] = 1
        # print "User %i" % idx
    return cats


def get_users(_users, **kwargs):
    filters = []
    for key in kwargs:
        fun = FILTER_FUNS_K[key]
        filters.append(fun(kwargs[key]))

    return _users.filter(
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


def compute_diffs(all_like_dists):
    statistically_meaningful_cutoff = 25
    diffs = {}
    '''
    diffs = {
        [15-35, m]: {
            community: +0.8,
            sports:+2.7,
            ...
        }
    '''
    # compute baseline
    baseline = {}
    baseline_total = 0
    for group in all_like_dists:
        for like_cat in group.like_breakdown:
            try:
                baseline[like_cat] += group.like_breakdown[like_cat]
            except KeyError:
                baseline[like_cat] = group.like_breakdown[like_cat]

            baseline_total += group.like_breakdown[like_cat]

    for group in all_like_dists:
        diff = {}
        for like_cat in group.like_breakdown:
            if group.like_breakdown[like_cat] > statistically_meaningful_cutoff:
                diff[like_cat] =\
                    ((group.like_breakdown[like_cat]/group.total -
                        baseline[like_cat]/baseline_total)/(baseline[like_cat]/baseline_total))
        diffs[str(group.filters)] = diff
        # compute diff to baseline and add to diffs dict.
    return diffs


def generate_report(diffs, lbobjs):

    report = ""
    for diff in diffs:
        count = -1
        for obj in lbobjs:
            if str(obj.filters) == diff:
                count = obj.user_count
        sorted_dic = sorted(diffs[diff].iteritems(),
                            key=operator.itemgetter(1))
        report += "=== %s == (%i) ========\n" % (diff.upper(), count)

        for i in range(5):
            try:
                report += "%s: %s\n" % (str(sorted_dic[-(i+1)][0]),
                                        str(sorted_dic[-(i+1)][1]))
            except IndexError:
                pass
        report += '\n'
        for i in range(5):
            try:
                report += "%s: %s\n" % (str(sorted_dic[i][0]),
                                        str(sorted_dic[i][1]))
            except IndexError:
                pass
        report += "\n"
    return report

def generate_csv(diffs, lbobjs):
    csv = ""
    for diff in diffs:
        count = -1
        for obj in lbobjs:
            if str(obj.filters) == diff:
                count = obj.user_count
        sorted_dic = sorted(diffs[diff].iteritems(),
                            key=operator.itemgetter(1))
        csv += "%s,%i\n" % (diff.upper().replace(',',';'), count) # [15-24,M], 1000
        for i in range(5):
            try:
                csv += "%s,%s\n" % (str(sorted_dic[-(i+1)][0]),
                                        str(sorted_dic[-(i+1)][1]))
            except IndexError:
                pass

        for i in range(5):
            try:
                csv += "%s,%s\n" % (str(sorted_dic[i][0]),
                                        str(sorted_dic[i][1]))
            except IndexError:
                pass
        csv += "\n"
    csv += '\n'
    return csv



class LikeBreakdown(object):
    def __init__(self, like_breakdown=None, filters={}, count=0):
        self.filters = filters
        self.like_breakdown = like_breakdown
        self.user_count = count
        print self.user_count
        self.total = sum([self.like_breakdown[k] for k in self.like_breakdown])

def flatten_tuple(tup):
    output = []
    for item in tup:
        output += flatten_tuple(item) if hasattr(item, "__iter__") else [item]
    return output

if __name__ == "__main__":

    def main(filters=None, user_count_cutoff=0, out_format=None):
        USERS = FacebookUser.query.filter(FacebookUser.pages)
        print len(USERS.all())
        like_groups = []

        if filters == None:
            filters = {'age': ['15-25', '25-35', '35-45', '45-55', '55-95'],
                       'employer': ['Employment.csv', 'NOT::Employment.csv'],
                       'currentcity': ['Location10th.tsv', 'NOT::Location10th.tsv'],
                       'sex': ['m', 'f']}

        all_permutations = []
        for key in filters:
            if all_permutations == []:
                all_permutations = filters[key]
            else:
                all_permutations = [x for x in itertools.product(all_permutations,
                                    filters[key])]

        all_like_dists = []
        for permutation in all_permutations:
            print permutation
            if type(permutation) == list or type(permutation) == tuple:
                permutation = flatten_tuple(permutation)
            else:
                permutation = [permutation]
            print permutation
            print "=========="
            kwargs = {}
            for idx, key in enumerate(filters):
                kwargs[key] = permutation[idx]

            print kwargs
            filtered_users = get_users(USERS, **kwargs)
            # print len(filtered_users)
            if len(filtered_users) > user_count_cutoff:
                lb_obj = LikeBreakdown(like_breakdown=like_breakdown(filtered_users),
                                       filters=permutation, count=len(filtered_users))
                all_like_dists.append(lb_obj)
        # print all_like_dists

        diffs = compute_diffs(all_like_dists)
        # print diffs

        if out_format == 'csv':
            print "generating csv..."
            return generate_csv(diffs, all_like_dists)
        return generate_report(diffs, all_like_dists)

    USER_COUNT_CUTOFF = 25

    filter_lst = [
        ['currentcity', ['Location10th.tsv', 'LocationIL.tsv', 'NOT::Location10th.tsv']],
        ['sex', ['m', 'f']],
        # ['age', ['15-24', '25-34', '35-44', '45-54', '55-64', '65-99']],
        # ['employer', ['Entry-Level.csv', 'Fortune_1000.csv', 'Intern.csv',
        #               'law.csv', 'Manager.csv', 'medicine.csv',
        #               'owner:founder.csv', 'public_servant.csv',
        #               'religious.csv', 'retired.csv', 'Senior_leadership.csv',
        #               'student.csv', 'technology.csv',
        #               'NOT::all_emp_Cats.csv']]
    ]

    for i in range(len(filter_lst)):
        print "Iteration %i of permutations." % i
        cur_filter_lst = filter_lst[i:] + filter_lst[:i]
        filters = {}

        csv_name = 'data/all_slices.csv'

        for idx, f in enumerate(cur_filter_lst):
            filters[f[0]] = f[1]
            report = main(filters, USER_COUNT_CUTOFF, out_format='csv')
            fname = str(filters.keys())
            with open(csv_name, 'a') as f:
                f.write(report)

        # for idx, f in enumerate(filter_lst):
        #     filters[f[0]] = f[1]
        #     report = main(filters, USER_COUNT_CUTOFF)
        #     fname = str(filters.keys())
        #     with open(fname,'w') as f:
        #         f.write(report)

            print "Generated level %i" % idx
    #main()
