import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from numpy import pi 

class DroneSurveyNode(Node):
    def __init__(self):
        super().__init__('drone_survey_node')

        self.cam_sub = self.create_subscription(Image, '/camera/image_raw', self.cam_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.bridge = CvBridge()
        self.cv_image = None

        self.state = 'TAKEOFF'
        self.start_time = self.get_clock().now().nanoseconds / 1e9
        self.rotation_count = 0
        self.get_logger().info("🚀 Bắt đầu kịch bản: Bay lên 1.5m và chụp ảnh...")
        self.timer = self.create_timer(0.2, self.control_loop)

    def cam_callback(self, msg):
        try:
            self.cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f"Lỗi khi nhận ảnh: {e}")

    def save_image(self, filename):
        if self.cv_image is not None:
            try:
                cv2.imwrite(filename, self.cv_image)
                self.get_logger().info(f"[CAMERA] 📸 Đã lưu thành công: {filename}")
            except Exception as e:
                self.get_logger().error(f"⚠️ Không thể lưu ảnh! Lỗi: {e}")
        else:
            self.get_logger().warning(f"[CAMERA] ⚠️ Chưa nhận được luồng ảnh từ topic /camera/image_raw!")

    def control_loop(self):
        msg = Twist()
        current_time = self.get_clock().now().nanoseconds / 1e9
        
        # Tránh trường hợp Gazebo chưa kịp gửi thời gian
        elapsed = current_time - self.start_time
        if elapsed == 0:
            return 
            
        elapsed = current_time - self.start_time

        if self.state == 'TAKEOFF':
            if elapsed < 3.0:
                msg.linear.z = 0.5
                self.cmd_pub.publish(msg)
            else:
                self.state = 'HOVER_INITIAL'
                self.start_time = self.get_clock().now().nanoseconds / 1e9
                self.get_logger().info("✅ Đã đạt độ cao. Đang giữ thăng bằng...")

        elif self.state == 'HOVER_INITIAL':
            msg.linear.z = 0.0
            self.cmd_pub.publish(msg)
            
            if elapsed > 1.5:
                self.save_image("anh_goc_0_do.jpg")
                self.state = 'ROTATE'
                self.start_time = self.get_clock().now().nanoseconds / 1e9
                self.get_logger().info("🔄 Bắt đầu xoay phải lần 1...")

        elif self.state == 'ROTATE':
            # Xoay với tốc độ 1.0 rad/s trong 1.57 giây (~90 độ)
            if elapsed < 1.57:
                msg.angular.z = -1.0  
                self.cmd_pub.publish(msg)
            else:
                self.state = 'HOVER_AFTER_ROTATE'
                self.start_time = self.get_clock().now().nanoseconds / 1e9

        elif self.state == 'HOVER_AFTER_ROTATE':
            msg.angular.z = 0.0
            self.cmd_pub.publish(msg)
            
            if elapsed > 1.5:
                self.rotation_count += 1
                self.save_image(f"anh_goc_xoay_phai_{self.rotation_count * 90}_do.jpg")
                
                if self.rotation_count < 3:
                    self.state = 'ROTATE'
                    self.start_time = self.get_clock().now().nanoseconds / 1e9
                    self.get_logger().info(f"🔄 Bắt đầu xoay phải lần {self.rotation_count + 1}...")
                else:
                    self.state = 'DONE'
                    self.get_logger().info("🏁 Đã hoàn thành nhiệm vụ!")

        elif self.state == 'DONE':
            msg.linear.z = 0.0
            msg.angular.z = 0.0
            self.cmd_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = DroneSurveyNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        stop_msg = Twist()
        node.cmd_pub.publish(stop_msg)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()