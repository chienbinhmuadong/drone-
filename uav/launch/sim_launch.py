import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Khai báo thư mục của các package
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_uav = get_package_share_directory('uav')

    # 2. Đường dẫn tới file sa bàn và thư mục models
    world_path = os.path.join(pkg_uav, 'worlds', 'arena_3x3.world')
    models_path = os.path.join(pkg_uav, 'models')
    xacro_file = os.path.join(pkg_uav, 'urdf', 'pioneer_drone.xacro') 

    # 3. TỰ ĐỘNG KHAI BÁO BIẾN MÔI TRƯỜNG (Thay cho lệnh export thủ công)
    # Giúp Gazebo luôn tìm thấy ảnh bản đồ
    set_env_var = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        models_path
    )

    # 4. Khởi chạy Gazebo (chỉ bật World)
    # Thêm cờ '-r' để Gazebo tự động chạy (Play) ngay khi mở
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': f"-r {world_path}"
        }.items()
    )

    # ====================================================================
    # PHẦN DÀNH CHO TƯƠNG LAI (Hiện tại đang comment lại vì chưa có file)
    # ====================================================================
    
    # xacro_file = os.path.join(pkg_uav, 'urdf', 'pioneer_mini.xacro')
    
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[
            {'use_sim_time': True},
            {'robot_description': Command(['xacro ', xacro_file])}
        ]
    )

    spawn_drone = Node(
        package='ros_gz_sim', 
        executable='create', 
        arguments=[
            '-name', 'pioneer_drone', 
            '-topic', 'robot_description', 
            '-x', '0.5', '-y', '0.5', '-z', '0.0'
        ], 
        output='screen'
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': os.path.join(pkg_uav, 'config', 'ros_gz_bridge.yaml'),
        }],
        output='screen'
    )


    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        parameters=[{'use_sim_time': True}], # Bắt buộc dùng sim time của Gazebo
        output='screen'
    )    

    takeoff_node = Node(
            package='uav',          # Tên package của bạn
            executable='takeoff', # Tên đã khai báo trong setup.py
            name='takeoff_node', # Tên hiển thị khi dùng lệnh 'ros2 node list'
            output='screen',
            #parameters=[{'use_sim_time': True}],         # Để bạn thấy log lệnh in ra trong terminal
        )
    # cv_node = Node(
    #     package='uav',
    #     executable='detect_on_map',
    #     name='computer_vision',
    #     output='screen',
    # )

    # ====================================================================

    # 5. Đưa tất cả vào danh sách Launch
    return LaunchDescription([
        set_env_var,  # Phải nạp biến môi trường trước
        gz_sim,       # Mở thế giới 3D
        
        robot_state_publisher,
        spawn_drone,
        bridge,
        rviz2,
        takeoff_node,
    ])