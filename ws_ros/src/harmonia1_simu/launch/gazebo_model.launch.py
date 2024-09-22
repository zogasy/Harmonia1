
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
import xacro


def generate_launch_description():
    robotXacroname = 'sous_marin'

    #nom du package
    name_package = "harmonia1_simu"

    #chemin relatif 
    modelFileRelativePath = 'model/sous_marin.xacro'

    pathModelFile = os.path.join(get_package_share_directory(name_package),modelFileRelativePath)

    #recuperer la description du robot a partir du model xacro
    robotDescription = xacro.process_file(pathModelFile).toxml()

    gazebo_rosPackageLaunch = PythonLaunchDescriptionSource(os.path.join(get_package_share_directory('ros_gz_sim'),
                                                                         'launch','gz_sim.launch.py'))
    
    # pour utiler un world vide 
    gazeboLaunch = IncludeLaunchDescription(gazebo_rosPackageLaunch,  launch_arguments={'gz_args': '-r -v 4 empty.sdf', 'on_exit_shutdown': 'true'}.items()
)

    #gazebo node
    spawnModelNodeGazebo = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name',robotXacroname,
            '-topic','robot_description'
        ],
        output='screen'
    )

    #Robot State Publisher Node
    nodeRobotStatePublisher = Node(
        package= 'robot_state_publisher',
        executable= 'robot_state_publisher',
        output='screen',
        parameters=[{'robot_description':robotDescription,
                     'use_sim_time': True}]
    )
    
    #Tres tres important les parametre pour lancer le bridge
    bridge_params = os.path.join(get_package_share_directory(name_package),
                                 'parameters',
                                 'bridge_parameters.yaml')
    
    start_gazebo_ros_bridge_cmd = Node(
        package= 'ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={bridge_params}',
        ],
        output = 'screen',
    )
    # Empty launch description object
    lauchDescriptionObject = LaunchDescription()

    lauchDescriptionObject.add_action(gazeboLaunch)

    lauchDescriptionObject.add_action(spawnModelNodeGazebo)
    lauchDescriptionObject.add_action(nodeRobotStatePublisher)

    lauchDescriptionObject.add_action(start_gazebo_ros_bridge_cmd)
    return lauchDescriptionObject
