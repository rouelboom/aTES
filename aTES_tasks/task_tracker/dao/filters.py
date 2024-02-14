"""
Make smart filters
"""
from m7_aiohttp.exceptions import InvalidParams


def make_string_filter(field: 'Column', field_filter: dict) -> 'BinaryExpression':
    """
    Makes string filter for field, which can be used in query.where(...)

    Args:
        field: table field
        field_filter: dict with filter conditions

    Returns:
        field filter

    Raises:
        InvalidParams: if filter parameters incorrect

    """
    like = field_filter.get('like')
    ilike = field_filter.get('ilike')
    values = field_filter.get('values')

    count = 0
    for item in [like, ilike, values]:
        if item:
            count += 1

    if count == 0:
        raise InvalidParams('No "value", "like" or "ilike" for field {}'.format(field))

    if count > 1:
        raise InvalidParams('Should be just one condition "value", "like" or "ilike" for field {}'.format(field))

    if like:
        return field.like(like)
    if ilike:
        return field.ilike(ilike)

    return field.in_(values)
