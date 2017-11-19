Dead-Reckoning-Data-Processing

This is the readme file for this project which aims to help you understand how to run the code. the instructions assume you are using Mac and has Julia and Python2 installed.

1. Firstly, you need to gather data using the GetSensorData2.0 app (from LOPSI). This data will be saved asa .txt file in your phone storage. Extract the data. An example of the data file can be found in this repository. And this file will be used as an example for the remaining of the readme. Look for
`example-log-file.txt`.

2. This data contains the raw accelerometer, gyroscope, wifi and other sensor reading values. You would need to pre-process the data into something manageable - like a data table or matrix. Julia (an alternative to Matlab) is used to pre-process the data. Run the following command from your terminal.

  `julia dead-reckoning.jl example-log-file`

  Note that the sensor data parameter does not have the .txt extension. The command will output the accelerometer reading table and graph, gyroscope reading table and graph and wifi reading table and graph, all contained in an output folder named after the sensor log file. (in this case, the folder's name is example-log-file).

  `example-log-file/`

3.  The next step is to generate the dead-reckoning path by feeding the data from the output folder into another julia processing algorithm to get step detection output and step direction output.

  `julia step-counting.jl example-log-file`

  The output from this step will be the path.txt and steps.txt which will be stored in the output folder as well.

4.  Finally, the dead-reckoning path computed can be drawn and corrected using the python program. The main file is `map-out.py`. To control what path to draw, the file will need to be modified manually every time. There is no wrapper function for this python program unfortunately.

  `map-out.py` takes the path.txt file and the map image and plot out the paths. These four code snippets controls what paths to be generated.

  Draws the ground truth and dead-reckoning
  ```
  # Draw Ground Truth
  ground, = map_image.plot_ground_truth(plt)
  # Draw DR
  dr, = map_image.plot_dr(plt)

  plt.legend([ground, dr], ['Ground Truth', 'Dead-Reckoning'])
  plt.show()
  ```

  Draws the ground truth, dead-reckoning and map-matching correction
  ```
  # Draw Ground Truth
  ground, = map_image.plot_ground_truth(plt)
  # Draw DR
  dr, = map_image.plot_dr(plt)
  # Draw map-correction
  map_dr, = map_image.plot_map_matching(plt)

  plt.legend([ground, dr, map_dr], ['Ground Truth', 'Dead-Reckoning', 'Map Matching'])
  plt.show()
  ```
  Draws the ground truth, dead-reckoning and Wifi correction
  ```
  # Draw Ground Truth
  ground, = map_image.plot_ground_truth(plt)
  # Draw DR
  dr, = map_image.plot_dr(plt)
  # Draw wifi_correction
  wifi, = map_image.plot_wifi_correction(plt)

  plt.legend([ground, dr, wifi], ['Ground Truth', 'Dead-Reckoning', 'WiFi'])
  plt.show()
  ```
  Draws the ground truth, dead-reckoning and Hybrid correction
  ```
  # Draw Ground Truth
  ground, = map_image.plot_ground_truth(plt)
  # Draw DR
  dr, = map_image.plot_dr(plt)
  # Draw hybrid_correction
  hybrid, = map_image.plot_hybrid_correction(plt)

  plt.legend([ground, dr, hybrid], ['Ground Truth', 'Dead-Reckoning', 'Hybrid'])
  plt.show()
  ```
  From the four combinations, comment out the lines that don't belong and run the python command

  `python map-out.py example-log-file`

  A `path.png` will be generated and it shows all the steps of the path taken.
