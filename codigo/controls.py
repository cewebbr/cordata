#################
### Functions ###
#################

def status_selected(usecase: dict, status_filter: dict):
    """
    Return whether the usecase is selected by a filter, that is,
    whether its value for the possible statuses in listed in 
    the provided status filter.

    Parameters
    ----------
    usecase : dict
        One usecase, stored as a dict.
    status_filter : dict of lists
        Each key is a possible status type, and the associated
        value is a list of selected statuses for that type.
    
    Returns
    -------
    selected : bool
        Whether or not that usecase was selected by the filter.
    """
    # Return False if any status type is not selected:
    for status_type in status_filter.keys():
        if usecase[status_type] not in status_filter[status_type]:
            return False
    # Return True if all status types are selected:
    return True


################
### Controls ###
################