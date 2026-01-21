



#from launch import LaunchDescription
from launch_ros.actions import Node
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution
#from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

#https://robotics.stackexchange.com/questions/89429/ros2-include-a-launch-file-from-a-launch-file
'''
def generate_launch_description():
    """Launch the example.launch.py launch file."""
    return LaunchDescription([
        launch.actions.DeclareLaunchArgument(
            'test',
            default_value='different_default_value',
            description='test arg that overlaps arg in included file',
            ),
        LogInfo(msg=[
            'Including launch file located at: ', ThisLaunchFileDir(), '/example.launch.py'
        ]),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([ThisLaunchFileDir(), '/example.launch.py']),
            launch_arguments={'node_name': 'bar'}.items(),
        ),
    ])
'''

#https://docs.ros.org/en/rolling/Tutorials/Intermediate/Launch/Using-ROS2-Launch-For-Large-Projects.html#writing-launch-files
#https://docs.ros.org/en/galactic/Tutorials/Intermediate/Launch/Using-Substitutions.html
#https://docs.ros.org/en/foxy/Tutorials/Intermediate/Launch/Creating-Launch-Files.html
def generate_launch_description():
    #print( get_package_share_directory("ardupilot_gz_bringup"))
    #launch_dir = ThisLaunchFileDir()#PathJoinSubstitution([FindPackageShare('launch_tutorial'), 'launch'])
    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                #PathJoinSubstitution([FindPackageShare('ardupilot_gz'), 'iris_runway.launch.py'])
                PathJoinSubstitution([
                    get_package_share_directory("ardupilot_gz_bringup"), 'launch', 'iris_runway.launch.py'
                ])
            ]),
        ),
        Node( # works, starts the node
            package='suas_cv',
            executable='suas_cv_imageSubscriber',
            name='image_subscriber',
        ),
    ])


#works, must do  source install/setup.bash  first after building and before running
'''
def generate_launch_description():
    return LaunchDescription([
        Node(
            package='demo_nodes_cpp',
            executable='talker',
            name='talker_node',
        )
    ])
'''

