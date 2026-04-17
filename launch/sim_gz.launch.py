from os.path import join
import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.substitutions import LaunchConfiguration, Command
from launch.launch_description_sources import PythonLaunchDescriptionSource

from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node


def generate_launch_description():

    pkg_name = 'basic_dif_bot_description'
    pkg_share = get_package_share_directory(pkg_name)

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    world_file = LaunchConfiguration(
        'world',
        default=join(pkg_share, 'worlds', 'my_world.sdf')
    )

    # Recursos para GZ
    gz_resource_path = [
        join(pkg_share, 'worlds'),
        join(pkg_share, 'models')
    ]
    os.environ['GZ_SIM_RESOURCE_PATH'] = ':'.join(gz_resource_path)

    # Xacro del robot para GZ
    robot_xacro = join(pkg_share, 'urdf', 'robot_gz.urdf.xacro')

    robot_description = Command([
        'xacro ', robot_xacro
    ])

    # robot_state_publisher
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_description
        }]
    )

    # Lanzar Gazebo (Ignition/GZ)
    gz_sim_share = get_package_share_directory('ros_gz_sim')
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            join(gz_sim_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': world_file
        }.items()
    )

    # Crear el robot en GZ
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_dif_bot',
        output='screen',
        arguments=[
            '-topic', '/robot_description',
            '-name', 'dif_bot',
            '-allow_renaming', 'true',
            '-z', '0.2'
        ]
    )

    # Esperar 3 segundos antes de spawnear
    spawn_after_gz = TimerAction(
        period=3.0,
        actions=[spawn_entity]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time'
        ),
        DeclareLaunchArgument(
            'world',
            default_value=world_file,
            description='World SDF file'
        ),
        gz_sim,
        rsp_node,
        spawn_after_gz,
    ])
