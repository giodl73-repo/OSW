"""One exact inventory expectation migration; historical rows stay unchanged."""
import madagascar_dimensions_cases_v1 as base

query=base.query
COUNT=base.COUNT
main_cases=base.main_cases
verify=base.verify

def adapt_legacy_cases(cases):
    contract=query.build_contract()
    prior=contract['parent_collection_counts']['widths']
    after=contract['expected_totals']['widths']
    if prior!=176 or contract['new_width_records']!=1 or after!=177:
        raise ValueError('Exact one-width frozen contract required')
    result=[];changed=0
    for request,expected in cases:
        if request=={'collection':'widths','limit':1}:
            if type(expected) is not int or expected!=prior:raise ValueError('Exact historical176-width case required')
            expected=after;changed+=1
        result.append((request,expected))
    if changed!=1:raise ValueError('Exactly one historical width inventory case required')
    return result
