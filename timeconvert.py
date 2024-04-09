# this convert time to minute from no.12 o'clock
def minsFrom12(hour,minute):
    if hour>=12: return (hour-12)*60+minute
    else: return hour*60+minute