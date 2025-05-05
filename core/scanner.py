class ScanType:
    EXACT_VALUE = 'Exact value'
    BIGGER_THAN = 'Bigger than...'
    SMALLER_THAN = 'Smaller than...'
    BETWEEN = 'Between...'
    UNKNOWN = 'Unknown'
    INCREASED_VALUE = 'Increased value'
    INCREASED_BY = 'Increased by...'
    DECREASED_VALUE = 'Decreased value'
    DECREASED_BY = 'Decreased by...'
    CHANGED_VALUE = 'Changed value'
    UNCHANGED_VALUE = 'Unchanged value'
    IGNORE = 'Ignore'
    CONTAINS = 'Contains...'
    STARTS_WITH = 'Starts with...'
    ENDS_WITH = 'Ends with...'

    ALL = (
        EXACT_VALUE,
        BIGGER_THAN,
        SMALLER_THAN,
        BETWEEN,
        UNKNOWN,
        INCREASED_VALUE,
        INCREASED_BY,
        DECREASED_VALUE,
        DECREASED_BY,
        CHANGED_VALUE,
        UNCHANGED_VALUE,
        IGNORE,
        CONTAINS,
        STARTS_WITH,
        ENDS_WITH
    )


class ScanGroup:
    FIRST_SCAN = (
        ScanType.EXACT_VALUE,
        ScanType.BIGGER_THAN,
        ScanType.SMALLER_THAN,
        ScanType.BETWEEN,
        ScanType.UNKNOWN    
    )
    SUBSEQUENT_SCAN = (
        ScanType.EXACT_VALUE,
        ScanType.BIGGER_THAN,
        ScanType.SMALLER_THAN,
        ScanType.BETWEEN,
        ScanType.INCREASED_VALUE,
        ScanType.INCREASED_BY,
        ScanType.DECREASED_VALUE,
        ScanType.DECREASED_BY,
        ScanType.CHANGED_VALUE,
        ScanType.UNCHANGED_VALUE,
        ScanType.IGNORE
    )
    STR_FIRST_SCAN = (
        ScanType.EXACT_VALUE,
        ScanType.CONTAINS,
        ScanType.STARTS_WITH,
        ScanType.ENDS_WITH,
        ScanType.UNKNOWN
    )
    STR_SUBSEQUENT_SCAN = (
        ScanType.EXACT_VALUE,
        ScanType.CONTAINS,
        ScanType.STARTS_WITH,
        ScanType.ENDS_WITH,
        ScanType.CHANGED_VALUE,
        ScanType.UNCHANGED_VALUE,
        ScanType.IGNORE
    )


class ScanInputGroup:
    DUAL_INPUT = (ScanType.BETWEEN,)
    NO_INPUT = (
        ScanType.UNKNOWN,
        ScanType.INCREASED_VALUE,
        ScanType.DECREASED_VALUE,
        ScanType.CHANGED_VALUE,
        ScanType.UNCHANGED_VALUE,
        ScanType.IGNORE
    )


class ScanBy:
    VALUE = 'value'
    NAME = 'name'

    ALL = (
        VALUE,
        NAME
    )


class ValueType:
    INTEGER = 'Integer'
    FLOAT = 'Float'
    STRING = 'String'
    BOOL = 'Bool'

    ALL = (
        INTEGER,
        FLOAT,
        STRING,
        BOOL
    )
