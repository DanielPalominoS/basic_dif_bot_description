from os.path import join

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg = get_package_share_directory('basic_dif_bot_description')

    # -------------------------------
    # Launch arguments
    # -------------------------------
    use_ros2_control = LaunchConfiguration('use_ros2_control')
    world = LaunchConfiguration('world')

    # -------------------------------
    # Robot description
    # -------------------------------
    robot_description = Command([
        'xacro ',
        join(pkg, 'urdf', 'robot_gz.urdf.xacro'),
        ' use_ros2_control:=', use_ros2_control
    ])

    # -------------------------------
    # Nodes
    # -------------------------------

    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': ParameterValue(robot_description, value_type=str)
        }]
    )

    gz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': [world, ' -r']}.items()
    )

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', '/robot_description', '-name', 'dif_bot', '-z', '0.25']
    )

    # -------------------------------
    # ros2_control (ONLY if enabled)
    # -------------------------------

    load_jsb = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager', '/controller_manager'
        ],
        condition=IfCondition(use_ros2_control),
        output='screen'
    )

    load_diff = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'diff_drive_controller',
            '--controller-manager', '/controller_manager'
        ],
        condition=IfCondition(use_ros2_control),
        output='screen'
    )

    # -------------------------------
    # Bridges
    # -------------------------------

    # Common bridges (always active)
    bridge_common = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Clock
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",

            # Command velocity
            #"/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",

            # Sensors
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/imu@sensor_msgs/msg/Imu[gz.msgs.IMU",

            # Depth camera
            "/camera/depth/image_raw@sensor_msgs/msg/Image[gz.msgs.Image",
            "/camera/depth/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
            "/camera/depth/image_raw/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked",
        ],
        output='screen'
    )

    # ODOM bridge ONLY in pure Gazebo mode
    bridge_odom = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
        ],
        condition=UnlessCondition(use_ros2_control),
        output='screen'
    )

    # -------------------------------
    # Launch description
    # -------------------------------
    return LaunchDescription([

        # Arguments
        DeclareLaunchArgument(
            'world',
            default_value=join(pkg, 'worlds', 'my_world.sdf')
        ),

        DeclareLaunchArgument(
            'use_ros2_control',
            default_value='true'
        ),

        # Core nodes
        rsp,
        gz,

        # Spawn robot (delay for GZ)
        TimerAction(period=2.0, actions=[spawn]),

        # Controllers (only if ros2_control)
        TimerAction(period=5.0, actions=[load_jsb]),
        TimerAction(period=7.0, actions=[load_diff]),

        # Bridges
        bridge_common,
        bridge_odom,
    ])