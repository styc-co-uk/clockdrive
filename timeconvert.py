# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# % This subroutine converts current minute    %
# % to the minute since 12 am/pm UTC           %
# % this is used as the standartised timescale %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def minsFrom12(hour,minute):
    return (hour%12)*60+minute
