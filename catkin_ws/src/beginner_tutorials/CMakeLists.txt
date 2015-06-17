cmake_minimum_required(VERSION 2.8.3)
project(beginner_tutorials)
			find_package(catkin REQUIRED COMPONENTS
			   roscpp
			   rospy
			   std_msgs
			   message_generation
			)
			add_message_files(
			  FILES
			  Num.msg
			)
			generate_messages(
			  DEPENDENCIES
			  std_msgs
			)
			catkin_package(
			  INCLUDE_DIRS include
			  LIBRARIES beginner_tutorials
			  CATKIN_DEPENDS roscpp rospy std_msgs
			  DEPENDS system_lib
			  CATKIN_DEPENDS message_runtime
			)
			include_directories(
			  ${catkin_INCLUDE_DIRS}
			)