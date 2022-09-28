import Sofa
import os

from SSD.Core.Rendering.VedoVisualizer import VedoVisualizer
from Caduceus import Caduceus

USE_GUI = True


def createScene(node):

    global USE_GUI

    if USE_GUI:
        node.addObject(Caduceus(node, name='Controller'))

    else:
        visualizer = VedoVisualizer(database_name='rendering-offscreen', remove_existing=True)
        node.addObject(Caduceus(node, database=visualizer.get_database(), name='Controller'))
        return visualizer


if __name__ == '__main__':

    USE_GUI = False

    root = Sofa.Core.Node('root')
    viewer = createScene(root)
    Sofa.Simulation.init(root)
    viewer.init_visualizer()

    for _ in range(300):
        Sofa.Simulation.animate(root, root.dt.value)
        viewer.render()

    for file in os.listdir(os.getcwd()):
        if '.ini' in file or '.log' in file:
            os.remove(file)