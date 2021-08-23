# RealSense_examples
Pointcloud examples that use the RealSense cameras.

This program shows the output from two Intel RealSense cameras, the L515 and the D455, in both the RealSense Viewer bundled with the Intel SDK, and in an Open3D pointcloud made with Python (realsense_o3d_colorized.py). The included Images are screenshots from the RealSense Viewer and realsense_o3d_colorized.py (running in both a colorized and a depth heatmap mode). The example files show that the Open3D version clips the points furthest from the sensor. In the D455 images, the background wall is not visible in the Open3D version but is visible in the RealSenseViewer version. For the L515 images, the effect is much more extreme as the clipping begins at 0.73 meters from the sensor (I measured with a meterstick, and ensured that the meterstick was not creating interference). This makes the L515 almost unusable, as its minimum range is 0.6 meters. 

The code in realsense_o3d_colorized.py is based on Open3D example and tutorial code, but may have errors. If you see any errors, please contribute feedback to help identify them - that's why I created this repo.
