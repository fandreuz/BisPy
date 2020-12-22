from bisimulation_algorithms.dovier_piazza_policriti.graph_entities import _Block, _Vertex

def check_block_stability(
    block1: _Block, block2: _Block
) -> bool:
    """Checks whether block1 is stable with respect to block2, namely block1
    is a subset of E^{-1}(block2) or the two sets are distinct. This method
    doesn't check whether block2 is stable with respect to block1.

    Args:
        block1 (_Block): The first block.
        block2 (_Block): The second block.

    Returns:
        bool: True if block1 is stable with respect to block2, False otherwise.
    """

    # if there's a vertex y in B_qblock_vertexes such that for the i-th vertex
    # we have i->y, then is_inside_B[i] = True
    goes_inside_block2 = []
    for vertex in block1.vertexes:
        flag = False
        for image_vertex in vertex.image:
            if image_vertex in block2.vertexes:
                flag = True
        goes_inside_block2.append(flag)

    # all == True if for each vertex x in A there's a vertex y such that
    # x \in E({x}) AND y \in B.
    # not any == True if the set "image of A" and B are distinct.
    return all(goes_inside_block2) or not any(goes_inside_block2)
