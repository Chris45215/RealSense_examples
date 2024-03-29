import numpy as np
import pyrealsense2 as rs
import datetime
import open3d

#only run this if this is the startup file
if __name__ == '__main__':
	# Configure depth and color streams
	pipeline = rs.pipeline()
	config = rs.config()
	pc = rs.pointcloud()
	filter_option = 2
	decimation_magnitude = 2

	# Get device product line for setting a supporting resolution
	pipeline_wrapper = rs.pipeline_wrapper(pipeline)
	pipeline_profile = config.resolve(pipeline_wrapper)
	device = pipeline_profile.get_device()
	device_product_line = str(device.get_info(rs.camera_info.product_line))

	found_rgb = False
	for s in device.sensors:
		if s.get_info(rs.camera_info.name) == 'RGB Camera':
			found_rgb = True
			break
	if not found_rgb:
		print("The demo requires Depth camera with Color sensor")
		exit(0)

	config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

	if device_product_line == 'L500':
		config.enable_stream(rs.stream.color, 960, 540, rs.format.rgb8, 30)  # Change for colorization
	else:
		config.enable_stream(rs.stream.color, 1280, 720, rs.format.rgb8, 30)
		#config.enable_stream(rs.stream.color, 424, 240, rs.format.rgb8, 30) #smaller frame, for the decimation
		
	# Start streaming
	pipe_profile = pipeline.start(config)

	#Set depth sensor to "high accuracy" mode.
	depth_sensor = pipe_profile.get_device().first_depth_sensor()

	preset_range = depth_sensor.get_option_range(rs.option.visual_preset)
	for i in range(int(preset_range.max)):
		visulpreset = depth_sensor.get_option_value_description(rs.option.visual_preset,i)
		#print('range index ', i, ': ', visulpreset)
		if visulpreset == "High Density":
			depth_sensor.set_option(rs.option.visual_preset, i)
			print("setting the ", visulpreset, " option on the sensor.")




	align = rs.align(rs.stream.color)

	vis = open3d.visualization.Visualizer()
	vis.create_window('PCD', width=1280, height=720)
	pointcloud = open3d.geometry.PointCloud()
	geom_added = False

	decimation_filter = rs.decimation_filter(decimation_magnitude)

	# Main loop
	frame_number = 0
	while(True):
		dt0 = datetime.datetime.now()  # For FPS
		frame_number += 1
		
		# Wait for a coherent pair of frames: depth and color
		frames = pipeline.wait_for_frames()
		profile = frames.get_profile()


		if filter_option == 1:
			#normal handling, no compression
			frames = align.process(frames)

		if filter_option == 2:
			#decimation approach
			decimated_depth = decimation_filter.process(frames).as_frameset()
			frames = align.process(decimated_depth)
		


		depth_frame = frames.get_depth_frame()
		color_frame = frames.get_color_frame()
		if not depth_frame or not color_frame:
			continue

		# Convert images to numpy arrays
		depth_image = np.asanyarray(depth_frame.get_data())
		color_image = np.asanyarray(color_frame.get_data())

		img_depth = open3d.geometry.Image(depth_image)
		img_color = open3d.geometry.Image(color_image)
		#rgbd = open3d.geometry.RGBDImage.create_from_color_and_depth(img_color, img_depth, convert_rgb_to_intensity=False)
		rgbd = open3d.geometry.RGBDImage.create_from_color_and_depth(img_color, img_depth, convert_rgb_to_intensity=False, depth_trunc = 10.0) #this function truncates to 3 meters by default; the addition of the depth_trunc parameter fixes it.

		intrinsics = profile.as_video_stream_profile().get_intrinsics()
		pinhole_camera_intrinsic = open3d.camera.PinholeCameraIntrinsic(intrinsics.width, intrinsics.height, intrinsics.fx, intrinsics.fy, intrinsics.ppx, intrinsics.ppy)

		pcd = open3d.geometry.PointCloud.create_from_rgbd_image(rgbd, pinhole_camera_intrinsic)

		'''
		#use only every nth point; discard the rest.
		n = 1
		pointcloud.points = open3d.cpu.pybind.utility.Vector3dVector(np.asarray(pcd.points)[::n])
		pointcloud.colors = open3d.cpu.pybind.utility.Vector3dVector(np.asarray(pcd.colors)[::n])
		'''

		
		#use all the points
		pointcloud.points = pcd.points
		pointcloud.colors = pcd.colors  # Disabling this creates heatmap
		

		opt = vis.get_render_option()
		opt.show_coordinate_frame = True

		coord_axes = open3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1, origin=np.array([0., 0., 0.]))

		if geom_added == False:
			vis.add_geometry(pointcloud)
			vis.add_geometry(coord_axes)
			geom_added = True
		
		vis.update_geometry(pointcloud)
		vis.update_geometry(coord_axes)
		vis.poll_events()
		vis.update_renderer()		

		process_time = datetime.datetime.now() - dt0
		print("FPS: "+str(1/process_time.total_seconds()))

	pipeline.stop()
	vis.destroy_window()
	cv.destroyAllWindows() # close all windows
