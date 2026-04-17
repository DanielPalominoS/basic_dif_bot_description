from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg_name = 'basic_dif_bot_description'
    pkg_share = get_package_share_directory(pkg_name)

    # Argumento opcional para RViz config
    rviz_config_arg = DeclareLaunchArgument(
        name='rvizconfig',
        default_value=PathJoinSubstitution([pkg_share, 'config', 'view_robot.rviz']),
        description='Ruta al archivo de configuración de RViz'
    )

    # Ruta al Xacro principal (robot físico + sensores)
    robot_xacro = PathJoinSubstitution([
        pkg_share,
        'urdf',
        'robot.urdf.xacro'
    ])

    # Expandir Xacro → robot_description
    robot_description = Command([
        'xacro ', robot_xacro
    ])

    # Nodo robot_state_publisher
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description
        }]
    )

    # Nodo joint_state_publisher_gui (útil para depurar articulaciones)
    jsp_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    # Nodo RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')]
    )

    return LaunchDescription([
        rviz_config_arg,
        rsp_node,
        jsp_gui_node,
        rviz_node
    ])
