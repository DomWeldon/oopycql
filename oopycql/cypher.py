from collections import namedtuple


class CypherReference(object):
    """Object to store cypher specific information"""

    PARAM_FINDING_REGEX = (
        '{ *([^\p{Sc}\p{S}][^\p{Sm}\p{So}\p{Sk}\p{C}\p{Z}\p{P}\p{M}]+) *}'
        '|\$([^\p{Sc}\p{S}][^\p{Sm}\p{So}\p{Sk}\p{C}\p{Z}\p{P}\p{M}]+)')
    """Regex to pull out specific """

    CypherClauseType = namedtuple('CypherClauseType', [
                                                        'keyword',
                                                        'operation_type',
                                                        'is_legacy',
                                                      ])

    CYPHER_CLAUSES = [
        # reading clauses
        CypherClauseType('MATCH', 'READING', False),
        CypherClauseType('OPTIONAL MATCH', 'READING', False),
        CypherClauseType('START', 'READING', True),
        # projecting clauses
        CypherClauseType('RETURN', 'PROJECTING', False),
        CypherClauseType('WITH', 'PROJECTING', False),
        CypherClauseType('UNWIND', 'PROJECTING', False),
        # reading sub clauses
        CypherClauseType('WHERE', 'READING_SUB', False),
        CypherClauseType('ORDER BY', 'READING_SUB', False),
        CypherClauseType('SKIP', 'READING_SUB', False),
        CypherClauseType('LIMIT', 'READING_SUB', False),
        # reading hint clauses
        CypherClauseType('USING INDEX', 'READING_HINT', False),
        CypherClauseType('USING SCAN', 'READING_HINT', False),
        CypherClauseType('USING JOIN', 'READING_HINT', False),
        # writing
        CypherClauseType('CREATE', 'WRITING', False),
        CypherClauseType('DELETE', 'WRITING', False),
        CypherClauseType('DETACH DELETE', 'WRITING', False),
        CypherClauseType('SET', 'WRITING', False),
        CypherClauseType('REMOVE`', 'WRITING', False),
        CypherClauseType('FOREACH', 'WRITING', False),
        # reading and writing
        CypherClauseType('MERGE', 'READING/WRITING', False),
        CypherClauseType('ON CREATE', 'READING/WRITING', False),
        CypherClauseType('ON MATCH', 'READING/WRITING', False),
        CypherClauseType('CALL', 'READING/WRITING', False),
        CypherClauseType('CREATE UNIQUE', 'READING/WRITING', False),
        # set operations
        CypherClauseType('UNION', 'SET', False),
        CypherClauseType('UNION ALL', 'SET', False),
        # importing
        CypherClauseType('LOAD CSV', 'IMPORTING', False),
        CypherClauseType('USING PERIODIC COMMIT', 'IMPORTING', False),
        # importing
        CypherClauseType('CREATE CONSTRAINT', 'SCHEMA', False),
        CypherClauseType('DROP CONSTRAINT', 'SCHEMA', False),
        CypherClauseType('CREATE INDEX', 'SCHEMA', False),
        CypherClauseType('DROP INDEX', 'SCHEMA', False),
    ]
