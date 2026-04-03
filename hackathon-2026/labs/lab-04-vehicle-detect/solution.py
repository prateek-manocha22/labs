# from typing import Optional


# def count_by_class(detections):
#     """
#     Count detections grouped by class name.

#     Args:
#         detections: List of detection dicts with 'class_name' key.

#     Returns:
#         A dict like {"car": 3, "truck": 1}
#     """
#     # TODO: Iterate over detections, count each class_name
#     pass


# def filter_by_confidence(detections, threshold):
#     """
#     Return only detections where confidence > threshold.

#     Args:
#         detections: List of detection dicts with 'confidence' key.
#         threshold:  Minimum confidence value (e.g., 0.75).

#     Returns:
#         Filtered list of detection dicts.
#     """
#     # TODO: Filter and return
#     pass


# def get_top_detection(detections):
#     """
#     Return the detection with the highest confidence score.

#     Args:
#         detections: List of detection dicts.

#     Returns:
#         Single dict with highest confidence, or None if list is empty.
#     """
#     # TODO: Return the max-confidence detection, or None if empty
#     pass

#________________________________________________________________________________________

from typing import Optional


def count_by_class(detections):
    """
    Count detections grouped by class name.

    Args:
        detections: List of detection dicts with 'class_name' key.

    Returns:
        A dict like {"car": 3, "truck": 1}
    """
    # TODO: Iterate over detections, count each class_name
    counts = {}
    for detection in detections:
        name = detection["class_name"]
        counts[name] = counts.get(name, 0) + 1
    return counts
    


def filter_by_confidence(detections, threshold):
    """
    Return only detections where confidence > threshold.

    Args:
        detections: List of detection dicts with 'confidence' key.
        threshold:  Minimum confidence value (e.g., 0.75).

    Returns:
        Filtered list of detection dicts.
    """
    # TODO: Filter and return
    return [d for d in detections if d["confidence"] > threshold]
    


def get_top_detection(detections):
    """
    Return the detection with the highest confidence score.

    Args:
        detections: List of detection dicts.

    Returns:
        Single dict with highest confidence, or None if list is empty.
    """
    # TODO: Return the max-confidence detection, or None if empty
    if not detections:
        return None
    return max(detections, key=lambda d: d["confidence"])