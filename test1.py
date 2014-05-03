from __future__ import division
from app.tasks import scrape
process_list = (scrape.get_users.s() | scrape.dmap.s(scrape.get_about.s()))
res = process_list()
pickle.dump( res.get(), open('res.p', 'wb') )

# res = pickle.load( open( "res.p", "rb" ) )

is_user_public_list = map(lambda task: task.result[1] if task.status == "SUCCESS" else False, res.get())
results = map(lambda task: task.result[0] if task.status == "SUCCESS" and task.result[1] == True else None, res.get())
results = filter(lambda x: x, results)
print sum(is_user_public_list)/len(is_user_public_list)