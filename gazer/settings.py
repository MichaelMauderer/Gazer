from __future__ import unicode_literals, division, print_function
from gazer.modules.dof.scenes import SimpleArrayStackDecoder, \
    ImageStackScene, \
    SimpleArrayStackEncoder

DECODERS = {ImageStackScene.scene_type: SimpleArrayStackDecoder()}

ENCODERS = {ImageStackScene.scene_type: SimpleArrayStackEncoder()}
