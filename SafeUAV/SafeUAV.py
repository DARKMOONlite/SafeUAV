import rclpy
from rclpy.node import Node
import argparse
import cv2
import datetime
import matplotlib.cm as cm
import numpy as np
import os
import sys
import time
import torch
sys.path.append('../neural-wrappers')

from neural_wrappers.utilities import minMaxNormalizeData
from neural_wrappers.pytorch import maybeCuda
from unet_tiny_sum import ModelUNetTinySum
import rclpy
from sensor_msgs.msg import Image
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy, HistoryPolicy
from cv_bridge import CvBridge
class SafeUAVNode(Node):
    def __init__(self):
        super().__init__('SUAV_node')
        self.get_logger().info('SafeUAV Node has been started')
        
        # Initialize CV Bridge for image conversion
        self.bridge = CvBridge()
        
        self.declare_parameter(name="SUAV_input_topic",value="/image")
        self.declare_parameter(name="SUAV_output_topic",value="/safe_uav/output")
        self.declare_parameter(name="SUAV_dstdir",value='data/results')
        self.declare_parameter(name="SUAV_task",value='classification')
        self.declare_parameter(name="SUAV_weights_file",value=None)
        self.declare_parameter(name="SUAV_devid",value=0)
        self.declare_parameter(name="SUAV_width",value=320)
        self.declare_parameter(name="SUAV_height",value=240)
        self.declare_parameter(name="SUAV_fps",value=30)
        self.declare_parameter(name="SUAV_pixfmt",value="YUYV")
        self.declare_parameter(name="SUAV_num",value=100)
        self.declare_parameter(name="SUAV_no_save",value=False)
        self.declare_parameter(name="SUAV_display",value=2) #0: only output, 1: input and output, 2: input, output, and overlap
        self.declare_parameter(name="SUAV_cmap",value="hot")
        self.params:dict[str,int|float|str]=self.get_parameters_by_prefix("SUAV")
        
        
        self.image_subscriber = self.create_subscription(msg_type=Image,topic=self.params["SUAV_input_topic"],callback=self.image_callback) #ty:ignore
        self.image_publisher = self.create_publisher(msg_type=Image,topic=self.params["SUAV_output_topic"])
        if self.params["SUAV_task"] == 'classification':
            dIn, dOut = 3, 3
        elif self.params["SUAV_task"]== 'regression':
            dIn, dOut = 3, 1
        else:
            assert False, f'invalid task: {self.params["SUAV_task"]}'
        if self.params["SUAV_weights_file"] is None:
            if self.params["SUAV_task"] == 'classification':
                self.params["SUAV_weights_file"] = 'data/weights/small-hvo.pkl'
            elif self.params["SUAV_task"] == 'regression':
                self.params["SUAV_weights_file"] = 'data/weights/small-depth.pkl'
            else:
                assert False, f'invalid task: {self.params["SUAV_task"]}'
        
        
        self.model = ModelUNetTinySum(dIn=dIn, dOut=dOut, numFilters=16)
        self.model = maybeCuda(self.model)
        self.model.loadWeights(self.params["SUAV_weights_file"])

        self.iteration = 0
        self.t_begin, self.t = time.time(),time.time()
        self.fps_list, self.t_list = [], []
    
    def __del__(self):
        pass
        
    def image_callback(self, image: Image):
        if image is None:
            return
        
        cv_image = self.bridge.imgmsg_to_cv2(image, desired_encoding='bgr8')
        cv_image = minMaxNormalizeData(np.float32(cv_image), np.min(cv_image), np.max(cv_image))
        cv_image = maybeCuda(torch.from_numpy(cv_image))
        cv_image = self.model.forward(cv_image)
    
        res_ = cv_image.detach().cpu().numpy()[0]
        res_ = self.minMaxNormalizeFrame(res_)
        if self.params["SUAV_task"] == 'classification':
            hvn = np.argmax(res_, axis=-1)
            tmp = np.zeros((*hvn.shape, 3), dtype=np.float32)
            tmp[np.where(hvn == 0)] = 0, 255, 0
            tmp[np.where(hvn == 1)] = 255, 0, 0
            tmp[np.where(hvn == 2)] = 0, 0, 255
        elif self.params["SUAV_task"] == 'regression':
            cmap = eval(f"cm.{self.params["SUAV_cmap"]}")
            tmp = cmap(res_[:,:,0])[...,:3]
        else:
            assert False, f'invalid task: {self.params["SUAV_task"]}'
    
        res = self.minMaxNormalizeFrame(tmp)

        t_ = time.time() - t
        fps = 1 / t_
        t = time.time()

        if not self.params["SUAV_no_save"] or self.params["SUAV_demo"]:
            out = cv2.cvtColor(res, cv2.COLOR_RGB2BGR)
            if self.params["SUAV_display"] == 0:
                disp = out
            elif self.params["SUAV_display"] == 1:
                disp = cv2.hconcat([cv_image, out])
            elif self.params["SUAV_display"] == 2:
                overlap = cv2.addWeighted(cv_image, 0.6, out, 0.4, 0)
                disp = cv2.hconcat([cv_image, out, overlap])
            else:
                assert False, f'invalid display option: {self.params["SUAV_display"]}'

        if not self.params["SUAV_no_save"]:
            dst = os.path.join(self.params["SUAV_dstdir"], f'{self.iteration:05d}.png')
            cv2.imwrite(dst, disp)

        
        
    def minMaxNormalizeFrame(self,frame):
        Min, Max = np.min(frame), np.max(frame)
        frame -= Min
        frame /= (Max - Min)
        frame *= 255
        return np.uint8(frame)




def main(args=None):
    rclpy.init(args=args)
    node = SafeUAVNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
