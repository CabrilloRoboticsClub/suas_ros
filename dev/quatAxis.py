#!/usr/bin/env python3

import math

from scipy.spatial.transform import Rotation
#import scipy.spatial.transform


#https://gist.github.com/salmagro/2e698ad4fbf9dae40244769c5ab74434
#https://robotics.stackexchange.com/questions/96357/ros2-python-quaternion-to-euler
#https://automaticaddison.com/how-to-convert-a-quaternion-into-euler-angles-in-python/
def euler_from_quaternion(x, y, z, w):
    # might want to put this into a seperate node to take in imu orientation data and output heading
    # can comment out the code for roll and pitch since I will only be using yaw
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
     
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
     
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
     
        return roll_x, pitch_y, yaw_z # in radians




def main(args=None):
    w =  0.043#0.062
    qx = 0.310#-0.003
    qy = 0.895#-0.947
    qz = -0.319#0.316

    #https://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToAngle/index.htm#:~:text=Equations.%20angle%20=%202%20*%20acos(qw)%20x,/%20sqrt(1%2Dqw*qw)%20z%20=%20qz%20/%20sqrt(1%2Dqw*qw)
    angle = 2 * math.acos(w)
    s = math.sqrt(1 - w * w)
    if s < 0.001:
        x = qx
        y = qy
        z = qz
    else:
        x = qx / s
        y = qy / s
        z = qz / s

    print(f"{w, qx, qy, qz} -> {x,y,z}, {math.degrees(angle)}")
    angle = math.degrees(angle)
    # ^ Axis angles are correct


    #https://stackoverflow.com/questions/56207448/efficient-quaternions-to-euler-transformation
    #quat_df = [w, qx, qy, qz]

    #rot = Rotation.from_quat(quat_df)
    #rot_euler = rot.as_euler('xyz', degrees=True)
    #euler_df = pd.DataFrame(data=rot_euler, columns=['x', 'y', 'z'])

    quat = [qx, qy, qz, w]
    r = Rotation.from_quat(quat)
    euler_angles = r.as_euler('xyz', degrees=True)
    # ^ euler angles are slightly incorrect:
    # outputs -142.94388683   -6.63086072  177.41251651
    #   when it should output 142.9781339  -6.849525  178.0673127

    print(euler_angles)


    #https://www.euclideanspace.com/maths/geometry/rotations/conversions/angleToEuler/index.htm
    #heading = math.atan2(y*math.sin(angle) - x * z * (1 - math.cos(angle)), 1 - (y * y - z * z) * (1 - math.cos(angle)))
    #print(heading)

    test = math.atan2(2*(qx*qy + w*qz), w*w + qx*qx - qy*qy - qz*qz) # around z axis
    print(math.degrees(test)) # same as scipy result to 6 decimal places


    (roll, pitch, yaw) = euler_from_quaternion(qx, qy, qz, w)
    print(math.degrees(roll), math.degrees(pitch), math.degrees(yaw)) # same as above and scipy result to 1 decimal place
    # all results are very different than online sandbox for [w, x, y, z] quaternions of [0.043, 0.310, 0.895, -0.319]
    

    #https://quaternion.readthedocs.io/en/latest/

if __name__ == '__main__':
    main()
