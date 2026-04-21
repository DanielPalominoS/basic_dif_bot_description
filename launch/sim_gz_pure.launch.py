from os.path import join
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    pkg = get_package_share_directory("basic_dif_bot_description")
    world = LaunchConfiguration("world", default=join(pkg, "worlds", "my_world.sdf"))

    # Robot description (URDF/Xacro)
    robot_description = Command(
        ["xacro ", join(pkg, "urdf", "robot_gz.urdf.xacro"), " use_ros2_control:=false"]
    )

    # Robot State Publisher (uses sim time)
    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {"robot_description": ParameterValue(robot_description, value_type=str)},
            {"use_sim_time": True},
        ],
        remappings=[("/joint_states", "/joint_states")],
    )

    # Launch Gazebo Sim
    gz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            join(
                get_package_share_directory("ros_gz_sim"), "launch", "gz_sim.launch.py"
            )
        ),
        launch_arguments={"gz_args": world}.items(),
    )

    # Spawn robot into Gazebo
    spawn = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=["-topic", "/robot_description", "-name", "dif_bot", "-z", "0.25"],
    )

    # ROS ↔ GZ Bridge
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[{"use_sim_time": True}],
        arguments=[
            # Joint states
            "/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model",
            # TF (critical)
            "/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
            # Simulation clock
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            # Velocity command
            "/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            # Odometry
            "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            # Sensors
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/imu@sensor_msgs/msg/Imu[gz.msgs.IMU",
            # Depth camera
            "/camera/depth/image_raw@sensor_msgs/msg/Image[gz.msgs.Image",
            "/camera/depth/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
            "/camera/depth/image_raw/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked",
        ],
    )
    static_tf_depth = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=[
            "0",
            "0",
            "0",  # xyz
            "0",
            "0",
            "0",  # rpy
            "camera_depth_frame",  # parent (your TF tree)
            "dif_bot/base_link/depth_camera",  # child (Gazebo frame)
        ],
        parameters=[{"use_sim_time": True}],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("world", default_value=world),
            rsp,
            gz,
            TimerAction(period=2.0, actions=[spawn]),
            bridge,
            static_tf_depth,
        ]
    )
