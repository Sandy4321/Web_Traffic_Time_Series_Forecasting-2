import numpy as np
import pandas as pd
import datetime
import copy
from fbprophet import Prophet


#Define prediction period strings for Phase 1
startDate = datetime.date(year=2017,month=1,day=1)
endDate= datetime.date(year=2017,month=3,day=1)
dateStrings=[]
while startDate <=endDate:
    dateStrings.append("_" + startDate.strftime("%Y-%m-%d"))
    startDate = startDate + datetime.timedelta(days=1)
nr_predictions=len(dateStrings)

#Create test DF for Phase 1
startDate = datetime.date(year=2017,month=1,day=1)
endDate= datetime.date(year=2017,month=3,day=1)
testDateArray=[]
while startDate <=endDate:
    testDateArray.append(copy.copy(startDate))
    startDate = startDate + datetime.timedelta(days=1)

test_date_df = pd.DataFrame(testDateArray, columns=["ds"],index=range(0,len(testDateArray)))

#Create train DF for Phase 1
startDate = datetime.date(year=2015,month=7,day=1)
endDate = datetime.date(year=2016,month=12,day=31)
trainDateArray=[]
while startDate <=endDate:
    trainDateArray.append(copy.copy(startDate))
    startDate = startDate + datetime.timedelta(days=1)

train_date_df = pd.DataFrame(trainDateArray, columns=["ds"],index=range(0,len(trainDateArray)))

#Eliminate Nan
train_df = pd.read_csv("../input/train_1.csv").fillna(0)

#We iterate over all series
pageArray = []
VisitsArray = []

limit_Prophet = 2000

for i in range(0,len(train_df.index)):

    entry = train_df.iloc[i]
    page = entry[0]

    if i < limit_Prophet:
        print(i)
        visits = pd.DataFrame(entry[1:].values,columns=["y"])

        X = visits.join(train_date_df)

        try:
            #Predict
            m = Prophet()
            m.fit(X)

            #Forecast
            forecast = m.predict(test_date_df)

            # For each series, we are going to write the predictions
            pageArray += [str(page + x) for x in dateStrings]
            VisitsArray += forecast['yhat'].values.tolist()

        except:
            visits = entry[-68:-8].median()
            pageArray += [str(page+x) for x in dateStrings]
            VisitsArray += ([visits] * nr_predictions)

    else:
        visits = entry[-68:-8].median()
        pageArray += [str(page + x) for x in dateStrings]
        VisitsArray += ([visits] * nr_predictions)


result_df= pd.DataFrame(data={"Page":pageArray,"Visits":VisitsArray},columns=["Page","Visits"])

key_df = pd.read_csv("../input/key_1.csv")

submission_df = pd.merge(key_df, result_df, on='Page')

submission_df.to_csv(path_or_buf="../output/fbProphet_first2000TS_with_8missing_submission.csv",columns=["Id","Visits"],index=False)