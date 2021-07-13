import itertools
from typing import List, Iterable

from bispy.utilities.graph_entities import _Vertex, _QBlock

# check if the given partition is stable with respect to the given block, or if
# it's stable if the block isn't given
def is_stable_vertexes_partition(partition: List[List[_Vertex]]) -> bool:
    """Checks the stability of the given partition. The input must be a
    partition of Vertex instances, and the relation which we consider for the
    stability is a->b, where a,b are two vertexes.

    Args:
        partition (list[list[_Vertex]]): A partition of Vertex instances.

    Returns:
        bool: True if the partition is stable. False otherwise.
    """

    for couple in itertools.product(partition, repeat=2):
        if not (
            check_vertexes_stability(couple[0], couple[1])
            and check_vertexes_stability(couple[1], couple[0])
        ):
            return False
    return True


def is_stable_partition(partition: List[_QBlock]) -> bool:
    return is_stable_vertexes_partition(
        [list(block.vertexes) for block in partition]
    )


# return True if A_block \subseteq R^{-1}(B_block) or
# A_block cap R^{-1}(B_block) = \emptyset
def check_vertexes_stability(
    A_block_vertexes: Iterable[_Vertex], B_block_vertexes: Iterable[_Vertex]
) -> bool:
    """Checks the stability of the first block with respect to the second one.
    The two inputs must be list of Vertex instances, and the relation which we
    consider for the stability is a->b, where a,b are two vertexes.

    Args:
        A_block_vertexes (list[_Vertex]): The checked block.
        B_block_vertexes (list[_Vertex]): The block against we check the
            stability of A.

    Returns:
        bool: True if A is stable with respect to B. False otherwise.
    """

    # if there's a vertex y in B_qblock_vertexes such that for the i-th vertex
    # we have i->y, then is_inside_B[i] = True
    is_inside_B = []
    for vertex in A_block_vertexes:
        is_inside_B.append(False)
        for edge in vertex.image:
            if edge.destination in B_block_vertexes:
                is_inside_B[-1] = True

    # all == True if for each vertex x in A there's a vertex y such that
    # x \in E({x}) AND y \in B.
    # not any == True if the set "image of A" and B are distinct.
    return all(is_inside_B) or not any(is_inside_B)


# return True if A_block \subseteq R^{-1}(B_block) or
# A_block cap R^{-1}(B_block) = \emptyset
def check_block_stability(A_block: _QBlock, B_block: _QBlock) -> bool:
    """Checks the stability of the first block with respect to the second one.
    The two inputs must be list of Vertex instances, and the relation which we
    consider for the stability is a->b, where a,b are two vertexes.

    Args:
        A_block_vertexes (list[_Vertex]): The checked block.
        B_block_vertexes (list[_Vertex]): The block against we check the
            stability of A.

    Returns:
        bool: True if A is stable with respect to B. False otherwise.
    """

    A_block_vertexes = [vertex for vertex in A_block.vertexes]
    B_block_vertexes = [vertex for vertex in B_block.vertexes]

    return check_vertexes_stability(A_block_vertexes, B_block_vertexes)
