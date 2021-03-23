import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import to_agraph
from bisimulation_algorithms.paige_tarjan.pta import rscp as paige_tarjan
from bisimulation_algorithms.paige_tarjan.graph_decorator import initialize
from bisimulation_algorithms.dovier_piazza_policriti.rank_computation import compute_rank
from PIL import Image as pilImage, ImageFont, ImageDraw
import os
from IPython.display import Image

colors = ['#ffcdd2', '#607d8b', '#795548', '#ff5722', '#7986cb', '#ffe082', '#cddc39', '#9575cd', '#7cb342', '#80cbc4', '#b2ebf2', '#f44336']

def draw(graph, partition, file_name, vx_to_color={}):
    colors_copy = colors.copy()

    for node in graph.nodes:
        graph.nodes[node]['height'] = 0.1
        graph.nodes[node]['shape'] = 'circle'

        graph.nodes[node]['width'] = 0.3
        graph.nodes[node]['height'] = 0.3
        graph.nodes[node]['fixedsize'] = True
        graph.nodes[node]['fontsize'] = 13

        if 'rank' in graph.nodes[node]:
            graph.nodes[node]['label'] = '{}({})'.format(graph.nodes[node]['label'], graph.nodes[node]['rank'])

    block_to_color = {}
    color_to_block = {}
    for idx, block in enumerate(partition):
        for node in block:
            graph.nodes[node]['style'] = 'filled'

            if idx in block_to_color:
                graph.nodes[node]['fillcolor'] = block_to_color[idx]
            else:
                # we check if the color is already given to another block
                if node in vx_to_color and (not vx_to_color[node] in color_to_block or color_to_block[vx_to_color[node]] == idx):
                    graph.nodes[node]['fillcolor'] = vx_to_color[node]

                    color_to_block[vx_to_color[node]] = idx
                    block_to_color[idx] = vx_to_color[node]
                    colors_copy.remove(vx_to_color[node])
                else:
                    color = colors_copy.pop()

                    graph.nodes[node]['fillcolor'] = color
                    color_to_block[color] = idx
                    block_to_color[idx] = color

            vx_to_color[node] = graph.nodes[node]['fillcolor']

    for edge in graph.edges:
        graph.edges[edge]['arrowsize'] = 0.5

    A = to_agraph(graph)
    A.layout('sfdp')
    A.graph_attr['nodesep'] = 1
    A.graph_attr['dpi'] = 300
    A.graph_attr['height'] = 500
    A.draw('{}.png'.format(file_name))

    return vx_to_color

def partition_to_string(partition):
    string = '{'
    for block in partition:
        string += '({}),'.format(','.join(map(str, block)))
    string = string[:len(string) - 1]
    string += '}'
    return string

def append_caption(image_name, partition, font=None):
    image = pilImage.open(image_name)
    width, height = image.size

    partition_string = partition_to_string(partition)

    new_image = pilImage.new('RGB', (width, height + 200), color='white')
    new_image.paste(image, (0,0))
    editable_image = ImageDraw.Draw(new_image)
    w, h = editable_image.textsize(partition_string, font=font)
    editable_image.text(((width - w) / 2, height + 80), partition_string, fill='black', font=font)
    new_image.save(image_name)

arial = ImageFont.truetype("ArialTh.ttf", 60)
