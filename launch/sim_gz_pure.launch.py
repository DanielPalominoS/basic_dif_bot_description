from os.path import join
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    pkg = get_package_share_directory('basic_dif_bot_description')
    world = LaunchConfiguration('world', default=join(pkg, 'worlds', 'my_world.sdf'))

    robot_description = Command([
        'xacro ', join(pkg, 'urdf', 'robot_gz.urdf.xacro'),
        ' use_ros2_control:=false'
    ])

    # Robot State Publisher (necesita joint_states)
    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        remappings=[
            ('/joint_states', '/joint_states')
        ]
    )

    # Lanzar Gazebo
    gz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': world}.items()
    )

    # Spawner del robot
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', '/robot_description', '-name', 'dif_bot', '-z', '0.25']
    )

    # Bridge ROS <-> GZ
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Joint states desde GZ
            "/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model",

            # Comandos de velocidad
            "/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",

            # Odometría
            "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",

            # Sensores
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/imu@sensor_msgs/msg/Imu[gz.msgs.IMU",
            "/camera@sensor_msgs/msg/Image[gz.msgs.Image",
            # "/camera/image@sensor_msgs/msg/Image[gz.msgs.Image",
            "/camera/camera_info@sensor_msgs/msg/CameraInfo[ignition.msgs.CameraInfo",
            "/camera/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked",
        ]
        # remappings=[
        #     ('/world/default/model/dif_bot/joint_state', '/joint_states')
        # ]
    )

    # bridge = Node(
    #     package='ros_gz_bridge',
    #     executable='parameter_bridge',
    #     arguments=[
    #         "/world/default/model/dif_bot/joint_state@sensor_msgs/msg/JointState[ignition.msgs.Model",
    #         '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',
    #         '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
    #         '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
    #         '/imu@sensor_msgs/msg/Imu[ignition.msgs.IMU',
    #         '/camera/image@sensor_msgs/msg/Image[ignition.msgs.Image',
    #     ],
    #     remappings=[
    #         ('/world/default/model/dif_bot/joint_state', '/joint_states')
    #     ]
    # )

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value=world),
        rsp,
        gz,
        TimerAction(period=2.0, actions=[spawn]),
        bridge
    ])
