#!/usr/bin/env python
# 
# Copyright (c) 2011 University of Dundee. 
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# Version: 1.0
#
# This script shows a simple connection to OMERO, printing details of the connection.
# NB: You will need to edit the config.py before running.
#
#
from omero.gateway import BlitzGateway
from omero.rtypes import *
USERNAME, PASSWORD, HOST, PORT = ('will', 'ome', 'localhost', 4064)
# create a connection
conn = BlitzGateway(USERNAME, PASSWORD, host=HOST, port=PORT)
conn.connect()

# Create an Image from 2 others

# Replace one channel with a channel from another image.

imageId = 351       
imageId2 = 352
replaceChannel = 0

image = conn.getObject('Image', imageId)
image2 = conn.getObject('Image', imageId2)
sizeZ, sizeC, sizeT = image.getSizeZ(), image.getSizeC(), image.getSizeT()
dataset = image.getParent()
pixels = image.getPrimaryPixels()
pixels2 = image2.getPrimaryPixels()
# set up a generator of 2D numpy arrays.
def planeGen():
    for z in range(sizeZ):          # all Z sections
        for c in range(sizeC):
            for t in range(sizeT):      # all time-points
                print "Plane: ",z,c,t
                if c == replaceChannel:
                    yield pixels2.getPlane(z,c,t)
                else:
                    yield pixels.getPlane(z,c,t)
desc = "Image created from Image ID: %s, replacing Channel %s from Image ID: %s" % (imageId, replaceChannel, imageId2)
newImg = conn.createImageFromNumpySeq(planeGen(), "ImageFromTwo", sizeZ, sizeC, sizeT, description=desc, dataset=dataset)

# Get original channel names and colors to apply to new image
cNames = []
colors = []
for ch in image.getChannels():
    cNames.append(ch.getLabel())
    colors.append(ch.getColor().getRGB())

# Save channel names and colors
print "Applying channel Names:", cNames, " Colors:", colors
for i, c in enumerate(newImg.getChannels()):
    lc = c.getLogicalChannel()
    lc.setName(cNames[i])
    lc.save()
    r,g,b = colors[i]
    # need to reload channels to avoid optimistic lock on update
    cObj = conn.getQueryService().get("Channel", c.id)
    cObj.red = rint(r)
    cObj.green = rint(g)
    cObj.blue = rint(b)
    cObj.alpha = rint(255)
    conn.getUpdateService().saveObject(cObj)
newImg.resetRDefs() # reset based on colors above

# Apply pixel sizes from original image
px = conn.getQueryService().get("Pixels", newImg.getPixelsId())
if physicalSizeX is not None:
    px.setPhysicalSizeX(rdouble(pixels.getPhysicalSizeX()))
if physicalSizeY is not None:
    px.setPhysicalSizeY(rdouble(pixels.getPhysicalSizeY()))
if physicalSizeZ is not None:
    px.setPhysicalSizeZ(rdouble(pixels.getPhysicalSizeZ()))
conn.getUpdateService().saveObject(px)