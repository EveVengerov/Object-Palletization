import ikpy.chain
import ikpy.utils.plot as plot_utils

import numpy as np
import time
import math

import ipywidgets as widgets

my_chain = ikpy.chain.Chain.from_urdf_file("../Resources/arm.urdf", active_links_mask=[False, True, True, True, True, True])

# target_position = [ 0.0, 0.0,0.5]
# station1
# target_position = [0.05,  0.130,  0.02+0.2+0.05 ]

# target 1
# target_position = [-0.075,  0.170,  0.02+0.2      ]

# target 2
# target_position =    [-0.01476016,  0.25549,     0.02 +0.25    ]






def doIK(target_position):
    # old_position = ik.copy()
    target_orientation = [0.1, 0.1, -1]
    ik = my_chain.inverse_kinematics(target_position, target_orientation, orientation_mode="Y")
    print("The angles of each joints are : ", list(map(lambda r: math.degrees(r), ik.tolist())))
    computed_position = my_chain.forward_kinematics(ik)
    print("Computed position: %s, original position : %s" % (computed_position[:3, 3], target_position))
    print("Computed position (readable) : %s" % ['%.2f' % elem for elem in computed_position[:3, 3]])

    return ik


if __name__ == '__main__':
    target_position = [0.05, 0.130, 0.02 + 0.2 + 0.05]
    target_orientation = [0.1, 0.1, -1]
    doIK(target_position)

    # %matplotlib widget
    ik = my_chain.inverse_kinematics(target_position, target_orientation, orientation_mode="Y")
    import matplotlib.pyplot as plt

    fig, ax = plot_utils.init_3d_figure()
    fig.set_figheight(9)
    fig.set_figwidth(13)
    my_chain.plot(ik, ax, target=target_position)
    plt.xlim(-0.5, 0.5)
    plt.ylim(-0.5, 0.5)
    ax.set_zlim(0, 0.6)
    plt.show()



#
#
# def updatePlot():
#     ax.clear()
#     my_chain.plot(ik, ax, target=target_position)
#     plt.xlim(-0.5, 0.5)
#     plt.ylim(-0.5, 0.5)
#     ax.set_zlim(0, 0.6)
#     fig.canvas.draw()
#     fig.canvas.flush_events()
#
#
# def move(x, y, z):
#     global target_position
#     target_position = [x, y, z]
#     doIK()
#     updatePlot()

# import DriveRobot as dr







# print("joint angles: %s "% ik)
#     # sendCommand(ik[1].item(), ik[2].item(), ik[3].item(), ik[4].item(), ik[5].item(), ik[6].item(), 1)
#
#     # move(0, 0.02, 0.10)