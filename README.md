Gazer
========

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

About
-----
This software was created at the University of St Andrews by Michael Mauderer with the help of David Morrison.
It was developed as part of the [Deepview project](http://deepview.cs.st-andrews.ac.uk/), supervised by Miguel Nacenta.
