#!/usr/bin/env python
# license removed for brevity
import rospy
import pygame
import threading

from geometry_msgs.msg import Twist
import sys, select, termios, tty

L1 = 4
L2 = 6
R1 = 5
R2 = 7

speed = 0.2
turn = 0.5
speed_direction = 0
turn_direction = 0

max_speed = 1.5
max_turn = 1.0


def start_joystick_loop():
    pygame.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print joystick.get_name()

    axes = joystick.get_numaxes()
    print 'axes',axes

    buttons = joystick.get_numbuttons()
    print 'buttons',buttons

    hats = joystick.get_numhats()
    print 'hats', hats

    balls = joystick.get_numballs()
    print 'balls', balls

    for i in range(axes):
        axis = joystick.get_axis(i)

    for i in range(buttons) :
        button = joystick.get_button(i)

    for i in range(hats):
        hat = joystick.get_hat(i)

    for i in range(balls):
        ball = joystick.get_ball(i)

    while not rospy.is_shutdown():
        for event in pygame.event.get(): # User did something
            # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
            if event.type == pygame.JOYBUTTONDOWN:
                print "You pressed",event.button
                tune_speed(event.button)
            if event.type == pygame.JOYBUTTONUP:
                print "You released",event.button
            if event.type == pygame.JOYBALLMOTION:
                print "ball motion"
            if event.type == pygame.JOYAXISMOTION:
                print "axies motion",event.axis, event.value
            if event.type == pygame.JOYHATMOTION:
                print "hat motion",event.hat,event.value
                hat_move(event.value)
    pygame.quit ()

def tune_speed(button):
    global speed,turn
    #tune speed
    if button == L1:
        speed = speed + 0.1
    if button == L2:
        speed = speed - 0.1
    if button == R1:
        turn = turn + 0.1
    if button == R2:
        turn = turn - 0.1
    #limitation 
    if speed > max_speed:
        speed = max_speed
    if speed < 0:
        speed = 0
    if turn > max_turn:
        turn = max_turn
    if turn < 0:
        turn = 0

def hat_move(direction):
    global speed_direction,turn_direction
    speed_direction = direction[1]
    turn_direction = direction[0]

def publisher():
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=5)
    rate = rospy.Rate(10) # 10hz

    control_speed = 0
    control_turn = 0
    target_speed = 0
    target_turn = 0

    while not rospy.is_shutdown():

        target_speed = speed*speed_direction
        target_turn = turn*turn_direction

        if target_speed > control_speed:
            control_speed = min( target_speed, control_speed + 0.05 )
        elif target_speed < control_speed:
            control_speed = max( target_speed, control_speed - 0.05 )
        else:
            control_speed = target_speed

        if target_turn > control_turn:
            control_turn = min( target_turn, control_turn + 0.2 )
        elif target_turn < control_turn:
            control_turn = max( target_turn, control_turn - 0.2 )
        else:
            control_turn = target_turn


        twist = Twist()
        twist.linear.x = control_speed
        twist.angular.z = control_turn
        pub.publish(twist)
        rate.sleep()


if __name__ == '__main__':
    rospy.init_node('joystick', anonymous=False)
    
    t = threading.Thread(target=start_joystick_loop)
    t.daemon = True
    t.start()

    publisher()
    rospy.spin()

    