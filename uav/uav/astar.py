import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Point
from nav_msgs.msg import Path
import numpy as np

# Giả định: Bạn đã có file pathfinding trong cùng package
from uav.pathfinding_logic import build_grid_array, plan_mission 

class PathPlannerNode(Node):
    def __init__(self):
        super().__init__('path_planner_node')
        
        # 1. Khởi tạo Grid và tính toán kế hoạch (Mission Planning)
        # Giả định FORBIDDEN_ZONE và RESOLUTION được lấy từ config
        self.grid = build_grid_array(forbidden_zone={"x_min": 1.0, "x_max": 2.0, "y_min": 1.0, "y_max": 2.0})
        self.waypoints = plan_mission(self.grid)
        
        # 2. Publisher gửi tọa độ mục tiêu cho drone (hoặc gửi Path)
        self.path_pub = self.create_publisher(Path, '/drone_path', 10)
        self.target_pub = self.create_publisher(PoseStamped, '/setpoint_position', 10)
        
        # 3. Giả lập vòng lặp xử lý (có thể thay bằng timer hoặc callback nhận ArUco)
        self.current_wp_index = 0
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        if self.current_wp_index < len(self.waypoints):
            wp = self.waypoints[self.current_wp_index]
            target_m = wp["to_m"]
            
            # Gửi tọa độ mục tiêu đến drone
            msg = PoseStamped()
            msg.pose.position.x = float(target_m[0])
            msg.pose.position.y = float(target_m[1])
            msg.pose.position.z = 1.0 # Độ cao mặc định
            self.target_pub.publish(msg)
            
            self.get_logger().info(f"Đang bay tới: {target_m}")
            self.current_wp_index += 1
        else:
            self.get_logger().info("Đã hoàn thành lộ trình!")

def main(args=None):
    rclpy.init(args=args)
    node = PathPlannerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()