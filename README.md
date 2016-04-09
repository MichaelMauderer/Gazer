[logo]: https://github.com/MichaelMauderer/Gazer/blob/develop/gazer/assets/logo/Gazer-Logo-full.jpg "Gazer"
[pier-preview]: https://github.com/MichaelMauderer/Gazer/blob/develop/gazer/assets/pier-preview.PNG "St Andrews Pier"
[cloister-preview]: https://github.com/MichaelMauderer/Gazer/blob/develop/gazer/assets/cloister-preview.PNG "St Andrews Cloister"
[workbench-preview]: https://github.com/MichaelMauderer/Gazer/blob/develop/gazer/assets/workbench-preview.PNG "SACHI Workbench"
[scale-preview]: https://github.com/MichaelMauderer/Gazer/blob/develop/gazer/assets/scale-preview.PNG "Paper Scale"

![Gazer][logo]

Application to view gaze-contingent images, e.g., images with variable
depth-of-field created from Lytro images.

Features
--------
* support for Tobii EyeX eye tracker
* importer for Lytro ILLUM images.
* Saving and loading of optimised custom file format that allows easy sharing
  of images with gaze-contingent depth-of-field.
* export and import of Image Stacks (combination of DOF slices and a depth map)

Usage
-----
Running the UI from source requires the requirements described in the
requirements.txt and the location of the Tobii.EyeX.Client.dll to be specified
in the EYEX_LIB_PATH environment variable or be in the working dir the script
is started from. We recommend setting it to '../lib' and putting the dll into the
corresponding top level lib folder.

Example Images
--------------


<a href="https://github.com/MichaelMauderer/Gazer/raw/develop/gazer/assets/st-andrews-pier.gc"><img src="https://github.com/MichaelMauderer/Gazer/blob/develop/gazer/assets/pier-preview.PNG" align="float left" width="400" ></a>
<a href="https://github.com/MichaelMauderer/Gazer/raw/develop/gazer/assets/st-andrews-cloister.gc"><img src="https://github.com/MichaelMauderer/Gazer/blob/develop/gazer/assets/cloister-preview.PNG" align="float left" width="400" ></a>
<a href="https://github.com/MichaelMauderer/Gazer/raw/develop/gazer/assets/sachi_workbench.gc"><img src="https://github.com/MichaelMauderer/Gazer/blob/develop/gazer/assets/workbench-preview.PNG" align="float left" width="400" ></a>
<a href="https://github.com/MichaelMauderer/Gazer/raw/develop/gazer/assets/scale.gc"><img src="https://github.com/MichaelMauderer/Gazer/blob/develop/gazer/assets/scale-preview.PNG" align="float left" width="400" ></a>

About
-----
This software was created at the University of St Andrews by Michael Mauderer, David Morrison and Miguel Nacenta.
It was developed as part of the [Deepview project](http://deepview.cs.st-andrews.ac.uk/).
