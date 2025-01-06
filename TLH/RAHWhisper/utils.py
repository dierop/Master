import torch
import random
import numpy as np

def seed_everything(seed):      
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = True

def read_file(path: str):
    files=[]
    text=[]
    with open(path, 'r') as file:
        data=file.readlines()
        for line in data:
            line=line.strip().split(',')
            files.append(line[0])
            text.append(line[1])
    return files[1:], text[1:]
            
    

from datetime import datetime, timedelta
import re

def parse_date_with_prompt(prompt_text):
    """
    Parses a text with a date prefix and calculates the resulting date based on the text instructions.

    Args:
        prompt_text (str): Input text in the format "dd/mm/aa [text instructions]".

    Returns:
        str: The resulting date in "dd/mm/aa" format.
    """
    # Extract the date and the instructions from the input
    match = re.match(r"(\d{2}/\d{2}/\d{2})\s+(.+)", prompt_text)
    if not match:
        raise ValueError("Input must be in the format 'dd/mm/aa [instructions]'")

    date_str, instructions = match.groups()

    # Parse the initial date
    base_date = datetime.strptime(date_str, "%d/%m/%y")
    day_match = re.search(r"(lunes|martes|miércoles|jueves|viernes|sábado|domingo)", instructions)

    # Interpret the instructions
    if "pasado mañana" in instructions or "par" in instructions:
        result_date = base_date + timedelta(days=2)
    elif "mañana" in instructions:
        result_date = base_date + timedelta(days=1)
    elif "tres" in instructions:
        result_date = base_date + timedelta(days=3)
    elif day_match:
        target_day = day_match.group(1)
        days_of_week = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        current_day_index = base_date.weekday()
        target_day_index = days_of_week.index(target_day)
        delta_days = (target_day_index - current_day_index + 7) % 7
        if delta_days == 0:
            delta_days = 7  # Move to the next week's day
        result_date = base_date + timedelta(days=delta_days)
    else:
        raise ValueError("Unsupported instruction format")

    # Return the resulting date in the desired format
    return result_date.strftime("%d/%m/%y")

def generate_random_date(start_date="01/01/00", end_date="31/12/60"):
    """
    Generates a random date between two given dates.

    Args:
        start_date (str): The start date in "dd/mm/yy" format.
        end_date (str): The end date in "dd/mm/yy" format.

    Returns:
        str: A randomly generated date in "dd/mm/yy" format.
    """
    start = datetime.strptime(start_date, "%d/%m/%y")
    end = datetime.strptime(end_date, "%d/%m/%y")
    random_date = start + timedelta(days=random.randint(0, (end - start).days))
    return random_date.strftime("%d/%m/%y")