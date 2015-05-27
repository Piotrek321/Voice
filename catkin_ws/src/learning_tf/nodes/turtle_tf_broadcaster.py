#!/usr/bin/env python  
# -*- coding: utf-8 -*-
import roslib
roslib.load_manifest('learning_tf')
import rospy
import math
import tf
import geometry_msgs.msg
import turtlesim.srv
from std_msgs.msg import String


rozkaz =-1
l=0

def callback(data):
    rospy.loginfo("%s", data.data)
    r = data.data
    global rozkaz
    if r == "przód":
    	rozkaz = 1
    if r == "tył":
    	rozkaz = -1 
    #rozkaz = int(r)
    #rozkaz=konwertujLiczbe(r)
    print(rozkaz)
    #if r == "3":
    #	global l
    #	l=2


if __name__ == '__main__':
    rospy.init_node('listener', anonymous=True)

    listener = tf.TransformListener()



    turtle_vel = rospy.Publisher('turtle1/cmd_vel', geometry_msgs.msg.Twist,queue_size=1)

    rate = rospy.Rate(1.0)
    angular = 0
    linear = 0
    while not rospy.is_shutdown():
        rospy.Subscriber("chatter", String, callback)
        linear = rozkaz
        
        cmd = geometry_msgs.msg.Twist()
        cmd.linear.x = linear
        cmd.angular.z = angular
        turtle_vel.publish(cmd)

 
        rate.sleep()






