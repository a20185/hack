from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
from queue import Queue
from PIL import Image
from io import BytesIO

import ctypes
import _ctypes
import pygame
import sys
import requests
import os
import json
import numpy
import math

import threading

# colors for drawing different bodies
SKELETON_COLORS = [pygame.color.THECOLORS["red"],
                   pygame.color.THECOLORS["blue"],
                   pygame.color.THECOLORS["green"],
                   pygame.color.THECOLORS["orange"],
                   pygame.color.THECOLORS["purple"],
                   pygame.color.THECOLORS["yellow"],
                   pygame.color.THECOLORS["violet"]]

class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def __sub__(self, rhs):
        return Point(self.x - rhs.x, self.y - rhs.y)


def angle(vec_a, vec_b):
    a = numpy.complex(vec_a.x, vec_a.y)
    b = numpy.complex(vec_b.x, vec_b.y)
    c = b / a
    return math.atan2(c.imag, c.real)

now_cnt = 0


# pose1: 两手平直
# pose2: 左手抬起
# pose3: 右手抬起
# pose4: 两手放下
# pose5: 两手抬起

def get_angles(shoulder_center, shoulder_left, shoulder_right, hand_left, hand_right):
    angles = []
    vec1 = shoulder_center - shoulder_left
    vec2 = hand_left - shoulder_left
    angles.append(angle(vec1, vec2))

    vec1 = shoulder_center - shoulder_right
    vec2 = hand_right - shoulder_right
    angles.append(angle(vec1, vec2))
    res = []
    res.append(angles[1])
    res.append(angles[0])
    return res


def check_pose1(shoulder_center, shoulder_left, shoulder_right, hand_left, hand_right):
    angles = get_angles(shoulder_center, shoulder_left, shoulder_right, hand_left, hand_right)
    #if angles[0] > -math.pi * 0.8:
    #    return False
    #if angles[1] < math.pi * 0.8:
    #    return False
    #return True
    if angles[0] < -1.6 and angles[1] > 1.6:
        return True
    return False


def check_pose2(shoulder_center, shoulder_left, shoulder_right, hand_left, hand_right):
    angles = get_angles(shoulder_center, shoulder_left, shoulder_right, hand_left, hand_right)
    if angles[0] < -0.2 and angles[1] < -2.4:
        return True
    #if angles[0] < -math.pi * 0.65:
    #    return False
    #if angles[1] < math.pi * 0.8:
    #    return False
    #return True
    return False


def check_pose3(shoulder_center, shoulder_left, shoulder_right, hand_left, hand_right):
    angles = get_angles(shoulder_center, shoulder_left, shoulder_right, hand_left, hand_right)
    if angles[0] > 2.4 and angles[1] > 0.2:
        return True
    #if angles[0] > -math.pi * 0.8:
    #    return False
    #if angles[1] > math.pi * 0.65:
    #    return False
    #return True
    return False


def check_pose4(shoulder_center, shoulder_left, shoulder_right, hand_left, hand_right):
    angles = get_angles(shoulder_center, shoulder_left, shoulder_right, hand_left, hand_right)
    #if angles[0] > -math.pi * 1.35:
    #    return False
    #if angles[1] < math.pi * 1.35:
    #    return False
    #return True
    if angles[0] < -0.25 and angles[1] > 0.70:
        return True
    return False


def check_pose5(shoulder_center, shoulder_left, shoulder_right, hand_left, hand_right):
    angles = get_angles(shoulder_center, shoulder_left, shoulder_right, hand_left, hand_right)
    #if angles[0] < -math.pi * 0.65:
    #    return False
    #if angles[1] > math.pi * 0.65:
    #    return False
    #return True
    if angles[0] > 2.6 and angles[1] < -2.6:
        return True
    return False


def get_pose(shoulder_center, shoulder_left, shoulder_right, hand_left, hand_right):
    check_func = [check_pose1, check_pose2, check_pose3, check_pose4, check_pose5]
    for idx, check in enumerate(check_func):
        if check(shoulder_center, shoulder_left, shoulder_right, hand_left, hand_right):
            return idx + 1
    return 0


