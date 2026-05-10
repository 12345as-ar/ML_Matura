import sqlite3


def check_complete(db:str) -> dict[int,int]:
    con = sqlite3.connect(db)
    cur = con.cursor()
    hours = {}
    current_time = 0
    cur.execute('SELECT timestamp FROM prices WHERE item_id IS 1')
    timestamps = cur.fetchall()
    last_time = int(timestamps[0][0]/1000)
    for index, timestamp in enumerate(timestamps, start=1):
        time = int(timestamp[0]/1000)
        print(time)
        gap = time - last_time
        if 0 <= gap <= 120:
            current_time += gap
        else:
            total_hours = round(current_time/3600)
            if total_hours in hours.keys():
                hours[total_hours] += 1
            else:
                hours[total_hours] = 1
        last_time = time
    return hours

        


if __name__ == "__main__":
    sorted_result = dict(sorted(check_complete("../skyblock/bazaar_collector_py/bazaar.db").items(), key=lambda item: item[1], reverse=True))
    for key in sorted_result.keys():
        print(key, sorted_result[key])
    
    
