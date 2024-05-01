from typing import Optional, List

def calculate_average(test_score: Optional[float], exam_score: Optional[float]) -> float:
    """
    Calculate the average of test_score and exam_score.

    Args:
        test_score (float): The test score.
        exam_score (float): The exam score.

    Returns:
        float: The average of test_score and exam_score.
    """
    if test_score is not None and exam_score is None:
        return test_score
    
    elif test_score is None and exam_score is not None:
        return exam_score
    
    elif test_score is not None and exam_score is not None:
        return (test_score + exam_score) / 2
    
    else:
        return 0.0

def calculate_total(results: List[float]) -> float:
    """
    Calculate the total of a list of results.

    Args:
        results (List[float]): List of result values.

    Returns:
        float: The total of the result values.
    """
    return sum(results)

def calculate_overall_average(total: float, num_subjects: int) -> float:
    """
    Calculate the overall average.

    Args:
        total (float): The total of all subject averages.
        num_subjects (int): The number of subjects.

    Returns:
        float: The overall average.
    """
    if num_subjects == 0:
        return 0.0
    return total / num_subjects

def calculate_overall_status(overall_average: float) -> str:
    """
    Determine the overall status based on the overall average.

    Args:
        overall_average (float): The overall average.

    Returns:
        str: The overall status ('Pass' or 'Fail').
    """
    if overall_average >= 25:
        return "Pass"
    else:
        return "Fail"