class BodyGameRuntime(object):
    def __init__(self):
        pygame.init()

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()

        # Set the width and height of the screen [width, height]
        self._infoObject = pygame.display.Info()
        self._screen = pygame.display.set_mode((self._infoObject.current_w, self._infoObject.current_h),
                                               pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE, 32)

        pygame.display.set_caption("Kinect for Windows v2 Body Game")

        # Loop until the user clicks the close button.
        self._done = False

        # Used to manage how fast the screen updates
        self._clock = pygame.time.Clock()

        # Kinect runtime object, we want only color and body frames
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)

        # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
        self._frame_surface = pygame.Surface((self._kinect.color_frame_desc.Width, self._kinect.color_frame_desc.Height), 0, 32)

        # here we will store skeleton data
        self._bodies = None

        self._img_queue = Queue(maxsize=5)
    
    def _update_text(self):
        while True:
            buf, fname = self._img_queue.get()
            pygame.image.save(buf, fname)
            url = 'http://10.221.64.253:5000/reco'
            with open(fname, 'rb') as f:
                files = { 'file': f }
                res = requests.post(url, files=files)
            os.remove(fname)
            result = json.loads(res.text)
            print(result)

    def get_screen_size(self):
        width = self._kinect.color_frame_desc.Width
        height = self._kinect.color_frame_desc.Height
        return width / 2, height / 2
    
    def draw_body_bone(self, joints, jointPoints, color, joint0, joint1):
        joint0State = joints[joint0].TrackingState
        joint1State = joints[joint1].TrackingState

        # both joints are not tracked
        if (joint0State == PyKinectV2.TrackingState_NotTracked) or (joint1State == PyKinectV2.TrackingState_NotTracked):
            return

        # both joints are not *really* tracked
        if (joint0State == PyKinectV2.TrackingState_Inferred) and (joint1State == PyKinectV2.TrackingState_Inferred):
            return

        # ok, at least one is good
        start = (jointPoints[joint0].x, jointPoints[joint0].y)
        end = (jointPoints[joint1].x, jointPoints[joint1].y)

        try:
            pygame.draw.line(self._frame_surface, color, start, end, 8)
        except:  # need to catch it due to possible invalid positions (with inf)
            pass

    def draw_rect(self, color):
        try:
            width = self._kinect.color_frame_desc.Width
            height = self._kinect.color_frame_desc.Height
            rect = pygame.Rect(width / 4, height / 4, width / 2, height / 2)
            pygame.draw.rect(self._frame_surface, color, rect, 3)
        except:
            pass

    def draw_body(self, joints, jointPoints, color):
        # Torso
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft)

        # Right Arm
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_HandRight)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandRight, PyKinectV2.JointType_HandTipRight)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristRight, PyKinectV2.JointType_ThumbRight)

        # Left Arm
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_HandLeft)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HandLeft, PyKinectV2.JointType_HandTipLeft)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_WristLeft, PyKinectV2.JointType_ThumbLeft)

        # Right Leg
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleRight, PyKinectV2.JointType_FootRight)

        # Left Leg
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft)
        self.draw_body_bone(joints, jointPoints, color, PyKinectV2.JointType_AnkleLeft, PyKinectV2.JointType_FootLeft)

        tmp = jointPoints[PyKinectV2.JointType_SpineBase]
        shoulder_center = Point(tmp.x, tmp.y)
        tmp = jointPoints[PyKinectV2.JointType_ShoulderLeft]
        shoulder_left = Point(tmp.x, tmp.y)
        tmp = jointPoints[PyKinectV2.JointType_ShoulderRight]
        shoulder_right = Point(tmp.x, tmp.y)
        tmp = jointPoints[PyKinectV2.JointType_HandLeft]
        hand_left = Point(tmp.x, tmp.y)
        tmp = jointPoints[PyKinectV2.JointType_HandRight]
        hand_right= Point(tmp.x, tmp.y)
        angles = get_angles(shoulder_center, shoulder_left, shoulder_right, hand_left, hand_right)
        # print("Pose %d, %f, %f" % (get_pose(shoulder_center, shoulder_left, shoulder_right, hand_left, hand_right), 
        #      angles[0], angles[1]))

    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        address = self._kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()

    def save_capture(self, filename):
        sub_screen = self.get_capture()
        pygame.image.save(sub_screen, filename)
    
    def get_capture(self):
        width = self._kinect.color_frame_desc.Width
        height = self._kinect.color_frame_desc.Height
        rect = pygame.Rect(width / 4, height / 4, width / 2, height / 2)
        sub_screen = self._screen.subsurface(rect)
        return sub_screen

    def run(self):
        # -------- Main Program Loop -----------
        cnt = 0
        update_text = threading.Thread(target=self._update_text)
        update_text.start()

        while not self._done:
            # --- Main event loop
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    self._done = True  # Flag that we are done so we exit this loop

                elif event.type == pygame.VIDEORESIZE:  # window resized
                    self._screen = pygame.display.set_mode(event.dict['size'],
                                                           pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE, 32)
                elif event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    print('Press key:', keys)
                    if keys[pygame.K_p]:
                        print('Press p')
                        self.save_capture('screen.jpg')

            # --- Game logic should go here

            # --- Getting frames and drawing
            # --- Woohoo! We've got a color frame! Let's fill out back buffer surface with frame's data
            if self._kinect.has_new_color_frame():
                frame = self._kinect.get_last_color_frame()
                self.draw_color_frame(frame, self._frame_surface)
                frame = None

            # --- Cool! We have a body frame, so can get skeletons
            if self._kinect.has_new_body_frame():
                self._bodies = self._kinect.get_last_body_frame()

            # --- Draw rectangle
            self.draw_rect(SKELETON_COLORS[0])

            try:
                sub_screen = self.get_capture()
                cnt += 1
                filename = 'screen%d.jpg' % cnt
                self._img_queue.put((sub_screen, filename), block=False)
            except:
                pass

            #url = 'http://10.221.64.253:5000/reco'
            #files = {'file': open('screen%d.jpg' % cnt, 'rb')}
            #res = requests.post(url, files=files)
            #print(res.text)

            # --- draw skeletons to _frame_surface
            if self._bodies is not None:
                for i in range(0, self._kinect.max_body_count):
                    body = self._bodies.bodies[i]
                    if not body.is_tracked:
                        continue

                    joints = body.joints
                    # convert joint coordinates to color space
                    joint_points = self._kinect.body_joints_to_color_space(joints)
                    self.draw_body(joints, joint_points, SKELETON_COLORS[i])

            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size)
            h_to_w = float(self._frame_surface.get_height()) / self._frame_surface.get_width()
            target_height = int(h_to_w * self._screen.get_width())
            surface_to_draw = pygame.transform.scale(self._frame_surface, (self._screen.get_width(), target_height))
            self._screen.blit(surface_to_draw, (0, 0))
            surface_to_draw = None

            pygame.display.update()

            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # --- Limit to 60 frames per second
            self._clock.tick(30)

        # Close our Kinect sensor, close the window and quit.
        self._kinect.close()
        pygame.quit()


__main__ = "Kinect v2 Body Game"
game = BodyGameRuntime()
game.run()
