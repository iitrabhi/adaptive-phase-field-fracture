// Gmsh project created on Mon Nov 21 17:13:51 2022
SetFactory("OpenCASCADE");
lc = 20;
Point(1) = {0, 0, 0, lc};
Point(2) = {500, 0, 0, lc};
Point(3) = {500, 125, 0, lc};
Point(4) = {248.75, 125, 0, lc};
Point(5) = {251.25, 125, 0, lc};
Point(6) = {248.75, 115, 0, lc};
Point(7) = {251.25, 115, 0, lc};
Point(8) = {0, 125, 0, lc};

Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 5};
Line(4) = {5, 7};
Line(5) = {7, 6};
Line(6) = {6, 4};
Line(7) = {4, 8};
Line(8) = {8, 1};
Curve Loop(1) = {7, 8, 1, 2, 3, 4, 5, 6};


Physical Surface("domain") = {1};

// Assuming Points 9 and 10 define the line at x=250
Point(9) = {250, 0, 0, 0.5}; // Smaller characteristic length for refinement
Point(10) = {250, 125, 0, 0.5};

// Define a line between these points
Line(9) = {9, 10};

// Say we would like to obtain mesh elements with size lc/30 near curve 2 and
// point 5, and size lc elsewhere. To achieve this, we can use two fields:
// "Distance", and "Threshold". We first define a Distance field (`Field[1]') on
// points 5 and on curve 2. This field returns the distance to point 5 and to
// (100 equidistant points on) curve 2.
Field[1] = Distance;
Field[1].CurvesList = {9};
Field[1].Sampling = 100;


// We then define a `Threshold' field, which uses the return value of the
// `Distance' field 1 in order to define a simple change in element size
// depending on the computed distances
//
// SizeMax -                     /------------------
//                              /
//                             /
//                            /
// SizeMin -o----------------/
//          |                |    |
//        Point         DistMin  DistMax
Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = 0.625/4;
Field[2].SizeMax = lc;
Field[2].DistMin = 10;
Field[2].DistMax = 80;

// Let's use the minimum of all the fields as the background mesh size field
Field[7] = Min;
Field[7].FieldsList = {2};
Background Field = 7;

Plane Surface(1) = {1};