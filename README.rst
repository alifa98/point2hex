=============================================================================
``point2hex`` - Generate hexagons for trajectories
=============================================================================


Requiremnets
------------

::

    pip install -r requirements.txt
    
    
Builds and configures Python environment
------------

::

    pip install -e .


Usage
-----

::

    From trajectory points to hexagon sequences:
        ./job.sh              

    Arguments:
        <path>                The path to the directory containing the application files for which a requirements file
                              should be generated (defaults to the current working directory)

    Options:
        --res                 The resolution of hexagons from H3 library.
        

Example
-------

::
    
    $ `python Point2Hex.py ttt.csv -slon "pickup_longitude" -slat "pickup_latitude" -elon "dropoff_longitude" -elat "dropoff_latitude" -t 10 -S -o ttt_points `
