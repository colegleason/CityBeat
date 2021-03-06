import os
from rq import Queue, Connection
from do_gp import Predict 
from redis import Redis
import time
from random import randrange
from data_process import find_photos_given_region
from twitter_data_process import find_tweets_given_region
from datetime import timedelta
from datetime import datetime
import pymongo
import calendar 

def read_regions():
    f = open('number.csv','r')
    res = []
    for line in f.readlines():
        t = line.split(',')
        res.append((t[0], t[1]))
    res.reverse()
    return res
    #return res[1:3]

def process_ts(ts):
    """return two results; the first is the start datetime, the second is the list of training data"""
    idx = ts.index
    start = idx[0]
    res = []
    for t in idx:
        days_diff = (t-start).days + (t-start).seconds/(24*3600.0);
        res.append((days_diff, ts[t]))
    return start, res

def get_testing(model_update_time, start_time, predict_days):
    res = []
    align = []
    for i in range(24*predict_days):
        delta = model_update_time + timedelta(seconds=3600*(i+1)) - start_time
        secs = delta.seconds+delta.days*86400
        res.append( secs/(3600.0 * 24) )
        align.append( model_update_time + timedelta(seconds=3600*(i+1)))
    return res,align

def save_to_mongo(result, region, model_update_time, data_source):
    mongo = pymongo.Connection("grande",27017)
    print 'in save'
    if data_source=='twitter':
        db_name = 'twitter_predict'
    else:
        db_name = 'predict'
    mongo_db = mongo['predict']
    mongo_collection = mongo_db.prediction
    for r in result:
        t = {'time':r[0], 'mu':float(r[1]), 'var':float(r[2]), 'mid_lat':str(region[0]), 'mid_lng':str(region[1]), 'model_update_time':model_update_time}
        mongo_collection.insert(t)

def do_align(align, result):
    res = []
    for a,r in zip(align,result):
        res.append( (a,r[1],r[2])) 
    return res

def main():
    data_source = 'instagram'
    #data_source = 'twitter'
    predict_days = 1
    regions = read_regions()
    redis_conn = Redis('tall4')
    q = Queue(connection=redis_conn)
    cnt = 0
    async_results = {}
    model_update_time = datetime.utcnow()
    
    for region in regions:
        par = cnt
        if data_source=='twitter':
            pass
            try:
                print region
                ts, tweets = find_tweets_given_region(region[0], region[1], '1h','tweets',True)
            except Exception as e:
                print e
                continue
        elif data_source =='instagram':
            try:
                ts, photos = find_photos_given_region(region[0], region[1], '1h','citybeat',True)
            except Exception as e:
                print e
                continue
        start, training = process_ts(ts)
        testing, align= get_testing(model_update_time, start, predict_days)
        print 'start is ',start
        print 'model_update_time is ',model_update_time
        print 'testing is ',testing
        async_results[cnt] = q.enqueue_call( Predict, args = ( training,testing, cnt,), timeout=1720000, result_ttl=-1 )
        cnt+=1
    done = False
    begin_time = time.time()
    time.sleep(2)
    saved_flag = [0]*len(async_results)
    while not done:
        print "Time elapsed : ",time.time()-begin_time
        done = True
        for x in range(cnt):
            result = async_results[x].return_value
            if result is None:
                done = False
                continue
            if saved_flag[x] == 0:
                result = do_align(align, result)
                if data_source=='twitter':
                    save_to_mongo(result, regions[x], model_update_time, "twitter")
                elif data_source=='instagram':
                    print 'work here'
                    save_to_mongo(result, regions[x], model_update_time, "instagram")
                saved_flag[x] = 1
        time.sleep(20)

main() 
