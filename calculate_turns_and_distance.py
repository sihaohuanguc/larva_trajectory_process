#!/usr/bin/env python
# -*- coding: utf-8

import os,math,sys
import pandas as pd
import numpy as np

__author__ = "Sihao Huang"
__copyright__ = ""
__credits__ = []
__license__ = "GPL 2.0"
__version__ = "1.1"
__maintainer__ = "Sihao Huang"
__email__ = "sihaohuang1024@gmail.com"
__status__ = "Development"

def main():
    indir=sys.argv[1] # input folder
    out_file=sys.argv[2]  # output file
 
    out_list=[]
    for item in os.listdir(indir):
        df=pd.read_csv(indir+"/"+item,index_col=0)

        # preprocess, the frame edge is 0 and 1000 on both x and y axis, so we could cut those points on the edge
        upbound=950
        lowbound=50
        df=df[(df["X-Midpoint"]>lowbound)&(df["X-Midpoint"]<upbound)&(df["Y-Midpoint"]>lowbound)&(df["Y-Midpoint"]<upbound)]
    
        # take data points from the curves
        sampling_interval=50    # keep one point in every 50 points
        x_list=df["X-Midpoint"].to_list()[::sampling_interval] 
        y_list=df["Y-Midpoint"].to_list()[::sampling_interval]

        # calculate the speed
        time_total=df["Time"].max()-df["Time"].min() 
        distance_total=0
        for i in range(1,len(x_list)):
            distance_total+=math.sqrt((y_list[i]-y_list[i-1])**2+(x_list[i]-x_list[i-1])**2)
        out_line=[item.split('.')[0],time_total,distance_total/time_total]  # speed

        # remove the points overlapping with the last one
        df2=pd.DataFrame({"x":x_list,"y":y_list})
        df2["overlap"]=(df2==df2.shift(1)).all(axis=1)  # if one point is the same as the one above, it will have a True
        df2=df2[~df2["overlap"]]
        x_list=df2["x"].to_list()
        y_list=df2["y"].to_list()
        
        # calculate turning frequency
        # set parameters
        turn_banning_times=0  # so when there is a turn in the last x points, it will not be viewed as a turn
        angle_size=1  # how far will the edge of the angle be, 1 means the corner will be connected with its +1 and -1 points
        edge_length_threshold=2  # the both edge length need to be larger than this value to be considered to judge whether it's a turn
        forward_angle=45  # > this angle to be called as a turn from forward
        back_angle=190   # < this angle to be called as a turn from back # when it's > 180 then it means there is no limitation

        turn_index=0
        count_turns=0

        for i in range(angle_size,len(x_list)-angle_size):
            # calculate the angle and length of the two vectors
            length1=np.linalg.norm(np.array([x_list[i],y_list[i]])-np.array([x_list[i-angle_size],y_list[i-angle_size]]))
            length2=np.linalg.norm(np.array([x_list[i+angle_size],y_list[i+angle_size]])-np.array([x_list[i],y_list[i]]))
            angle=math.degrees(math.atan2(y_list[i+angle_size]-y_list[i],x_list[i+angle_size]-x_list[i])-math.atan2(y_list[i]-y_list[i-angle_size],x_list[i]-x_list[i-angle_size]))
            while angle < -180:
                angle+=360
            while angle > 180:
                angle-=360

            # record the turns
            if ((angle>forward_angle and angle<back_angle) or (angle< -forward_angle and angle>-back_angle)) and turn_index==0 and length1>=edge_length_threshold and length2>= edge_length_threshold: # this is viewed as a turn
                count_turns+=1
                turn_index+=turn_banning_times  # now any turn in the following x points will not be a turn
            else:
                if turn_index>0: # there is a turn before it and within x points
                    turn_index-=1
        
        out_line.append(count_turns/time_total)  # turns, normalized by time, as different samples have different time scale
        out_list.append(out_line)

    out_df=pd.DataFrame(out_list)
    out_df.columns=["sample","time","speed","normalized_turns"]
    # out_df.sort_values(by="sample",inplace=True)
    out_df.to_csv(out_file,index=False)


if __name__ == "__main__" :
    main()


