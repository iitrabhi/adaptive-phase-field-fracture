// Gmsh project created on Mon Nov 21 17:13:51 2022
SetFactory("OpenCASCADE");
lc = 20;
Point(1) = {0, 0, 0, lc};
Point(2) = {500, 0, 0, lc};
Point(3) = {500, 125, 0, lc};
Point(4) = {248.75, 125, 0, 2.5};
Point(5) = {251.25, 125, 0, 2.5};
Point(6) = {248.75, 115, 0, 2.5};
Point(7) = {251.25, 115, 0, 2.5};
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

Plane Surface(1) = {1};

Physical Surface("domain") = {1};

