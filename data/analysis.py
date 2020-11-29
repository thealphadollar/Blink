from datetime import time
import pandas
from pandas.core.algorithms import diff
from scipy.stats import chi2_contingency, ttest_ind

data = pandas.read_csv('script_data.csv')

def different_categories():
    category_count = {}
    untracked_count = {}
    click = 0
    non_click = 0
    both = 0
    # print(data.head())
    for row in data.values:
        # print(row)
        if row[1] == True or row[2] == True:
            category_count[row[3]] = category_count.get(row[3], 0) + 1
        else:
            untracked_count[row[3]] = untracked_count.get(row[3], 0) + 1
        
        if row[1] == True and row[2] == True:
            both += 1
        elif row[2] == True:
            click += 1
        elif row[1] == True:
            non_click += 1
    
    print(category_count)
    print(untracked_count)
    print(non_click, click, both)
    
def chi2():
    category_count = {}
    untracked_count = {}
    click = 0
    non_click = 0
    both = 0
    # print(data.head())
    for row in data.values:
        # print(row)
        if row[1] == True or row[2] == True:
            category_count[row[3]] = category_count.get(row[3], 0) + 1
        else:
            untracked_count[row[3]] = untracked_count.get(row[3], 0) + 1
    category_count["SOCIAL"] = 0
    dataF = pandas.DataFrame([
        [3.47, 13.58],
        [96.53, 86.42]
    ],
    index=["Tracked", "Non-Tracked"],
    columns=["Personal", "Not-Personal"])
    
    print(dataF.head())
    
    print(chi2_contingency(dataF))
    
def corr():
    main_dict = {}
    for row in data.values:
        main_dict[row[13]] = main_dict.get(row[13], {
        "tracked": 0,
        "nontracked": 0,
        "avg.time": 0,
        "num": 0,
        "send_tracked": 0,
        "total_num": 0
    })
        if row[1] == True or row[2] == True:
            main_dict[row[13]]["tracked"] += 1
        else:
            main_dict[row[13]]["nontracked"] += 1
        main_dict[row[13]]["send_tracked"] = row[14]
        avg_time = (row[12] + row[11]) / 2
        if avg_time != 0:
            main_dict[row[13]]["num"] += 1
            main_dict[row[13]]["avg.time"] = (main_dict[row[13]]["avg.time"] + avg_time) / main_dict[row[13]]["num"]
        main_dict[row[13]]["total_num"] += 1
        
    for key in main_dict.keys():
        main_dict[key]["tracked"] = (main_dict[key]["tracked"] / main_dict[key]["total_num"]) * 100
        main_dict[key]["nontracked"] = (main_dict[key]["nontracked"] / main_dict[key]["total_num"]) * 100
        
    dataF = pandas.DataFrame([
        main_dict[x].values() for x in main_dict.keys()
    ],
    index=main_dict.keys(),
    columns=main_dict["e6ca72cddd77e2dfc9ef1d47ed743edb"].keys())        
    print(dataF)
    print("Correlation b/w tracked emails and avg. response time: ", dataF["tracked"].corr(dataF["avg.time"]))
    print("Correlation b/w non tracked emails and avg. response time: ", dataF["nontracked"].corr(dataF["avg.time"]))
    print("Correlation b/w tracked emails and if the user sends emails with tracking: ", dataF["tracked"].corr(dataF["send_tracked"]))
    print("Correlation b/w non tracked emails and if the user sends emails with tracking: ", dataF["nontracked"].corr(dataF["send_tracked"]))
    print("Correlation b/w tracked emails and number of emails sent: ", dataF["tracked"].corr(dataF["num"]))
    print("Correlation b/w non tracked emails and number of emails sent: ", dataF["nontracked"].corr(dataF["num"]))
    
    by_tracker_user = dataF[dataF["send_tracked"] == 1]
    by_non_tracker_user = dataF[dataF["send_tracked"] == 0]
    print("T-test result between tracked and if user sends tracking emails", ttest_ind(by_tracker_user["tracked"], by_non_tracker_user["tracked"]))
    print("T-test result between non_tracked and if user sends tracking emails", ttest_ind(by_tracker_user["nontracked"], by_non_tracker_user["nontracked"]))
    
def time_distribution():
    date_wise = [0 for x in range(32)]
    day_wise = {}
    time_quadrant = [0 for x in range(5)]
    for row in data.values:
        if row[1] == True or row[2] == True:
            date_wise[row[8]] += 1
            time_quadrant[row[4]] += 1
            day_wise[row[7]] = day_wise.get(row[7], 0) + 1

    print(date_wise)
    print(day_wise)
    print(time_quadrant)    
        

# different_categories()
# chi2()
# corr()
time_distribution()